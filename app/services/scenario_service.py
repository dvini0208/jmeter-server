import json
from sqlalchemy.orm import Session

from app.models import Scenario
from app.schemas import ScenarioCreate


def create_scenario(db: Session, payload: ScenarioCreate) -> Scenario:
    first_tg = payload.thread_groups[0]

    scenario = Scenario(
        name=payload.name,
        script_package_id=payload.script_package_id,
        notes=payload.notes,
        threads=first_tg.threads,
        ramp_up_seconds=first_tg.ramp_up_seconds,
        duration_seconds=first_tg.duration_seconds,
        ramp_down_seconds=first_tg.ramp_down_seconds,
        thread_groups_json=json.dumps(
            [tg.model_dump() for tg in payload.thread_groups]
        ),
    )

    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return scenario


def list_scenarios(db: Session):
    return db.query(Scenario).order_by(Scenario.created_at.desc()).all()


def get_scenario(db: Session, scenario_id: int):
    return db.query(Scenario).filter(Scenario.id == scenario_id).first()


def delete_scenario(db: Session, scenario_id: int) -> bool:
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        return False

    db.delete(scenario)
    db.commit()
    return True