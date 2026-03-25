from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ScriptPackage
from app.schemas import ScriptPackageOut, ScriptUploadResponse
from app.services.script_service import save_script_package

router = APIRouter(prefix="/scripts", tags=["scripts"])


@router.post("/upload", response_model=ScriptUploadResponse)
def upload_script_package(
    name: str = Form(...),
    version: str = Form("1.0"),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    result = save_script_package(db, files, name=name, version=version)

    return {
        "message": "Script package uploaded successfully",
        "script_package": result["script_package"],
    }


@router.get("", response_model=list[ScriptPackageOut])
def list_scripts(db: Session = Depends(get_db)):
    return db.query(ScriptPackage).order_by(ScriptPackage.uploaded_at.desc()).all()