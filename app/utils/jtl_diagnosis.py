import csv
import xml.etree.ElementTree as ET
from pathlib import Path


def extract_jtl_diagnosis(jtl_path: str) -> dict:
    path = Path(jtl_path)

    if not jtl_path or not path.exists():
        return {
            "jtl_found": False,
            "diagnosis": "JTL file not found",
            "samples": [],
        }

    # Try CSV JTL first
    try:
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                failed_samples = []

                for row in reader:
                    success_value = str(row.get("success", "")).strip().lower()
                    if success_value in {"false", "0", "no"}:
                        failed_samples.append(
                            {
                                "label": row.get("label", ""),
                                "response_code": row.get("responseCode", ""),
                                "response_message": row.get("responseMessage", ""),
                                "thread_name": row.get("threadName", ""),
                            }
                        )

                if failed_samples:
                    first = failed_samples[0]
                    diagnosis = (
                        f"Failed sampler '{first['label']}' "
                        f"with response_code='{first['response_code']}' "
                        f"and response_message='{first['response_message']}'"
                    )
                    return {
                        "jtl_found": True,
                        "diagnosis": diagnosis,
                        "samples": failed_samples[:10],
                    }

                return {
                    "jtl_found": True,
                    "diagnosis": "No failed samples found in JTL",
                    "samples": [],
                }
    except Exception:
        pass

    # Try XML JTL
    try:
        tree = ET.parse(path)
        root = tree.getroot()

        failed_samples = []

        for elem in root:
            success_value = str(elem.attrib.get("s", "")).strip().lower()
            if success_value in {"false", "0"}:
                failed_samples.append(
                    {
                        "label": elem.attrib.get("lb", ""),
                        "response_code": elem.attrib.get("rc", ""),
                        "response_message": elem.attrib.get("rm", ""),
                        "thread_name": elem.attrib.get("tn", ""),
                    }
                )

        if failed_samples:
            first = failed_samples[0]
            diagnosis = (
                f"Failed sampler '{first['label']}' "
                f"with response_code='{first['response_code']}' "
                f"and response_message='{first['response_message']}'"
            )
            return {
                "jtl_found": True,
                "diagnosis": diagnosis,
                "samples": failed_samples[:10],
            }

        return {
            "jtl_found": True,
            "diagnosis": "No failed samples found in JTL",
            "samples": [],
        }

    except Exception:
        return {
            "jtl_found": True,
            "diagnosis": "Could not parse JTL for diagnosis",
            "samples": [],
        }