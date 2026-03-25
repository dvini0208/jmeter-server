from pathlib import Path
from typing import Sequence
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models import ScriptPackage
from app.utils.file_inspector import find_referenced_csvs, check_missing_dependencies


ALLOWED_EXTENSIONS = {".jmx", ".csv", ".txt", ".json", ".xml", ".properties"}


def save_script_package(db: Session, files: Sequence[UploadFile], name: str, version: str = "1.0"):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    from app.utils.storage import create_script_package_dir

    package_dir = create_script_package_dir(name)
    entry_jmx = None

    for file in files:
        if not file.filename:
            continue

        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file: {file.filename}")

        dest = package_dir / Path(file.filename).name

        with dest.open("wb") as f:
            f.write(file.file.read())

        if ext == ".jmx" and entry_jmx is None:
            entry_jmx = dest.name

    if entry_jmx is None:
        raise HTTPException(status_code=400, detail="At least one .jmx file is required")

    script_package = ScriptPackage(
        name=name,
        version=version,
        original_filename=entry_jmx,
        stored_path=str(package_dir / entry_jmx),
        extract_dir=str(package_dir),
        entry_jmx=entry_jmx,
    )

    db.add(script_package)
    db.commit()
    db.refresh(script_package)

    referenced_csvs = find_referenced_csvs(package_dir / entry_jmx)
    missing_dependencies = check_missing_dependencies(package_dir, referenced_csvs)

    return {
        "script_package": script_package,
        "referenced_csvs": referenced_csvs,
        "missing_dependencies": missing_dependencies,
    }