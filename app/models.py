from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db import Base


class ScriptPackage(Base):
    __tablename__ = "script_packages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False, default="1.0")
    original_filename = Column(String, nullable=True)
    stored_path = Column(Text, nullable=True)
    extract_dir = Column(Text, nullable=True)
    entry_jmx = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    scenarios = relationship(
        "Scenario",
        back_populates="script_package",
        cascade="all, delete-orphan",
    )


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    script_package_id = Column(
        Integer,
        ForeignKey("script_packages.id"),
        nullable=False,
        index=True,
    )

    # Backward-compatible single TG fields
    threads = Column(Integer, nullable=False, default=1)
    ramp_up_seconds = Column(Integer, nullable=False, default=1)
    duration_seconds = Column(Integer, nullable=False, default=60)
    ramp_down_seconds = Column(Integer, nullable=False, default=1)

    notes = Column(Text, nullable=True)

    # New field for multi-thread-group scenario config
    # Example JSON:
    # [
    #   {
    #     "key": "tg1",
    #     "threads": 5,
    #     "ramp_up_seconds": 10,
    #     "duration_seconds": 60,
    #     "ramp_down_seconds": 5
    #   },
    #   {
    #     "key": "tg2",
    #     "threads": 2,
    #     "ramp_up_seconds": 5,
    #     "duration_seconds": 60,
    #     "ramp_down_seconds": 5
    #   }
    # ]
    thread_groups_json = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    script_package = relationship("ScriptPackage", back_populates="scenarios")
    runs = relationship(
        "TestRun",
        back_populates="scenario",
        cascade="all, delete-orphan",
    )


class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(
        Integer,
        ForeignKey("scenarios.id"),
        nullable=False,
        index=True,
    )

    status = Column(String, nullable=False, default="queued")
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)

    exit_code = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)

    run_dir = Column(Text, nullable=True)
    result_jtl_path = Column(Text, nullable=True)
    log_path = Column(Text, nullable=True)
    report_dir = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    scenario = relationship("Scenario", back_populates="runs")