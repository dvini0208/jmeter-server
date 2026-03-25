from app.config import settings


def build_jmeter_metrics_properties(run_id: int, scenario_id: int | None = None) -> dict[str, str]:
    return {
        "metrics_enabled": "true" if settings.influx_enabled else "false",
        "influx_host": settings.influx_host,
        "influx_port": str(settings.influx_port),
        "influx_database": settings.influx_database,
        "influx_username": settings.influx_username,
        "influx_password": settings.influx_password,
        "metrics_application": settings.influx_metrics_application,
        "metrics_run_id": str(run_id),
        "metrics_scenario_id": str(scenario_id) if scenario_id is not None else "",
        "metrics_summary_only": "true" if settings.influx_summary_only else "false",
    }