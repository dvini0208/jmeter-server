from pathlib import Path
from uuid import uuid4
from app.config import settings


def ensure_storage_dirs() -> None:
    Path(settings.storage_root).mkdir(parents=True, exist_ok=True)
    Path(settings.storage_root, "scripts").mkdir(parents=True, exist_ok=True)
    Path(settings.storage_root, "runs").mkdir(parents=True, exist_ok=True)


def create_script_package_dir(name: str) -> Path:
    safe_name = name.replace(" ", "_")
    path = Path(settings.storage_root, "scripts", f"{safe_name}_{uuid4().hex[:8]}")
    path.mkdir(parents=True, exist_ok=True)
    return path


def create_run_dir(run_id: int) -> Path:
    path = Path(settings.storage_root, "runs", f"run_{run_id}")
    path.mkdir(parents=True, exist_ok=True)
    return path