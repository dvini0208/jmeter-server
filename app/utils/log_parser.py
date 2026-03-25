from pathlib import Path


def extract_log_diagnosis(log_path: str) -> dict:
    path = Path(log_path)

    if not log_path or not path.exists():
        return {
            "log_found": False,
            "diagnosis": "Log file not found",
            "matched_lines": [],
            "category": "log_missing",
        }

    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    strong_patterns = [
        ("unauthorized", ["401", "unauthorized"]),
        ("forbidden", ["403", "forbidden"]),
        ("not_found", ["404", "not found"]),
        ("server_error", ["500", "internal server error"]),
        ("assertion_failure", ["assertion failed"]),
        ("connection_refused", ["connection refused"]),
        ("timeout", ["sockettimeoutexception", "read timed out", "connect timed out", "timeout"]),
        ("dns_error", ["unknownhostexception"]),
        ("file_missing", ["filenotfoundexception", "no such file"]),
        ("non_http_response", ["non http response code", "non http response message"]),
        ("ssl_error", ["ssl", "pkix", "certificate"]),
    ]

    matched = []
    detected_category = None
    detected_line = None

    for line in lines:
        lower = line.lower()

        for category, patterns in strong_patterns:
            if any(pattern in lower for pattern in patterns):
                matched.append(line.strip())
                if detected_category is None:
                    detected_category = category
                    detected_line = line.strip()

    if detected_category:
        return {
            "log_found": True,
            "diagnosis": detected_line,
            "matched_lines": matched[-10:],
            "category": detected_category,
        }

    generic_keywords = [
        "error",
        "exception",
        "response code",
        "response message",
        "failed",
    ]

    for line in lines:
        lower = line.lower()
        if any(keyword in lower for keyword in generic_keywords):
            matched.append(line.strip())

    if matched:
        return {
            "log_found": True,
            "diagnosis": matched[-1],
            "matched_lines": matched[-10:],
            "category": "generic_error",
        }

    return {
        "log_found": True,
        "diagnosis": "No obvious failure pattern found in log",
        "matched_lines": [],
        "category": "unknown",
    }