from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AgentCommandRequest(BaseModel):
    command: str


class ThreadGroupConfig(BaseModel):
    key: str
    threads: int = 1
    ramp_up_seconds: int = 1
    duration_seconds: int = 60
    ramp_down_seconds: int = 1


class ScriptPackageBase(BaseModel):
    name: str
    version: str = "1.0"


class ScriptPackageCreate(ScriptPackageBase):
    pass


class ScriptPackageOut(BaseModel):
    id: int
    name: str
    version: str
    original_filename: Optional[str] = None
    stored_path: Optional[str] = None
    extract_dir: Optional[str] = None
    entry_jmx: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class ScriptUploadResponse(BaseModel):
    message: str
    script_package: ScriptPackageOut


class ScenarioCreate(BaseModel):
    name: str
    script_package_id: int
    notes: Optional[str] = None
    thread_groups: List[ThreadGroupConfig] = Field(
        default_factory=lambda: [
            ThreadGroupConfig(
                key="tg1",
                threads=1,
                ramp_up_seconds=1,
                duration_seconds=60,
                ramp_down_seconds=1,
            )
        ]
    )


class ScenarioOut(BaseModel):
    id: int
    name: str
    script_package_id: int
    threads: int
    ramp_up_seconds: int
    duration_seconds: int
    ramp_down_seconds: int
    notes: Optional[str] = None
    thread_groups_json: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TestRunOut(BaseModel):
    id: int
    scenario_id: int
    status: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    exit_code: Optional[int] = None
    error_message: Optional[str] = None
    run_dir: Optional[str] = None
    result_jtl_path: Optional[str] = None
    log_path: Optional[str] = None
    report_dir: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True