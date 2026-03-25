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
    """Compute detailed stats for a list of response time samples.
    Each sample is a dict with 'elapsed' (int ms), 'success' (bool),
    and 'timestamp' (int ms epoch).
    """
    if not samples:
        return {
            "count": 0, "error_count": 0, "error_pct": 0.0,
            "avg": 0.0, "min": 0, "max": 0,
            "median": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0,
            "throughput": 0.0,
        }

    # Filter out bogus JMeter values (Long.MAX_VALUE / Long.MIN_VALUE)
    # that appear for transactions with 0 actual executions
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


def _parse_csv_rows(path: Path) -> list:
    """Parse JTL CSV file and return list of sample dicts."""
    samples = []
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return samples
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

            samples.append({
                "label": label,
                "elapsed": elapsed,
                "timestamp": timestamp,
                "success": success,
            })
    return samples


def _parse_xml_rows(path: Path) -> list:
    """Parse JTL XML file and return list of sample dicts."""
    samples = []
    tree = ET.parse(str(path))
    root = tree.getroot()
    for elem in root:
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

        samples.append({
            "label": label,
            "elapsed": elapsed,
            "timestamp": timestamp,
            "success": success,
        })
    return samples


def parse_jtl_summary(jtl_path: str) -> dict:
    path = Path(jtl_path)

    if not path.exists():
        return {
            "exists": False,
            "total_samples": 0,
            "error_count": 0,
            "error_percentage": 0.0,
            "passed": False,
            "transactions": [],
        }

    # Try CSV first, then XML
    samples = []
    try:
        samples = _parse_csv_rows(path)
    except Exception:
        pass

    if not samples:
        try:
            samples = _parse_xml_rows(path)
        except Exception:
            return {
                "exists": True,
                "total_samples": 0,
                "error_count": 0,
                "error_percentage": 0.0,
                "passed": False,
                "transactions": [],
            }

    total = len(samples)
    errors = sum(1 for s in samples if not s["success"])
    error_pct = (errors / total * 100) if total else 0.0

    # Group by transaction label and compute per-transaction stats
    by_label = defaultdict(list)
    for s in samples:
        by_label[s["label"]].append(s)

    transactions = []
    for label in sorted(by_label.keys()):
        stats = _compute_transaction_stats(by_label[label])
        stats["label"] = label
        transactions.append(stats)

    # Also compute overall stats
    overall = _compute_transaction_stats(samples)

    return {
        "exists": True,
        "total_samples": total,
        "error_count": errors,
        "error_percentage": round(error_pct, 2),
        "passed": total > 0 and errors == 0,
        "overall": overall,
        "transactions": transactions,
    }