from pathlib import Path
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Scenario, TestRun, ScriptPackage
from app.utils.file_inspector import find_referenced_csvs, check_missing_dependencies


def create_run(db: Session, scenario_id: int) -> TestRun:
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    script_package = db.query(ScriptPackage).filter(
        ScriptPackage.id == scenario.script_package_id
    ).first()

    jmx_path = Path(script_package.extract_dir) / script_package.entry_jmx

    referenced_csvs = find_referenced_csvs(jmx_path)
    missing_dependencies = check_missing_dependencies(Path(script_package.extract_dir), referenced_csvs)

    if missing_dependencies:
        raise HTTPException(
            status_code=400,
            detail={"missing_dependencies": missing_dependencies}
        )

    run = TestRun(
        scenario_id=scenario_id,
        status="queued"
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    return run