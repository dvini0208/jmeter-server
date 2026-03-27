import json
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from app.config import settings
from app.models import TestRun, Scenario, ScriptPackage
from app.utils.storage import create_run_dir
from app.utils.jmeter_metrics import build_jmeter_metrics_properties


def _set_or_create_prop(parent: ET.Element, tag: str, name: str, value: str):
    """Set a property element's text, or create it if missing."""
    for elem in parent:
        if elem.tag == tag and elem.get("name") == name:
            elem.text = value
            return
    new_elem = ET.SubElement(parent, tag)
    new_elem.set("name", name)
    new_elem.text = value


def _modify_jmx_thread_groups(jmx_path: Path, scenario: Scenario) -> None:
    """
    Directly modify thread group settings in the JMX XML so JMeter
    uses the scenario's threads/ramp-up/duration regardless of what
    was originally configured in the test plan.
    """
    tree = ET.parse(str(jmx_path))
    root = tree.getroot()

    # Parse multi-thread-group config if available
    thread_group_configs = []
    if scenario.thread_groups_json:
        try:
            thread_group_configs = json.loads(scenario.thread_groups_json)
        except (json.JSONDecodeError, TypeError):
            pass

    # Default config from scenario's top-level fields
    default_config = {
        "threads": scenario.threads,
        "ramp_up_seconds": scenario.ramp_up_seconds,
        "duration_seconds": scenario.duration_seconds,
        "ramp_down_seconds": scenario.ramp_down_seconds,
    }

    # Find all thread group elements (ThreadGroup, SetupThreadGroup, etc.)
    thread_group_tags = {"ThreadGroup", "SetupThreadGroup", "PostThreadGroup",
                         "com.blazemeter.jmeter.threads.concurrency.ConcurrencyThreadGroup",
                         "com.blazemeter.jmeter.threads.arrivals.ArrivalsThreadGroup"}

    thread_groups = []
    for elem in root.iter():
        testclass = elem.get("testclass", "")
        if testclass in thread_group_tags or elem.tag in thread_group_tags:
            thread_groups.append(elem)

    for idx, tg in enumerate(thread_groups):
        # Pick config: use matching thread_group_configs entry or default
        if idx < len(thread_group_configs):
            cfg = thread_group_configs[idx]
        else:
            cfg = default_config

        threads = str(cfg.get("threads", default_config["threads"]))
        ramp_up = str(cfg.get("ramp_up_seconds", default_config["ramp_up_seconds"]))
        duration = str(cfg.get("duration_seconds", default_config["duration_seconds"]))

        testclass = tg.get("testclass", tg.tag)

        if testclass in ("com.blazemeter.jmeter.threads.concurrency.ConcurrencyThreadGroup",
                         "com.blazemeter.jmeter.threads.arrivals.ArrivalsThreadGroup"):
            # Blazemeter Concurrency/Arrivals Thread Group uses different property names
            _set_or_create_prop(tg, "stringProp", "TargetLevel", threads)
            _set_or_create_prop(tg, "stringProp", "RampUp", ramp_up)
            _set_or_create_prop(tg, "stringProp", "Hold", duration)
        else:
            # Standard JMeter ThreadGroup
            _set_or_create_prop(tg, "stringProp", "ThreadGroup.num_threads", threads)
            _set_or_create_prop(tg, "stringProp", "ThreadGroup.ramp_time", ramp_up)

            # Enable scheduler and set duration for duration-based execution
            _set_or_create_prop(tg, "boolProp", "ThreadGroup.scheduler", "true")
            _set_or_create_prop(tg, "stringProp", "ThreadGroup.duration", duration)
            _set_or_create_prop(tg, "stringProp", "ThreadGroup.delay", "")

            # Set loop count to -1 (forever) so duration controls test length
            for lc in tg.iter():
                if lc.get("testclass") == "LoopController" or lc.tag == "LoopController":
                    _set_or_create_prop(lc, "intProp", "LoopController.loops", "-1")
                    _set_or_create_prop(lc, "boolProp", "LoopController.continue_forever", "false")
                    break
            # Also handle LoopController inside elementProp
            for ep in tg.findall("elementProp"):
                if ep.get("name") == "ThreadGroup.main_controller":
                    _set_or_create_prop(ep, "intProp", "LoopController.loops", "-1")
                    _set_or_create_prop(ep, "boolProp", "LoopController.continue_forever", "false")

    tree.write(str(jmx_path), xml_declaration=True, encoding="utf-8")


