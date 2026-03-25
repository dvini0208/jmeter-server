from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "JMeter AI Platform")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./jmeter_ai.db")
    storage_root: str = os.getenv("STORAGE_ROOT", "./storage")
    jmeter_bin: str = os.getenv("APP_JMETER_CMD", "jmeter")
    max_threads: int = int(os.getenv("MAX_THREADS", "5000"))
    max_duration_seconds: int = int(os.getenv("MAX_DURATION_SECONDS", "86400"))

    grafana_enabled: bool = os.getenv("GRAFANA_ENABLED", "false").lower() == "true"
    grafana_base_url: str = os.getenv("GRAFANA_BASE_URL", "")
    grafana_dashboard_uid: str = os.getenv("GRAFANA_DASHBOARD_UID", "")
    grafana_dashboard_slug: str = os.getenv("GRAFANA_DASHBOARD_SLUG", "jmeter-live")
    grafana_datasource: str = os.getenv("GRAFANA_DATASOURCE", "")
    grafana_org_id: int = int(os.getenv("GRAFANA_ORG_ID", "1"))

    influx_enabled: bool = os.getenv("INFLUX_ENABLED", "false").lower() == "true"
    influx_host: str = os.getenv("INFLUX_HOST", "localhost")
    influx_port: int = int(os.getenv("INFLUX_PORT", "8086"))
    influx_database: str = os.getenv("INFLUX_DATABASE", "jmeter")
    influx_username: str = os.getenv("INFLUX_USERNAME", "")
    influx_password: str = os.getenv("INFLUX_PASSWORD", "")
    influx_metrics_application: str = os.getenv("INFLUX_METRICS_APPLICATION", "jmeter_ai")
    influx_summary_only: bool = os.getenv("INFLUX_SUMMARY_ONLY", "false").lower() == "true"


settings = Settings()