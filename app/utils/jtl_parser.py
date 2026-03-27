import csv
import math
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


def _percentile(sorted_values: list, pct: float) -> float:
    """Compute the pct-th percentile from a pre-sorted list."""
    if not sorted_values:
        return 0.0
    k = (len(sorted_values) - 1) * (pct / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(sorted_values[int(k)])
    return sorted_values[int(f)] * (c - k) + sorted_values[int(c)] * (k - f)


def _compute_transaction_stats(samples: list) -> dict:
    """Compute detailed stats for a list of response time samples."""
    if not samples:
        return {
            "count": 0, "error_count": 0, "error_pct": 0.0,
            "avg": 0.0, "min": 0, "max": 0,
            "median": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0,
            "throughput": 0.0,
        }

    # Filter out bogus JMeter values (Long.MAX_VALUE / Long.MIN_VALUE)
    MAX_REASONABLE_MS = 3_600_000  # 1 hour max response time
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


def _is_parent_sample(row: dict) -> bool:
    """Detect Transaction Controller parent (aggregate) samples."""
    # SampleCount > 1 means this is a parent/aggregate sample
    sample_count = row.get("SampleCount", "")
    if sample_count:
        try:
            if int(sample_count) > 1:
                return True
        except (ValueError, TypeError):
            pass

    # If URL column exists and is empty, it's likely a Transaction Controller
    url = row.get("URL", None)
    if url is not None and url.strip() == "":
        return True

    return False


def _parse_csv_rows(path: Path) -> tuple:
    """Parse JTL CSV file and return (sampler_samples, transaction_samples).
    Samplers = individual HTTP requests.
    Transactions = Transaction Controller parent/aggregate samples.
    """
    samplers = []
    transactions = []

    with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return samplers, transactions

        has_url_column = "URL" in reader.fieldnames
        has_sample_count = "SampleCount" in reader.fieldnames
        can_detect_parents = has_url_column or has_sample_count

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

            sample = {
                "label": label,
                "elapsed": elapsed,
                "timestamp": timestamp,
                "success": success,
            }

            if can_detect_parents and _is_parent_sample(row):
                transactions.append(sample)
            else:
                samplers.append(sample)

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
                    # Parent sample (Transaction Controller) - add to transactions
                    transactions.append(_extract_sample(elem))
                    # Recurse into children for individual samplers
                    _collect_samples(elem)
                else:
                    # Leaf sample (individual HTTP request)
                    samplers.append(_extract_sample(elem))

    _collect_samples(root)

    # Fallback: if no structured nesting, treat all as samplers
    if not samplers and not transactions:
        for elem in root:
            samplers.append(_extract_sample(elem))

    return samplers, transactions


def _build_grouped_stats(samples: list) -> list:
    """Group samples by label and compute per-label stats."""
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

    # Try CSV first, then XML
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

    # Use samplers for overall stats (individual request metrics)
    all_for_overall = sampler_samples if sampler_samples else transaction_samples
    total = len(all_for_overall)
    errors = sum(1 for s in all_for_overall if not s["success"])
    error_pct = (errors / total * 100) if total else 0.0

    # Build per-label stats for both categories
    sampler_stats = _build_grouped_stats(sampler_samples)
    transaction_stats = _build_grouped_stats(transaction_samples)

    # Overall stats from individual samplers
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
