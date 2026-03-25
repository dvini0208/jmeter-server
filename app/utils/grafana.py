from urllib.parse import urlencode

from app.config import settings


def build_grafana_run_url(run_id: int) -> str | None:
    if not settings.grafana_enabled:
        return None

    if not settings.grafana_base_url or not settings.grafana_dashboard_uid:
        return None

    base = settings.grafana_base_url.rstrip("/")
    path = f"/d/{settings.grafana_dashboard_uid}/{settings.grafana_dashboard_slug}"

    query = {
        "orgId": settings.grafana_org_id,
        "var-run_id": str(run_id),
        "from": "now-30m",
        "to": "now",
    }

    return f"{base}{path}?{urlencode(query)}"