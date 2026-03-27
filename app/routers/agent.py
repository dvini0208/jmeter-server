from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db, SessionLocal
from app.models import ScriptPackage, Scenario, TestRun
from app.schemas import AgentCommandRequest
from app.services.agent_service import parse_agent_command
from app.services.run_service import create_run
from app.utils.jmeter_runner import execute_run
from app.utils.jtl_parser import parse_jtl_summary
from app.utils.log_parser import extract_log_diagnosis
from app.utils.jtl_diagnosis import extract_jtl_diagnosis
from app.utils.fix_suggester import suggest_fix_from_diagnosis
from app.utils.grafana import build_grafana_run_url

router = APIRouter(prefix="/agent", tags=["agent"])


def get_latest_script(db: Session):
    return db.query(ScriptPackage).order_by(ScriptPackage.uploaded_at.desc()).first()


def get_latest_scenario(db: Session):
    return db.query(Scenario).order_by(Scenario.created_at.desc()).first()


def get_latest_run(db: Session):
    return db.query(TestRun).order_by(TestRun.id.desc()).first()


def build_run_summary(run: TestRun):
    if not run.result_jtl_path:
        return {
            "run_id": run.id,
            "execution_status": run.status,
            "jtl_found": False,
            "total_samples": 0,
            "error_count": 0,
            "error_percentage": 0.0,
            "passed": False,
            "overall": None,
            "transactions": [],
        }

    summary = parse_jtl_summary(run.result_jtl_path)
    return {
        "run_id": run.id,
        "execution_status": run.status,
        "jtl_found": summary["exists"],
        "total_samples": summary["total_samples"],
        "error_count": summary["error_count"],
        "error_percentage": summary["error_percentage"],
        "passed": summary["passed"],
        "overall": summary.get("overall"),
        "transactions": summary.get("transactions", []),
        "samplers": summary.get("samplers", []),
    }


def build_run_artifacts(run: TestRun):
    grafana_url = build_grafana_run_url(run.id)

    
    return {
        "run_id": run.id,
        "execution_status": run.status,
        "run_dir": run.run_dir,
        "result_jtl_path": run.result_jtl_path,
        "log_path": run.log_path,
        "report_dir": run.report_dir,
        "grafana_url": grafana_url,
        "grafana_enabled": grafana_url is not None,
    }


def build_run_diagnosis(run: TestRun):
    log_diag = extract_log_diagnosis(run.log_path or "")
    jtl_diag = extract_jtl_diagnosis(run.result_jtl_path or "")

    diagnosis = jtl_diag["diagnosis"]
    source = "jtl"

    if not jtl_diag["jtl_found"] or diagnosis in {
        "JTL file not found",
        "Could not parse JTL for diagnosis",
        "No failed samples found in JTL",
    }:
        diagnosis = log_diag["diagnosis"]
        source = "log"

    return {
        "run_id": run.id,
        "execution_status": run.status,
        "error_message": run.error_message,
        "diagnosis_source": source,
        "diagnosis": diagnosis,
        "log_found": log_diag["log_found"],
        "log_category": log_diag["category"],
        "log_matches": log_diag["matched_lines"],
        "jtl_found": jtl_diag["jtl_found"],
        "failed_samples": jtl_diag["samples"],
    }


def build_fix_suggestion(run: TestRun):
    diagnosis_result = build_run_diagnosis(run)
    suggestion = suggest_fix_from_diagnosis(
        diagnosis_result["diagnosis"],
        diagnosis_result["failed_samples"],
    )

    return {
        "run_id": run.id,
        "execution_status": run.status,
        "diagnosis": diagnosis_result["diagnosis"],
        "category": suggestion["category"],
        "sampler": suggestion["sampler"],
        "response_code": suggestion["response_code"],
        "response_message": suggestion["response_message"],
        "suggestions": suggestion["suggestions"],
    }


