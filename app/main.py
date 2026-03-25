from fastapi import FastAPI
from app.config import settings
from app.db import Base, engine
from app.utils.storage import ensure_storage_dirs
from app.routers import scripts, scenarios, runs, agent, ui, files
import app.models
from pathlib import Path
from fastapi.staticfiles import StaticFiles

Base.metadata.create_all(bind=engine)
ensure_storage_dirs()

app = FastAPI(title=settings.app_name)

app.include_router(scripts.router)
app.include_router(scenarios.router)
app.include_router(runs.router)
app.include_router(agent.router)
app.include_router(ui.router)
app.include_router(files.router)

# Serve static files
storage_path = Path("storage")
storage_path.mkdir(parents=True, exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")

@app.get("/")
def root():
    return {"message": "JMeter AI Platform is running"}


@app.get("/health")
def health():
    return {"status": "ok"}