from pathlib import Path
from urllib.parse import unquote

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, PlainTextResponse, RedirectResponse

router = APIRouter(prefix="/files", tags=["files"])

STORAGE_ROOT = Path("./storage").resolve()


def safe_resolve_path(raw_path: str) -> Path:
    if not raw_path:
        raise HTTPException(status_code=400, detail="Path is required")

    decoded = unquote(raw_path).strip()
    candidate = Path(decoded)

    if candidate.is_absolute():
        file_path = candidate.resolve()
    else:
        file_path = (STORAGE_ROOT / candidate).resolve()   

    if STORAGE_ROOT not in file_path.parents and file_path != STORAGE_ROOT:
        raise HTTPException(
            status_code=403,
            detail="Access outside storage root is not allowed",
        )

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {file_path}",
        )

    return file_path


@router.get("/download")
def download_file(path: str = Query(...)):
    file_path = safe_resolve_path(path)

    if file_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail="Path points to a directory, not a file",
        )

    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/octet-stream",
    )


@router.get("/text")
def read_text_file(path: str = Query(...)):
    file_path = safe_resolve_path(path)

    if file_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail="Path points to a directory, not a text file",
        )

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not read file: {exc}",
        )

    return PlainTextResponse(content)


@router.get("/report/{run_id}")
def open_report(run_id: int):
    report_index = STORAGE_ROOT / "runs" / f"run_{run_id}" / "report" / "index.html"

    if not report_index.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Report index not found: {report_index}",
        )
    relative_path = report_index.relative_to(STORAGE_ROOT).as_posix()
    return RedirectResponse(url=f"/storage/{relative_path}")

    return FileResponse(
        path=str(report_index),
        filename="index.html",
        media_type="text/html",
    )