@router.post("/command")
def agent_command(
    payload: AgentCommandRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    parsed = parse_agent_command(payload.command)
    intent = parsed["intent"]

    if intent == "latest_run_fix_suggestion":
        run = get_latest_run(db)
        if not run:
            raise HTTPException(status_code=404, detail="No runs found")
        return {"intent": intent, "result": build_fix_suggestion(run)}

    if intent == "run_fix_suggestion":
        run_id = parsed["run_id"]
        run = db.query(TestRun).filter(TestRun.id == run_id).first()
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        return {"intent": intent, "result": build_fix_suggestion(run)}

    if intent == "latest_run_diagnosis":
        run = get_latest_run(db)
        if not run:
            raise HTTPException(status_code=404, detail="No runs found")
        return {"intent": intent, "result": build_run_diagnosis(run)}

    if intent == "run_diagnosis":
        run_id = parsed["run_id"]
        run = db.query(TestRun).filter(TestRun.id == run_id).first()
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        return {"intent": intent, "result": build_run_diagnosis(run)}

    if intent == "list_scripts":
        scripts = db.query(ScriptPackage).all()
        result = [
            {
                "id": s.id,
                "name": s.name,
                "version": s.version,
                "entry_jmx": s.entry_jmx,
                "uploaded_at": s.uploaded_at,
            }
            for s in scripts
        ]
        return {"intent": intent, "result": result}

    if intent == "latest_script":
        script = get_latest_script(db)
        if not script:
            raise HTTPException(status_code=404, detail="No scripts found")

        return {
            "intent": intent,
            "result": {
                "id": script.id,
                "name": script.name,
                "version": script.version,
                "entry_jmx": script.entry_jmx,
                "uploaded_at": script.uploaded_at,
            },
        }

    if intent == "list_scenarios":
        scenarios = db.query(Scenario).all()
        result = [
            {
                "id": s.id,
                "name": s.name,
                "script_package_id": s.script_package_id,
                "threads": s.threads,
                "ramp_up_seconds": s.ramp_up_seconds,
                "duration_seconds": s.duration_seconds,
                "ramp_down_seconds": s.ramp_down_seconds,
                "created_at": s.created_at,
            }
            for s in scenarios
        ]
        return {"intent": intent, "result": result}

    if intent == "latest_scenario":
        scenario = get_latest_scenario(db)
        if not scenario:
            raise HTTPException(status_code=404, detail="No scenarios found")

        return {
            "intent": intent,
            "result": {
                "id": scenario.id,
                "name": scenario.name,
                "script_package_id": scenario.script_package_id,
                "threads": scenario.threads,
                "ramp_up_seconds": scenario.ramp_up_seconds,
                "duration_seconds": scenario.duration_seconds,
                "ramp_down_seconds": scenario.ramp_down_seconds,
                "created_at": scenario.created_at,
            },
        }

    if intent == "create_scenario_from_text":
        if not parsed.get("use_latest_script", False):
            raise HTTPException(
                status_code=400,
                detail="For now, scenario creation supports commands using 'latest script'",
            )

        latest_script = get_latest_script(db)
        if not latest_script:
            raise HTTPException(status_code=404, detail="No scripts found")

        scenario = Scenario(
            name=parsed["name"],
            script_package_id=latest_script.id,
            threads=parsed["threads"],
            ramp_up_seconds=parsed["ramp_up_seconds"],
            duration_seconds=parsed["duration_seconds"],
            ramp_down_seconds=parsed["ramp_down_seconds"],
            notes=parsed["notes"],
        )

        db.add(scenario)
        db.commit()
        db.refresh(scenario)

        return {
            "intent": intent,
            "result": {
                "message": "Scenario created successfully",
                "scenario_id": scenario.id,
                "name": scenario.name,
                "script_package_id": scenario.script_package_id,
                "threads": scenario.threads,
                "ramp_up_seconds": scenario.ramp_up_seconds,
                "duration_seconds": scenario.duration_seconds,
                "ramp_down_seconds": scenario.ramp_down_seconds,
                "notes": scenario.notes,
            },
        }

    if intent == "run_latest_script_from_text":
        latest_script = get_latest_script(db)
        if not latest_script:
            raise HTTPException(status_code=404, detail="No scripts found")

        scenario = Scenario(
            name=parsed["name"],
            script_package_id=latest_script.id,
            threads=parsed["threads"],
            ramp_up_seconds=parsed["ramp_up_seconds"],
            duration_seconds=parsed["duration_seconds"],
            ramp_down_seconds=parsed["ramp_down_seconds"],
            notes=parsed["notes"],
        )

        db.add(scenario)
        db.commit()
        db.refresh(scenario)

        run = create_run(db, scenario.id)

        def run_in_background(run_id: int):
            local_db = SessionLocal()
            try:
                execute_run(local_db, run_id)
            finally:
                local_db.close()

        background_tasks.add_task(run_in_background, run.id)

        return {
            "intent": intent,
            "result": {
                "message": "Scenario created and run started successfully",
                "script_package_id": latest_script.id,
                "scenario_id": scenario.id,
                "run_id": run.id,
                "status": run.status,
                "threads": scenario.threads,
                "ramp_up_seconds": scenario.ramp_up_seconds,
                "duration_seconds": scenario.duration_seconds,
                "ramp_down_seconds": scenario.ramp_down_seconds,
            },
        }

    if intent == "list_runs":
        runs = db.query(TestRun).all()
        result = [
            {
                "id": r.id,
                "scenario_id": r.scenario_id,
                "status": r.status,
                "started_at": r.started_at,
                "ended_at": r.ended_at,
                "exit_code": r.exit_code,
            }
            for r in runs
        ]
        return {"intent": intent, "result": result}

    if intent == "latest_run":
        run = get_latest_run(db)
        if not run:
            raise HTTPException(status_code=404, detail="No runs found")
        
        grafana_url = build_grafana_run_url(run.id)

        return {
            "intent": intent,
            "result": {
                "id": run.id,
                "scenario_id": run.scenario_id,
                "status": run.status,
                "started_at": run.started_at,
                "ended_at": run.ended_at,
                "exit_code": run.exit_code,
                "error_message": run.error_message,
                "grafana_url": grafana_url,
                "grafana_enabled": grafana_url is not None,
            },
        }

    if intent == "start_scenario":
        scenario_id = parsed["scenario_id"]
        run = create_run(db, scenario_id)

        def run_in_background(run_id: int):
            local_db = SessionLocal()
            try:
                execute_run(local_db, run_id)
            finally:
                local_db.close()

        background_tasks.add_task(run_in_background, run.id)

        return {
            "intent": intent,
            "result": {
                "message": f"Scenario {scenario_id} started",
                "run_id": run.id,
                "status": run.status,
            },
        }

    if intent == "start_latest_scenario":
        scenario = get_latest_scenario(db)
        if not scenario:
            raise HTTPException(status_code=404, detail="No scenarios found")

        run = create_run(db, scenario.id)

        def run_in_background(run_id: int):
            local_db = SessionLocal()
            try:
                execute_run(local_db, run_id)
            finally:
                local_db.close()

        background_tasks.add_task(run_in_background, run.id)

        return {
            "intent": intent,
            "result": {
                "message": f"Latest scenario {scenario.id} started",
                "scenario_id": scenario.id,
                "run_id": run.id,
                "status": run.status,
            },
        }

    if intent == "run_status":
        run_id = parsed["run_id"]
        run = db.query(TestRun).filter(TestRun.id == run_id).first()
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        
        grafana_url = build_grafana_run_url(run.id)

        return {
            "intent": intent,
            "result": {
                "run_id": run.id,
                "status": run.status,
                "started_at": run.started_at,
                "ended_at": run.ended_at,
                "exit_code": run.exit_code,
                "error_message": run.error_message,
                "grafana_url": grafana_url,
                "grafana_enabled": grafana_url is not None,
            },
        }

    if intent == "latest_run_status":
        run = get_latest_run(db)
        if not run:
            raise HTTPException(status_code=404, detail="No runs found")
        
        grafana_url = build_grafana_run_url(run.id)

        return {
            "intent": intent,
            "result": {
                "run_id": run.id,
                "status": run.status,
                "started_at": run.started_at,
                "ended_at": run.ended_at,
                "exit_code": run.exit_code,
                "error_message": run.error_message,
                "grafana_url": grafana_url,
                "grafana_enabled": grafana_url is not None,
            },
        }

    if intent == "run_summary":
        run_id = parsed["run_id"]
        run = db.query(TestRun).filter(TestRun.id == run_id).first()
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")

        return {"intent": intent, "result": build_run_summary(run)}

    if intent == "latest_run_summary":
        run = get_latest_run(db)
        if not run:
            raise HTTPException(status_code=404, detail="No runs found")

        return {"intent": intent, "result": build_run_summary(run)}

    if intent == "run_artifacts":
        run_id = parsed["run_id"]
        run = db.query(TestRun).filter(TestRun.id == run_id).first()
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")

        return {"intent": intent, "result": build_run_artifacts(run)}

    if intent == "latest_run_artifacts":
        run = get_latest_run(db)
        if not run:
            raise HTTPException(status_code=404, detail="No runs found")

        return {"intent": intent, "result": build_run_artifacts(run)}

    raise HTTPException(status_code=400, detail="Unknown agent intent")