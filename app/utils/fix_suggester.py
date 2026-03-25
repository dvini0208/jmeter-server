def suggest_fix_from_diagnosis(diagnosis: str, failed_samples: list[dict]) -> dict:
    text = (diagnosis or "").lower()

    response_code = ""
    response_message = ""
    sampler = ""

    if failed_samples:
        first = failed_samples[0]
        response_code = str(first.get("response_code", "")).strip()
        response_message = str(first.get("response_message", "")).strip()
        sampler = str(first.get("label", "")).strip()

    suggestions = []
    category = "unknown"

    if response_code == "429" or "too many requests" in text:
        category = "rate_limit"
        suggestions = [
            "Reduce request rate or add pacing between requests.",
            "Check API quota, rate limits, and account usage limits.",
            "Use fewer users/threads or a longer ramp-up.",
            "Add timers in JMeter so requests are not sent too aggressively.",
        ]

    elif response_code == "401" or "unauthorized" in text:
        category = "authentication"
        suggestions = [
            "Check API key, token, or authentication header.",
            "Verify the token is valid and not expired.",
            "Make sure the Authorization header format is correct.",
        ]

    elif response_code == "403" or "forbidden" in text:
        category = "permission"
        suggestions = [
            "Check whether the account or API key has permission to access this resource.",
            "Verify model, endpoint, or environment access rules.",
            "Review account restrictions or policy blocks.",
        ]

    elif response_code == "404" or "not found" in text:
        category = "not_found"
        suggestions = [
            "Check the request URL, path, or endpoint name.",
            "Verify the target resource exists.",
            "Make sure the model or API route name is correct.",
        ]

    elif response_code == "500" or "internal server error" in text:
        category = "server_error"
        suggestions = [
            "Retry the request to confirm whether the error is temporary.",
            "Check server-side logs or backend health if you own the target service.",
            "Reduce load and see whether the issue appears only under stress.",
        ]

    elif "assertion" in text:
        category = "assertion_failure"
        suggestions = [
            "Check JMeter assertions and expected response content.",
            "Verify response body, response code, and headers match expectations.",
            "Open the JTL/report to see which assertion failed.",
        ]

    elif "timeout" in text:
        category = "timeout"
        suggestions = [
            "Increase timeout settings if appropriate.",
            "Check network latency and server responsiveness.",
            "Use fewer users first and see when timeouts begin.",
        ]

    elif "connection refused" in text:
        category = "connection_refused"
        suggestions = [
            "Check whether the target host and port are reachable.",
            "Verify the server is running and accepting connections.",
            "Check firewall, proxy, or network restrictions.",
        ]

    elif "ssl" in text or "certificate" in text or "pkix" in text:
        category = "ssl_error"
        suggestions = [
            "Check SSL/TLS certificate trust and hostname configuration.",
            "Verify whether the endpoint requires a client certificate.",
            "Confirm Java/JMeter truststore settings if HTTPS is involved.",
        ]

    else:
        suggestions = [
            "Open the latest JTL and jmeter.log for more detail.",
            "Check response code, response message, and sampler name.",
            "Retry with a smaller load and compare the result.",
        ]

    return {
        "category": category,
        "sampler": sampler,
        "response_code": response_code,
        "response_message": response_message,
        "suggestions": suggestions,
    }