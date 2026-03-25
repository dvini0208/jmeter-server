from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import ScenarioCreate
from app.services.scenario_service import (
    create_scenario,
    delete_scenario,
    get_scenario,
    list_scenarios,
)

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.post("")
def create_scenario_endpoint(payload: ScenarioCreate, db: Session = Depends(get_db)):
    scenario = create_scenario(db, payload)
    return {
        "id": scenario.id,
        "name": scenario.name,
        "script_package_id": scenario.script_package_id,
        "threads": scenario.threads,
        "ramp_up_seconds": scenario.ramp_up_seconds,
        "duration_seconds": scenario.duration_seconds,
        "ramp_down_seconds": scenario.ramp_down_seconds,
        "notes": scenario.notes,
        "thread_groups_json": scenario.thread_groups_json,
        "created_at": scenario.created_at,
    }


@router.get("")
def list_scenarios_endpoint(db: Session = Depends(get_db)):
    scenarios = list_scenarios(db)
    return [
        {
            "id": s.id,
            "name": s.name,
            "script_package_id": s.script_package_id,
            "threads": s.threads,
            "ramp_up_seconds": s.ramp_up_seconds,
            "duration_seconds": s.duration_seconds,
            "ramp_down_seconds": s.ramp_down_seconds,
            "notes": s.notes,
            "thread_groups_json": s.thread_groups_json,
            "created_at": s.created_at,
        }
        for s in scenarios
    ]


@router.get("/{scenario_id}")
def get_scenario_endpoint(scenario_id: int, db: Session = Depends(get_db)):
    scenario = get_scenario(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return {
        "id": scenario.id,
        "name": scenario.name,
        "script_package_id": scenario.script_package_id,
        "threads": scenario.threads,
        "ramp_up_seconds": scenario.ramp_up_seconds,
        "duration_seconds": scenario.duration_seconds,
        "ramp_down_seconds": scenario.ramp_down_seconds,
        "notes": scenario.notes,
        "thread_groups_json": scenario.thread_groups_json,
        "created_at": scenario.created_at,
    }


@router.delete("/{scenario_id}")
def delete_scenario_endpoint(scenario_id: int, db: Session = Depends(get_db)):
    deleted = delete_scenario(db, scenario_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return {"message": f"Scenario {scenario_id} deleted successfully"}