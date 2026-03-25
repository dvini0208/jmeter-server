import re
from fastapi import HTTPException


def extract_timing_and_load(text: str):
    threads = 10
    ramp_up_seconds = 10
    duration_seconds = 60
    ramp_down_seconds = 5

    m = re.search(r"(\d+)\s+users?", text)
    if m:
        threads = int(m.group(1))

    m = re.search(r"for\s+(\d+)\s+(minutes?|mins?|min)\b", text)
    if m:
        duration_seconds = int(m.group(1)) * 60
    else:
        m = re.search(r"for\s+(\d+)\s+(seconds?|secs?|sec)\b", text)
        if m:
            duration_seconds = int(m.group(1))

    m = re.search(r"ramp[\s-]?up\s+(\d+)\s+(minutes?|mins?|min)\b", text)
    if m:
        ramp_up_seconds = int(m.group(1)) * 60
    else:
        m = re.search(r"ramp[\s-]?up\s+(\d+)\s+(seconds?|secs?|sec)\b", text)
        if m:
            ramp_up_seconds = int(m.group(1))

    m = re.search(r"ramp[\s-]?down\s+(\d+)\s+(minutes?|mins?|min)\b", text)
    if m:
        ramp_down_seconds = int(m.group(1)) * 60
    else:
        m = re.search(r"ramp[\s-]?down\s+(\d+)\s+(seconds?|secs?|sec)\b", text)
        if m:
            ramp_down_seconds = int(m.group(1))

    return threads, ramp_up_seconds, duration_seconds, ramp_down_seconds