def execute_run(db: Session, run_id: int) -> None:
    run = db.query(TestRun).filter(TestRun.id == run_id).first()
    if not run:
        return

    scenario = db.query(Scenario).filter(Scenario.id == run.scenario_id).first()
    if not scenario:
        run.status = "failed"
        run.ended_at = datetime.utcnow()
        run.error_message = "Scenario not found"
        db.commit()
        return
    metrics_props = build_jmeter_metrics_properties(
        run_id=run.id,
        scenario_id=run.scenario_id,
    )

    script_package = db.query(ScriptPackage).filter(
        ScriptPackage.id == scenario.script_package_id
    ).first()
    if not script_package:
        run.status = "failed"
        run.ended_at = datetime.utcnow()
        run.error_message = "Script package not found"
        db.commit()
        return

    run_dir = create_run_dir(run.id).resolve()
    workspace_dir = (run_dir / "workspace").resolve()
    report_dir = (run_dir / "report").resolve()

    workspace_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    source_dir = Path(script_package.extract_dir).resolve()

    for item in source_dir.iterdir():
        target = workspace_dir / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)

    # IMPORTANT: use only the file name here because cwd is workspace_dir
    jmx_file_name = script_package.entry_jmx

    # Modify the JMX thread groups directly so duration/threads/ramp-up
    # take effect regardless of what the original JMX had configured
    jmx_full_path = workspace_dir / jmx_file_name
    try:
        _modify_jmx_thread_groups(jmx_full_path, scenario)
    except Exception as exc:
        run.status = "failed"
        run.ended_at = datetime.utcnow()
        run.error_message = f"Failed to modify JMX thread groups: {exc}"
        db.commit()
        return

    # Use absolute paths for output files
    result_jtl = (run_dir / "results.jtl").resolve()
    log_path = (run_dir / "jmeter.log").resolve()

    # Write a custom properties file to ensure proper CSV output format
    # -J flags don't always work for jmeter.save.saveservice properties
    custom_props_path = (workspace_dir / "custom.properties").resolve()
    custom_props_path.write_text(
        "jmeter.save.saveservice.output_format=csv\n"
        "jmeter.save.saveservice.print_field_names=true\n"
        "jmeter.save.saveservice.url=true\n"
        "jmeter.save.saveservice.sample_count=true\n"
        "jmeter.save.saveservice.thread_counts=true\n"
        "jmeter.save.saveservice.connect_time=true\n"
        "jmeter.save.saveservice.latency=true\n"
        "jmeter.save.saveservice.bytes=true\n"
        "jmeter.save.saveservice.sent_bytes=true\n"
        "jmeter.save.saveservice.data_type=true\n"
        "jmeter.save.saveservice.label=true\n"
        "jmeter.save.saveservice.response_code=true\n"
        "jmeter.save.saveservice.response_message=true\n"
        "jmeter.save.saveservice.successful=true\n"
        "jmeter.save.saveservice.thread_name=true\n"
        "jmeter.save.saveservice.time=true\n"
        "jmeter.save.saveservice.timestamp_format=ms\n",
        encoding="utf-8",
    )

    base_cmd = [
        settings.jmeter_bin,
        "-n",
        "-t",
        jmx_file_name,
        "-l",
        str(result_jtl),
        "-j",
        str(log_path),
        "-e",
        "-o",
        str(report_dir),
        "-q",
        str(custom_props_path),
        f"-Jthreads={scenario.threads}",
        f"-Jramp_up={scenario.ramp_up_seconds}",
        f"-Jduration={scenario.duration_seconds}",
        f"-Jramp_down={scenario.ramp_down_seconds}",
    ]

    for key, value in metrics_props.items():
        base_cmd.append(f"-J{key}={value}")

    if settings.jmeter_bin.lower().endswith(".bat") or settings.jmeter_bin.lower().endswith(".cmd"):
        cmd = ["cmd", "/c"] + base_cmd
    else:
        cmd = base_cmd

    clean_env = os.environ.copy()
    clean_env.pop("JMETER_BIN", None)

    run.status = "running"
    run.started_at = datetime.utcnow()
    run.run_dir = str(run_dir)
    run.result_jtl_path = str(result_jtl)
    run.log_path = str(log_path)
    run.report_dir = str(report_dir)
    run.error_message = None
    db.commit()

    try:
        process = subprocess.Popen(
            cmd,
            cwd=str(workspace_dir),
            env=clean_env,
        )
        run.process_id = process.pid
        db.commit()

        exit_code = process.wait()
        run.exit_code = exit_code
        run.ended_at = datetime.utcnow()
        run.status = "completed" if exit_code == 0 else "failed"

        if exit_code != 0:
            run.error_message = f"JMeter exited with code {exit_code}"

        db.commit()

    except Exception as exc:
        run.status = "failed"
        run.ended_at = datetime.utcnow()
        run.error_message = str(exc)
        db.commit()