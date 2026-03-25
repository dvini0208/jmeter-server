from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db, SessionLocal
from app.models import TestRun
from app.schemas import TestRunOut
from app.services.run_service import create_run
from app.utils.jmeter_runner import execute_run
from app.utils.jtl_parser import parse_jtl_summary

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("/start/{scenario_id}", response_model=TestRunOut)
def start_run(scenario_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    run = create_run(db, scenario_id)

    def run_in_background(run_id: int):
        local_db = SessionLocal()
        try:
            execute_run(local_db, run_id)
        finally:
            local_db.close()

    background_tasks.add_task(run_in_background, run.id)
    return run


@router.get("", response_model=list[TestRunOut])
def list_runs(db: Session = Depends(get_db)):
    return db.query(TestRun).all()


@router.get("/{run_id}", response_model=TestRunOut)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(TestRun).filter(TestRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/{run_id}/status")
def get_run_status(run_id: int, db: Session = Depends(get_db)):
    run = db.query(TestRun).filter(TestRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return {
        "id": run.id,
        "status": run.status,
        "started_at": run.started_at,
        "ended_at": run.ended_at,
        "exit_code": run.exit_code,
        "error_message": run.error_message,
    }


@router.get("/{run_id}/summary")
def get_run_summary(run_id: int, db: Session = Depends(get_db)):
    run = db.query(TestRun).filter(TestRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    if not run.result_jtl_path:
        return {
            "run_id": run.id,
            "execution_status": run.status,
            "jtl_found": False,
            "total_samples": 0,
            "error_count": 0,
            "error_percentage": 0.0,
            "passed": False,
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
    }


@router.get("/{run_id}/artifacts")
def get_run_artifacts(run_id: int, db: Session = Depends(get_db)):
    run = db.query(TestRun).filter(TestRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return {
        "run_id": run.id,
        "execution_status": run.status,
        "run_dir": run.run_dir,
        "result_jtl_path": run.result_jtl_path,
        "log_path": run.log_path,
        "report_dir": run.report_dir,
    }