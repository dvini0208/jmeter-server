from pathlib import Path
from urllib.parse import unquote

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, RedirectResponse

from app.utils.jtl_parser import parse_jtl_summary

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


def _build_table_rows(stats_list: list) -> str:
    if not stats_list:
        return '<tr><td colspan="12" style="text-align:center;color:#64748b;">No data</td></tr>'
    rows = []
    for t in stats_list:
        rows.append(f"""<tr>
            <td>{t['label']}</td>
            <td>{t['count']}</td>
            <td>{t['error_count']}</td>
            <td>{t['error_pct']}%</td>
            <td>{t['avg']}</td>
            <td>{t['min']}</td>
            <td>{t['max']}</td>
            <td>{t['median']}</td>
            <td>{t['p90']}</td>
            <td>{t['p95']}</td>
            <td>{t['p99']}</td>
            <td>{t['throughput']}</td>
        </tr>""")
    return "\n".join(rows)


@router.get("/custom-report/{run_id}", response_class=HTMLResponse)
def custom_report(run_id: int):
    """Custom HTML report with Transaction Controllers and Samplers separated."""
    jtl_path = STORAGE_ROOT / "runs" / f"run_{run_id}" / "results.jtl"

    if not jtl_path.exists():
        raise HTTPException(status_code=404, detail=f"JTL file not found for run {run_id}")

    summary = parse_jtl_summary(str(jtl_path))

    if not summary["exists"]:
        raise HTTPException(status_code=404, detail="JTL file could not be parsed")

    overall = summary.get("overall", {})
    transactions = summary.get("transactions", [])
    samplers = summary.get("samplers", [])

    tc_rows = _build_table_rows(transactions)
    sampler_rows = _build_table_rows(samplers)

    table_header = """<tr>
        <th>Label</th><th>Samples</th><th>Errors</th><th>Error%</th>
        <th>Avg(ms)</th><th>Min(ms)</th><th>Max(ms)</th><th>Median</th>
        <th>P90</th><th>P95</th><th>P99</th><th>TPS</th>
    </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Test Report - Run #{run_id}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0; padding: 24px;
            font-family: Inter, Arial, sans-serif;
            background: #f6f8fc; color: #0f172a;
        }}
        .shell {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ font-size: 26px; font-weight: 800; margin: 0 0 8px; }}
        .subtitle {{ color: #64748b; font-size: 14px; margin-bottom: 24px; }}
        .card {{
            background: #fff; border-radius: 16px; padding: 24px;
            box-shadow: 0 4px 14px rgba(15,23,42,0.05);
            margin-bottom: 24px;
        }}
        .card-title {{
            font-size: 18px; font-weight: 700; margin: 0 0 4px;
        }}
        .card-desc {{
            color: #64748b; font-size: 13px; margin: 0 0 16px;
        }}
        .summary-grid {{
            display: grid; grid-template-columns: repeat(auto-fill, minmax(160px,1fr));
            gap: 12px; margin-bottom: 24px;
        }}
        .metric-card {{
            background: #f8fafc; border: 1px solid #e5ebf3; border-radius: 12px;
            padding: 14px; text-align: center;
        }}
        .metric-label {{ font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }}
        .metric-value {{ font-size: 22px; font-weight: 700; margin-top: 4px; }}
        table {{
            width: 100%; border-collapse: collapse; font-size: 13px;
        }}
        th {{
            background: #f1f5f9; padding: 10px 12px; text-align: left;
            font-weight: 600; font-size: 12px; color: #475569;
            border-bottom: 2px solid #e2e8f0;
        }}
        td {{
            padding: 9px 12px; border-bottom: 1px solid #f1f5f9;
        }}
        tr:hover td {{ background: #f8fafc; }}
        .table-wrap {{ overflow-x: auto; }}
        .badge {{
            display: inline-block; padding: 3px 10px; border-radius: 999px;
            font-size: 12px; font-weight: 600;
        }}
        .badge-pass {{ background: #dcfce7; color: #16a34a; }}
        .badge-fail {{ background: #fee2e2; color: #dc2626; }}
    </style>
</head>
<body>
<div class="shell">
    <h1>Test Report - Run #{run_id}</h1>
    <p class="subtitle">
        Total Samples: {summary['total_samples']} |
        Errors: {summary['error_count']} ({summary['error_percentage']}%) |
        Status: <span class="badge {'badge-pass' if summary['passed'] else 'badge-fail'}">
            {'PASSED' if summary['passed'] else 'FAILED'}</span>
    </p>

    <div class="card">
        <div class="card-title">Overall Summary</div>
        <div class="summary-grid">
            <div class="metric-card"><div class="metric-label">Avg</div><div class="metric-value">{overall.get('avg', 0)} ms</div></div>
            <div class="metric-card"><div class="metric-label">Min</div><div class="metric-value">{overall.get('min', 0)} ms</div></div>
            <div class="metric-card"><div class="metric-label">Max</div><div class="metric-value">{overall.get('max', 0)} ms</div></div>
            <div class="metric-card"><div class="metric-label">Median</div><div class="metric-value">{overall.get('median', 0)} ms</div></div>
            <div class="metric-card"><div class="metric-label">P90</div><div class="metric-value">{overall.get('p90', 0)} ms</div></div>
            <div class="metric-card"><div class="metric-label">P95</div><div class="metric-value">{overall.get('p95', 0)} ms</div></div>
            <div class="metric-card"><div class="metric-label">P99</div><div class="metric-value">{overall.get('p99', 0)} ms</div></div>
            <div class="metric-card"><div class="metric-label">Throughput</div><div class="metric-value">{overall.get('throughput', 0)} /s</div></div>
        </div>
    </div>

    <div class="card">
        <div class="card-title">Transaction Controllers</div>
        <p class="card-desc">Aggregated business flow times (total elapsed across all HTTP requests in each transaction)</p>
        <div class="table-wrap">
            <table>
                <thead>{table_header}</thead>
                <tbody>{tc_rows}</tbody>
            </table>
        </div>
    </div>

    <div class="card">
        <div class="card-title">Individual HTTP Samplers</div>
        <p class="card-desc">Individual HTTP request response times</p>
        <div class="table-wrap">
            <table>
                <thead>{table_header}</thead>
                <tbody>{sampler_rows}</tbody>
            </table>
        </div>
    </div>
</div>
</body>
</html>"""

    return HTMLResponse(content=html)