import csv
import math
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

# HTTP sampler labels typically start with an HTTP method or look like a URL path
_HTTP_METHOD_PATTERN = re.compile(
    r"^(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)\s", re.IGNORECASE
)
_URL_PATH_PATTERN = re.compile(r"^(https?://|/)")


def _percentile(sorted_values: list, pct: float) -> float:
    if not sorted_values:
        return 0.0
    k = (len(sorted_values) - 1) * (pct / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(sorted_values[int(k)])
    return sorted_values[int(f)] * (c - k) + sorted_values[int(c)] * (k - f)


def _compute_transaction_stats(samples: list) -> dict:
    if not samples:
        return {
            "count": 0, "error_count": 0, "error_pct": 0.0,
            "avg": 0.0, "min": 0, "max": 0,
            "median": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0,
            "throughput": 0.0,
        }

    MAX_REASONABLE_MS = 3_600_000
    valid_samples = [s for s in samples if 0 <= s["elapsed"] <= MAX_REASONABLE_MS]

    if not valid_samples:
        return {
            "count": 0, "error_count": 0, "error_pct": 0.0,
            "avg": 0.0, "min": 0, "max": 0,
            "median": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0,
            "throughput": 0.0,
        }

    elapsed_values = sorted(s["elapsed"] for s in valid_samples)
    error_count = sum(1 for s in valid_samples if not s["success"])
    count = len(valid_samples)

    timestamps = [s["timestamp"] for s in valid_samples]
    min_ts = min(timestamps)
    max_ts = max(timestamps)
    duration_sec = (max_ts - min_ts) / 1000.0 if max_ts > min_ts else 1.0

    return {
        "count": count,
        "error_count": error_count,
        "error_pct": round(error_count / count * 100, 2) if count else 0.0,
        "avg": round(sum(elapsed_values) / count, 2),
        "min": elapsed_values[0],
        "max": elapsed_values[-1],
        "median": round(_percentile(elapsed_values, 50), 2),
        "p90": round(_percentile(elapsed_values, 90), 2),
        "p95": round(_percentile(elapsed_values, 95), 2),
        "p99": round(_percentile(elapsed_values, 99), 2),
        "throughput": round(count / duration_sec, 2),
    }


def _is_parent_sample_by_columns(row: dict) -> bool:
    """Detect Transaction Controller parent samples using CSV columns."""
    sample_count = row.get("SampleCount", "")
    if sample_count:
        try:
            if int(sample_count) > 1:
                return True
        except (ValueError, TypeError):
            pass

    url = row.get("URL", None)
    if url is not None and url.strip() == "":
        return True

    return False


def _is_http_sampler_label(label: str) -> bool:
    """Check if a label looks like an HTTP sampler (starts with HTTP method or URL path)."""
    return bool(_HTTP_METHOD_PATTERN.match(label) or _URL_PATH_PATTERN.match(label))


def _classify_by_label(all_labels: set) -> set:
    """Classify Transaction Controller labels by checking which labels look like
    HTTP samplers vs custom Transaction Controller names.

    Transaction Controllers typically have custom names like:
      G10X_S01_WishingTree_Grant_A_Wish_T01_Launch
    HTTP Samplers typically have labels like:
      GET /prod/orders, POST /prod/users/login/otp, OPTIONS /prod/clients
    """
    tc_labels = set()

    has_http_labels = any(_is_http_sampler_label(l) for l in all_labels)

    if has_http_labels:
        # If we have HTTP-style labels, non-HTTP labels are likely TCs
        for label in all_labels:
            if not _is_http_sampler_label(label):
                tc_labels.add(label)
    else:
        # No HTTP-style labels: check prefix patterns as fallback
        label_list = sorted(all_labels)
        for label in label_list:
            for other in label_list:
                if other != label and (
                    other.startswith(label + "-")
                    or other.startswith(label + "_")
                    or other.startswith(label + " ")
                ):
                    tc_labels.add(label)
                    break

    return tc_labels


def _parse_csv_rows(path: Path) -> tuple:
    """Parse JTL CSV file and return (sampler_samples, transaction_samples)."""
    all_rows = []

    with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return [], []

        has_url_column = "URL" in reader.fieldnames
        has_sample_count = "SampleCount" in reader.fieldnames
        can_detect_by_columns = has_url_column or has_sample_count

        for row in reader:
            try:
                elapsed = int(row.get("elapsed", 0))
            except (ValueError, TypeError):
                elapsed = 0
            try:
                timestamp = int(row.get("timeStamp", 0))
            except (ValueError, TypeError):
                timestamp = 0

            success_value = str(row.get("success", "")).strip().lower()
            success = success_value not in {"false", "0", "no"}
            label = row.get("label", "Unknown")

            is_parent = False
            if can_detect_by_columns:
                is_parent = _is_parent_sample_by_columns(row)

            all_rows.append({
                "label": label,
                "elapsed": elapsed,
                "timestamp": timestamp,
                "success": success,
                "is_parent": is_parent,
            })

    # If we couldn't detect by columns, use label-based classification
    if not can_detect_by_columns and all_rows:
        all_labels = {r["label"] for r in all_rows}
        tc_labels = _classify_by_label(all_labels)
        if tc_labels:
            for r in all_rows:
                if r["label"] in tc_labels:
                    r["is_parent"] = True

    samplers = [r for r in all_rows if not r["is_parent"]]
    transactions = [r for r in all_rows if r["is_parent"]]

    return samplers, transactions


def _parse_xml_rows(path: Path) -> tuple:
    """Parse JTL XML file and return (sampler_samples, transaction_samples)."""
    samplers = []
    transactions = []

    tree = ET.parse(str(path))
    root = tree.getroot()

    def _extract_sample(elem):
        try:
            elapsed = int(elem.attrib.get("t", 0))
        except (ValueError, TypeError):
            elapsed = 0
        try:
            timestamp = int(elem.attrib.get("ts", 0))
        except (ValueError, TypeError):
            timestamp = 0

        success_value = str(elem.attrib.get("s", "")).strip().lower()
        success = success_value not in {"false", "0"}
        label = elem.attrib.get("lb", "Unknown")

        return {
            "label": label,
            "elapsed": elapsed,
            "timestamp": timestamp,
            "success": success,
        }

    def _collect_samples(parent):
        for elem in parent:
            if elem.tag in ("sample", "httpSample"):
                children = list(elem.findall("sample")) + list(elem.findall("httpSample"))
                if children:
                    transactions.append(_extract_sample(elem))
                    _collect_samples(elem)
                else:
                    samplers.append(_extract_sample(elem))

    _collect_samples(root)

    # Fallback: if no structured nesting, use label classification
    if not samplers and not transactions:
        flat = []
        for elem in root:
            flat.append(_extract_sample(elem))

        all_labels = {s["label"] for s in flat}
        tc_labels = _classify_by_label(all_labels)

        for s in flat:
            if s["label"] in tc_labels:
                transactions.append(s)
            else:
                samplers.append(s)

    return samplers, transactions


def _build_grouped_stats(samples: list) -> list:
    by_label = defaultdict(list)
    for s in samples:
        by_label[s["label"]].append(s)

    result = []
    for label in sorted(by_label.keys()):
        stats = _compute_transaction_stats(by_label[label])
        stats["label"] = label
        result.append(stats)
    return result


def parse_jtl_summary(jtl_path: str) -> dict:
    path = Path(jtl_path)

    empty_result = {
        "exists": False,
        "total_samples": 0,
        "error_count": 0,
        "error_percentage": 0.0,
        "passed": False,
        "transactions": [],
        "samplers": [],
    }

    if not path.exists():
        return empty_result

    sampler_samples = []
    transaction_samples = []

    try:
        sampler_samples, transaction_samples = _parse_csv_rows(path)
    except Exception:
        pass

    if not sampler_samples and not transaction_samples:
        try:
            sampler_samples, transaction_samples = _parse_xml_rows(path)
        except Exception:
            empty_result["exists"] = True
            return empty_result

    all_for_overall = sampler_samples if sampler_samples else transaction_samples
    total = len(all_for_overall)
    errors = sum(1 for s in all_for_overall if not s["success"])
    error_pct = (errors / total * 100) if total else 0.0

    sampler_stats = _build_grouped_stats(sampler_samples)
    transaction_stats = _build_grouped_stats(transaction_samples)
    overall = _compute_transaction_stats(all_for_overall)

    return {
        "exists": True,
        "total_samples": total,
        "error_count": errors,
        "error_percentage": round(error_pct, 2),
        "passed": total > 0 and errors == 0,
        "overall": overall,
        "transactions": transaction_stats,
        "samplers": sampler_stats,
    }