def parse_agent_command(command: str) -> dict:
    original = command.strip()
    text = re.sub(r"\s+", " ", original.lower()).strip()

    if any(
        phrase in text
        for phrase in [
            "how to fix latest run failure",
            "how to fix latest run",
            "suggest fix for latest run",
            "fix latest run",
            "how do i fix latest run",
        ]
    ):
        return {"intent": "latest_run_fix_suggestion"}

    match = re.search(r"(how to fix|suggest fix for|fix).*(run)\s+(\d+)", text)
    if match:
        return {"intent": "run_fix_suggestion", "run_id": int(match.group(3))}

    if any(
        phrase in text
        for phrase in [
            "why did latest run fail",
            "diagnose latest run",
            "latest run failure",
            "latest run error",
            "why latest run failed",
        ]
    ):
        return {"intent": "latest_run_diagnosis"}

    match = re.search(r"(why did|diagnose|failure of|error in).*(run)\s+(\d+)", text)
    if match:
        return {
            "intent": "run_diagnosis",
            "run_id": int(match.group(3)),
        }

    if (
        "run latest script" in text
        or "execute latest script" in text
        or "start latest script" in text
        or "run newest script" in text
        or "run last script" in text
        or "run a quick test for latest script" in text
    ):
        threads, ramp_up_seconds, duration_seconds, ramp_down_seconds = extract_timing_and_load(text)

        name = "Generated Scenario"
        if "quick" in text:
            name = "Quick Scenario"
        elif "smoke" in text:
            name = "Smoke Scenario"
            if "users" not in text:
                threads = 5
            if "minute" not in text and "second" not in text:
                duration_seconds = 60
            ramp_up_seconds = 5
            ramp_down_seconds = 5

        return {
            "intent": "run_latest_script_from_text",
            "name": name,
            "threads": threads,
            "ramp_up_seconds": ramp_up_seconds,
            "duration_seconds": duration_seconds,
            "ramp_down_seconds": ramp_down_seconds,
            "notes": original,
        }

    if (
        "create scenario" in text
        or "make scenario" in text
        or "create a scenario" in text
        or "make a scenario" in text
        or "create a quick test" in text
        or "make a quick test" in text
        or "create smoke scenario" in text
        or "make smoke scenario" in text
    ):
        latest_script = (
            "latest script" in text
            or "newest script" in text
            or "last script" in text
        )

        threads, ramp_up_seconds, duration_seconds, ramp_down_seconds = extract_timing_and_load(text)

        name = "Generated Scenario"
        if "smoke" in text:
            name = "Smoke Scenario"
            if "users" not in text:
                threads = 5
            if "minute" not in text and "second" not in text:
                duration_seconds = 60
            ramp_up_seconds = 5
            ramp_down_seconds = 5
        elif "quick" in text:
            name = "Quick Scenario"

        return {
            "intent": "create_scenario_from_text",
            "use_latest_script": latest_script,
            "name": name,
            "threads": threads,
            "ramp_up_seconds": ramp_up_seconds,
            "duration_seconds": duration_seconds,
            "ramp_down_seconds": ramp_down_seconds,
            "notes": original,
        }

    if any(
        phrase in text
        for phrase in [
            "latest script",
            "newest script",
            "last script",
            "show latest script",
            "show newest script",
            "show last script",
        ]
    ):
        return {"intent": "latest_script"}

    if any(
        phrase in text
        for phrase in [
            "list scripts",
            "show scripts",
            "show my scripts",
            "list my scripts",
            "list all scripts",
            "what scripts do i have",
        ]
    ):
        return {"intent": "list_scripts"}

    if any(
        phrase in text
        for phrase in [
            "latest scenario",
            "newest scenario",
            "last scenario",
            "show latest scenario",
            "show newest scenario",
            "show last scenario",
        ]
    ):
        return {"intent": "latest_scenario"}

    if any(
        phrase in text
        for phrase in [
            "list scenarios",
            "show scenarios",
            "show my scenarios",
            "list all scenarios",
            "what scenarios do i have",
        ]
    ):
        return {"intent": "list_scenarios"}

    if text in {
        "latest run",
        "newest run",
        "last run",
        "show latest run",
        "show newest run",
        "show last run",
    }:
        return {"intent": "latest_run"}

    if any(
        phrase in text
        for phrase in [
            "list runs",
            "show runs",
            "show my runs",
            "list all runs",
            "what runs do i have",
        ]
    ):
        return {"intent": "list_runs"}

    if any(
        phrase in text
        for phrase in [
            "start latest scenario",
            "run latest scenario",
            "execute latest scenario",
            "start newest scenario",
            "run newest scenario",
            "start last scenario",
            "run last scenario",
        ]
    ):
        return {"intent": "start_latest_scenario"}

    match = re.search(r"(start|run|execute)\s+scenario\s+(\d+)", text)
    if match:
        return {"intent": "start_scenario", "scenario_id": int(match.group(2))}

    match = re.search(r"scenario\s+(\d+)", text)
    if text.startswith("start ") or text.startswith("run ") or text.startswith("execute "):
        if match:
            return {"intent": "start_scenario", "scenario_id": int(match.group(1))}

    if any(
        phrase in text
        for phrase in [
            "latest run status",
            "newest run status",
            "last run status",
            "show latest run status",
            "show newest run status",
            "show last run status",
            "status of latest run",
            "status of last run",
        ]
    ):
        return {"intent": "latest_run_status"}

    match = re.search(r"(status|show status|get status).*(run)\s+(\d+)", text)
    if match:
        return {"intent": "run_status", "run_id": int(match.group(3))}

    match = re.search(r"run\s+(\d+)", text)
    if any(word in text for word in ["status", "state"]):
        if match:
            return {"intent": "run_status", "run_id": int(match.group(1))}

    if any(
        phrase in text
        for phrase in [
            "latest run summary",
            "newest run summary",
            "last run summary",
            "summary of latest run",
            "summary of last run",
            "summarize latest run",
            "summarize last run",
            "latest run report",
        ]
    ):
        return {"intent": "latest_run_summary"}

    match = re.search(r"(summary|summarize|report).*(run)\s+(\d+)", text)
    if match:
        return {"intent": "run_summary", "run_id": int(match.group(3))}

    if "summary" in text or "summarize" in text or "report" in text:
        match = re.search(r"run\s+(\d+)", text)
        if match:
            return {"intent": "run_summary", "run_id": int(match.group(1))}

    if any(
        phrase in text
        for phrase in [
            "latest run artifacts",
            "newest run artifacts",
            "last run artifacts",
            "artifacts of latest run",
            "artifacts of last run",
            "latest run files",
            "last run files",
            "latest run paths",
        ]
    ):
        return {"intent": "latest_run_artifacts"}

    match = re.search(r"(artifacts|files|paths).*(run)\s+(\d+)", text)
    if match:
        return {"intent": "run_artifacts", "run_id": int(match.group(3))}

    if "artifacts" in text or "files" in text or "paths" in text:
        match = re.search(r"run\s+(\d+)", text)
        if match:
            return {"intent": "run_artifacts", "run_id": int(match.group(1))}

    raise HTTPException(
        status_code=400,
        detail=(
            "Unsupported command. Try examples like: "
            "'show latest script', 'run latest script with 20 users for 2 minutes', "
            "'show latest run status', 'show latest run summary', "
            "'why did latest run fail', 'how to fix latest run failure'"
        ),
    )