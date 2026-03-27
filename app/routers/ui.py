from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])


@router.get("/ui", response_class=HTMLResponse)
def ui_home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>JMeter AI Agent</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
        :root {
            --bg: #f6f8fc;
            --panel: #ffffff;
            --panel-soft: #fafcff;
            --line: #e5ebf3;
            --line-2: #d8e1ee;
            --text: #0f172a;
            --muted: #64748b;
            --primary: #2563eb;
            --primary-soft: #dbeafe;
            --success: #16a34a;
            --success-soft: #dcfce7;
            --danger: #dc2626;
            --danger-soft: #fee2e2;
            --warn: #d97706;
            --warn-soft: #fef3c7;
            --shadow-sm: 0 4px 14px rgba(15, 23, 42, 0.05);
            --shadow-md: 0 14px 34px rgba(15, 23, 42, 0.08);
            --radius-xl: 24px;
            --radius-lg: 18px;
            --radius-md: 14px;
        }

        * { box-sizing: border-box; }
        html { scroll-behavior: smooth; }

        body {
            margin: 0;
            font-family: Inter, Arial, sans-serif;
            background:
                radial-gradient(circle at top left, rgba(37,99,235,0.08), transparent 20%),
                var(--bg);
            color: var(--text);
        }

        a {
            color: inherit;
            text-decoration: none;
        }

        .shell {
            max-width: 1380px;
            margin: 0 auto;
            padding: 24px;
        }

        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .brand-title {
            margin: 0 0 4px 0;
            font-size: 30px;
            font-weight: 800;
            letter-spacing: -0.03em;
        }

        .brand-sub {
            margin: 0;
            color: var(--muted);
            font-size: 14px;
        }

        .live-chip {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 999px;
            box-shadow: var(--shadow-sm);
            font-size: 13px;
            white-space: nowrap;
        }

        .live-dot {
            width: 10px;
            height: 10px;
            border-radius: 999px;
            background: #94a3b8;
        }

        .dot-completed { background: var(--success); }
        .dot-failed { background: var(--danger); }
        .dot-running { background: var(--warn); }
        .dot-queued { background: var(--primary); }

        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1.2fr;
            gap: 18px;
            margin-bottom: 18px;
        }

        .card {
            background: var(--panel);
            border: 1px solid rgba(15,23,42,0.05);
            border-radius: var(--radius-xl);
            box-shadow: var(--shadow-md);
            padding: 20px;
        }

        .section-title {
            font-size: 12px;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 14px;
        }

        .card-title {
            margin: 0 0 6px 0;
            font-size: 22px;
            font-weight: 800;
            letter-spacing: -0.02em;
        }

        .card-sub {
            color: var(--muted);
            font-size: 14px;
            margin-bottom: 16px;
            line-height: 1.6;
        }

        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        .full {
            grid-column: 1 / -1;
        }

        .label {
            display: block;
            font-size: 12px;
            color: var(--muted);
            margin-bottom: 6px;
        }

        .input {
            width: 100%;
            padding: 13px 14px;
            border-radius: 13px;
            border: 1px solid var(--line-2);
            background: white;
            color: var(--text);
            font-size: 14px;
            outline: none;
        }

        .input::placeholder {
            color: #94a3b8;
        }

        .input:focus {
            border-color: rgba(37,99,235,0.45);
            box-shadow: 0 0 0 4px rgba(37,99,235,0.10);
        }

        .btn {
            border: none;
            border-radius: 12px;
            padding: 12px 16px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 700;
            transition: transform 0.15s ease;
        }

        .btn:hover {
            transform: translateY(-1px);
        }

        .btn:disabled {
            opacity: 0.55;
            cursor: not-allowed;
            transform: none;
        }

        .btn-primary {
            background: var(--primary);
            color: white;
            box-shadow: 0 10px 24px rgba(37,99,235,0.22);
        }

        .btn-secondary {
            background: white;
            color: var(--text);
            border: 1px solid var(--line);
        }

        .btn-soft {
            background: var(--panel-soft);
            color: var(--text);
            border: 1px solid var(--line);
        }

        .btn-small {
            padding: 8px 10px;
            font-size: 12px;
            border-radius: 10px;
        }

        .thread-group-box {
            margin-bottom: 14px;
            padding: 14px;
            border: 1px solid var(--line);
            border-radius: 14px;
            background: var(--panel-soft);
        }

        .thread-group-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            gap: 12px;
            flex-wrap: wrap;
        }

        .thread-group-title {
            font-weight: 800;
            font-size: 14px;
        }

        .runs-card {
            margin-bottom: 18px;
        }

        .runs-head {
            display: flex;
            justify-content: space-between;
            align-items: end;
            gap: 16px;
            margin-bottom: 14px;
            flex-wrap: wrap;
        }

        .runs-title {
            margin: 0 0 4px 0;
            font-size: 24px;
            font-weight: 800;
            letter-spacing: -0.02em;
        }

        .runs-sub {
            margin: 0;
            font-size: 14px;
            color: var(--muted);
        }

        .runs-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .table-wrap {
            overflow-x: auto;
            border: 1px solid var(--line);
            border-radius: 16px;
            background: white;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 1120px;
            font-size: 14px;
        }

        th, td {
            text-align: left;
            padding: 13px 14px;
            border-bottom: 1px solid var(--line);
            vertical-align: top;
        }

        th {
            background: #f8fafc;
            color: #334155;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        tbody tr:hover td {
            background: #fbfdff;
        }

        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
        }

        .badge-completed {
            background: var(--success-soft);
            color: var(--success);
        }

        .badge-failed {
            background: var(--danger-soft);
            color: var(--danger);
        }

        .badge-running {
            background: var(--warn-soft);
            color: var(--warn);
        }

        .badge-queued {
            background: var(--primary-soft);
            color: var(--primary);
        }

        .badge-unknown {
            background: #eef2f7;
            color: #475569;
        }

        .link-btn {
            color: var(--primary);
            font-weight: 700;
            cursor: pointer;
            font-size: 13px;
            margin-right: 10px;
            white-space: nowrap;
        }

        .link-btn.disabled {
            color: #94a3b8;
            cursor: default;
            pointer-events: none;
        }

        .details-card {
            margin-bottom: 18px;
        }

        .details-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }

        .subpanel {
            background: var(--panel-soft);
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 16px;
            min-height: 180px;
        }

        .sub-title {
            font-size: 12px;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 10px;
        }

        .metric-list {
            display: grid;
            gap: 10px;
        }

        .metric-row {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            padding-bottom: 8px;
            border-bottom: 1px dashed var(--line-2);
            font-size: 14px;
        }

        .metric-row:last-child {
            border-bottom: none;
            padding-bottom: 0;
        }

        .metric-key {
            color: var(--muted);
        }

        .metric-value {
            font-weight: 700;
            text-align: right;
            word-break: break-word;
        }

        .callout {
            font-size: 14px;
            line-height: 1.7;
            color: #334155;
            white-space: pre-wrap;
            word-break: break-word;
        }

        details {
            margin-bottom: 14px;
        }

        details summary {
            list-style: none;
            cursor: pointer;
            background: white;
            border: 1px solid var(--line);
            border-radius: 16px;
            box-shadow: var(--shadow-sm);
            padding: 16px 18px;
            font-weight: 700;
        }

        details summary::-webkit-details-marker {
            display: none;
        }

        .details-body {
            padding-top: 12px;
        }

        .history-list {
            display: grid;
            gap: 10px;
        }

        .history-item {
            padding: 14px;
            cursor: pointer;
            color: var(--text);
            background: var(--panel-soft);
            border: 1px solid var(--line);
            border-radius: 14px;
        }

        .history-item:hover {
            background: #eef5ff;
        }

        .structured-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 12px;
        }

        .structured-card {
            padding: 14px;
            background: var(--panel-soft);
            border: 1px solid var(--line);
            border-radius: 14px;
        }

        .structured-label {
            font-size: 12px;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 8px;
        }

        .structured-value {
            font-size: 16px;
            font-weight: 700;
            word-break: break-word;
        }

        .raw-box {
            background: #0f172a;
            color: #e5e7eb;
            border-radius: 16px;
            padding: 16px;
            min-height: 220px;
            white-space: pre-wrap;
            word-break: break-word;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.6;
        }

        .dock {
            position: fixed;
            left: 50%;
            bottom: 18px;
            transform: translateX(-50%);
            width: min(980px, calc(100vw - 24px));
            z-index: 50;
            background: rgba(255,255,255,0.88);
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 14px;
            backdrop-filter: blur(18px);
            box-shadow: 0 18px 44px rgba(15,23,42,0.14);
        }

        .dock-grid {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 12px;
            align-items: center;
        }

        .dock-left {
            min-width: 0;
        }

        .dock-input-row {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 10px;
            margin-bottom: 10px;
        }

        .dock-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .chip-btn {
            border: 1px solid var(--line);
            background: white;
            color: var(--text);
            border-radius: 999px;
            padding: 8px 12px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
        }

        .dock-right {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            justify-content: flex-end;
        }

        .status-line {
            margin-top: 8px;
            color: var(--muted);
            font-size: 13px;
        }

        @media (max-width: 1080px) {
            .main-grid,
            .details-grid {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 900px) {
            .dock-grid,
            .dock-input-row {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 640px) {
            .shell {
                padding: 16px 16px 130px;
            }

            .topbar {
                flex-direction: column;
                align-items: stretch;
            }

            .runs-actions,
            .dock-chips,
            .dock-right {
                flex-direction: column;
            }

            .btn,
            .chip-btn {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="shell">
        <div class="topbar">
            <div>
                <h1 class="brand-title">JMeter AI Agent</h1>
                <p class="brand-sub">Upload one JMX, configure one or more thread groups in the scenario, run tests, and inspect reports.</p>
            </div>

            <div class="live-chip">
                <span id="liveDot" class="live-dot"></span>
                <span id="liveStatusText">Waiting for latest run data</span>
            </div>
        </div>

        <section class="main-grid">
            <div class="card">
                <div class="section-title">Upload Script</div>
                <h2 class="card-title">Add test package</h2>
                <div class="card-sub">Upload your JMX and supporting files.</div>

                <div class="form-grid">
                    <div>
                        <label class="label">Package Name</label>
                        <input class="input" id="uploadName" type="text" placeholder="Example: Login Test" />
                    </div>
                    <div>
                        <label class="label">Version</label>
                        <input class="input" id="uploadVersion" type="text" value="1.0" />
                    </div>
                    <div class="full">
                        <label class="label">Select Files</label>
                        <input class="input" id="uploadFiles" type="file" multiple />
                    </div>
                    <div class="full">
                        <button class="btn btn-primary" onclick="uploadPackage()">Upload Package</button>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="section-title">Create Scenario</div>
                <h2 class="card-title">Configure thread groups</h2>
                <div class="card-sub">TG1 is available by default. Add or delete more thread groups based on your JMX test plan.</div>

                <div class="form-grid">
                    <div>
                        <label class="label">Scenario Name</label>
                        <input class="input" id="scenarioName" type="text" placeholder="Smoke Test" />
                    </div>
                    <div>
                        <label class="label">Script Package ID</label>
                        <input class="input" id="scenarioScriptId" type="number" placeholder="1" />
                    </div>

                    <div class="full">
                        <label class="label">Notes</label>
                        <input class="input" id="scenarioNotes" type="text" placeholder="Optional notes" />
                    </div>

                    <div class="full">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; gap:12px; flex-wrap:wrap;">
                            <label class="label" style="margin-bottom:0;">Thread Groups</label>
                            <button class="btn btn-secondary btn-small" type="button" onclick="addThreadGroup()">+ Add Thread Group</button>
                        </div>

                        <div id="threadGroupsContainer"></div>
                    </div>

                    <div class="full">
                        <button class="btn btn-primary" onclick="createScenario()">Create Scenario</button>
                    </div>
                </div>
            </div>
        </section>

        <section class="card runs-card" style="margin-bottom:18px;">
            <div class="runs-head">
                <div>
                    <div class="section-title">Uploaded Scripts</div>
                    <h2 class="runs-title">Script packages</h2>
                    <p class="runs-sub">Use a script to auto-fill the scenario form.</p>
                </div>
                <div class="runs-actions">
                    <button class="btn btn-secondary" onclick="refreshAllData()">Refresh Scripts</button>
                </div>
            </div>

            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Version</th>
                            <th>Entry JMX</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="scriptsTableBody">
                        <tr><td colspan="5">No scripts yet.</td></tr>
                    </tbody>
                </table>
            </div>
        </section>

        <section class="card runs-card">
            <div class="runs-head">
                <div>
                    <div class="section-title">Scenarios</div>
                    <h2 class="runs-title">Scenario library</h2>
                    <p class="runs-sub">Each scenario can store multiple thread groups for one uploaded JMX.</p>
                </div>
                <div class="runs-actions">
                    <button class="btn btn-secondary" onclick="refreshAllData()">Refresh Scenarios</button>
                </div>
            </div>

            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Script</th>
                            <th>Thread Groups</th>
                            <th>TG Summary</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="scenariosTableBody">
                        <tr><td colspan="6">No scenarios yet.</td></tr>
                    </tbody>
                </table>
            </div>
        </section>

        <section class="card runs-card">
            <div class="runs-head">
                <div>
                    <div class="section-title">Recent Runs</div>
                    <h2 class="runs-title">Run history</h2>
                    <p class="runs-sub">Artifacts and Grafana are attached to each run row.</p>
                </div>
                <div class="runs-actions">
                    <button class="btn btn-secondary" onclick="refreshDashboard()">Refresh Runs</button>
                    <button class="btn btn-secondary" onclick="scrollToSection('consoleSection')">Open Console</button>
                </div>
            </div>

            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Run ID</th>
                            <th>Scenario</th>
                            <th>Status</th>
                            <th>Exit</th>
                            <th>Started</th>
                            <th>Ended</th>
                            <th>Artifacts</th>
                            <th>Actions</th>
                            <th>Live</th>
                        </tr>
                    </thead>
                    <tbody id="runsTableBody">
                        <tr><td colspan="9">No runs yet.</td></tr>
                    </tbody>
                </table>
            </div>
        </section>

        <section class="card details-card">
            <div class="section-title">Selected Run</div>
            <h2 class="runs-title" style="margin-bottom:4px;">Run details</h2>
            <p class="runs-sub" style="margin-bottom:16px;">Status, summary, diagnosis and fix suggestions appear here when you open a run.</p>

            <div class="details-grid">
                <div class="subpanel">
                    <div class="sub-title">Summary</div>
                    <div class="metric-list" id="latestSummaryPanel">No data</div>
                </div>

                <div class="subpanel">
                    <div class="sub-title">Status</div>
                    <div class="metric-list" id="latestStatusPanel">No data</div>
                </div>

                <div class="subpanel">
                    <div class="sub-title">Diagnosis</div>
                    <div class="callout" id="latestFailureReason">No diagnosis yet.</div>
                </div>

                <div class="subpanel">
                    <div class="sub-title">Fix Suggestion</div>
                    <div class="callout" id="latestFixReason">No fix suggestion yet.</div>
                </div>
            </div>

            <div style="margin-top:20px;">
                <div class="sub-title">Transaction Controllers</div>
                <p style="margin:4px 0 10px;color:var(--muted);font-size:13px;">Aggregated transaction times (total elapsed per transaction flow)</p>
                <div class="table-wrap">
                    <table>
                        <thead>
                            <tr>
                                <th>Transaction</th>
                                <th>Samples</th>
                                <th>Errors</th>
                                <th>Error%</th>
                                <th>Avg(ms)</th>
                                <th>Min(ms)</th>
                                <th>Max(ms)</th>
                                <th>Median</th>
                                <th>P90</th>
                                <th>P95</th>
                                <th>P99</th>
                                <th>TPS</th>
                            </tr>
                        </thead>
                        <tbody id="transactionMetricsBody">
                            <tr><td colspan="12">No transaction data yet.</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div style="margin-top:20px;">
                <div class="sub-title">Individual Samplers</div>
                <p style="margin:4px 0 10px;color:var(--muted);font-size:13px;">Individual HTTP request metrics</p>
                <div class="table-wrap">
                    <table>
                        <thead>
                            <tr>
                                <th>Sampler</th>
                                <th>Samples</th>
                                <th>Errors</th>
                                <th>Error%</th>
                                <th>Avg(ms)</th>
                                <th>Min(ms)</th>
                                <th>Max(ms)</th>
                                <th>Median</th>
                                <th>P90</th>
                                <th>P95</th>
                                <th>P99</th>
                                <th>TPS</th>
                            </tr>
                        </thead>
                        <tbody id="samplerMetricsBody">
                            <tr><td colspan="12">No sampler data yet.</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <section id="consoleSection">
            <details>
                <summary>Bottom Console</summary>
                <div class="details-body">
                    <div class="card" style="margin-bottom:14px;">
                        <div class="section-title">Command History</div>
                        <div class="history-list" id="historyList"></div>
                    </div>

                    <div class="card" style="margin-bottom:14px;">
                        <div class="section-title">Structured Response</div>
                        <div id="resultCards" class="structured-grid"></div>
                    </div>

                    <div class="card">
                        <div class="section-title">Raw JSON</div>
                        <div id="output" class="raw-box">No response yet.</div>
                    </div>
                </div>
            </details>
        </section>
    </div>

    <div class="dock">
        <div class="dock-grid">
            <div class="dock-left">
                <div class="dock-input-row">
                    <input class="input" id="commandInput" type="text" placeholder="Type a command like: run latest script with 20 users for 2 mins" />
                    <button class="btn btn-primary" onclick="sendCommand()">Send</button>
                </div>

                <div class="dock-chips">
                    <button class="chip-btn" onclick="fillCommand('show latest run status')">Latest Status</button>
                    <button class="chip-btn" onclick="fillCommand('show latest run summary')">Latest Summary</button>
                    <button class="chip-btn" onclick="fillCommand('why did latest run fail')">Diagnose</button>
                    <button class="chip-btn" onclick="fillCommand('how to fix latest run failure')">Fix</button>
                    <button class="chip-btn" onclick="fillCommand('show latest run artifacts')">Artifacts</button>
                </div>

                <div class="status-line" id="statusText">Ready.</div>
            </div>

            <div class="dock-right">
                <button class="btn btn-secondary" onclick="refreshAllData()">Refresh</button>
            </div>
        </div>
    </div>

    <script>
        let historyItems = [];
        let latestArtifactsByRun = {};

        let scenarioThreadGroups = [
            {
                key: "tg1",
                threads: 1,
                ramp_up_seconds: 1,
                duration_seconds: 60,
                ramp_down_seconds: 1
            }
        ];

        function scrollToSection(id) {
            const el = document.getElementById(id);
            if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
        }

        function escapeHtml(value) {
            return String(value ?? "")
                .replaceAll("&", "&amp;")
                .replaceAll("<", "&lt;")
                .replaceAll(">", "&gt;")
                .replaceAll('"', "&quot;")
                .replaceAll("'", "&#39;");
        }

        function fillCommand(text) {
            document.getElementById("commandInput").value = text;
        }

        function addHistory(command) {
            historyItems.unshift(command);
            historyItems = [...new Set(historyItems)].slice(0, 20);

            const historyList = document.getElementById("historyList");
            historyList.innerHTML = "";

            historyItems.forEach(item => {
                const div = document.createElement("div");
                div.className = "history-item";
                div.textContent = item;
                div.onclick = () => fillCommand(item);
                historyList.appendChild(div);
            });
        }

        function setStatus(text) {
            document.getElementById("statusText").textContent = text;
        }

        function statusBadge(status) {
            const s = String(status || "").toLowerCase();
            if (s === "completed") return '<span class="badge badge-completed">completed</span>';
            if (s === "failed") return '<span class="badge badge-failed">failed</span>';
            if (s === "running") return '<span class="badge badge-running">running</span>';
            if (s === "queued") return '<span class="badge badge-queued">queued</span>';
            return '<span class="badge badge-unknown">' + escapeHtml(status || "unknown") + '</span>';
        }

        function setLiveChip(status) {
            const dot = document.getElementById("liveDot");
            const text = document.getElementById("liveStatusText");
            dot.className = "live-dot";

            const s = String(status || "").toLowerCase();
            if (s === "completed") dot.classList.add("dot-completed");
            else if (s === "failed") dot.classList.add("dot-failed");
            else if (s === "running") dot.classList.add("dot-running");
            else if (s === "queued") dot.classList.add("dot-queued");

            text.textContent = status ? `Latest run is ${status}` : "Waiting for latest run data";
        }

        function metricRow(label, value) {
            return `
                <div class="metric-row">
                    <div class="metric-key">${escapeHtml(label)}</div>
                    <div class="metric-value">${escapeHtml(value ?? "-")}</div>
                </div>
            `;
        }

        function renderCards(data) {
            const container = document.getElementById("resultCards");
            container.innerHTML = "";
            if (!data || typeof data !== "object") return;

            const result = data.result || data;
            const fields = [
                ["intent", data.intent],
                ["run_id", result.run_id],
                ["scenario_id", result.scenario_id],
                ["script_package_id", result.script_package_id],
                ["status", result.status],
                ["execution_status", result.execution_status],
                ["category", result.category],
                ["response_code", result.response_code],
                ["response_message", result.response_message],
                ["sampler", result.sampler],
                ["threads", result.threads],
                ["duration_seconds", result.duration_seconds],
                ["error_count", result.error_count],
                ["error_percentage", result.error_percentage],
                ["passed", result.passed]
            ];

            fields.forEach(([label, value]) => {
                if (value !== undefined && value !== null && value !== "") {
                    const div = document.createElement("div");
                    div.className = "structured-card";
                    div.innerHTML = `
                        <div class="structured-label">${escapeHtml(String(label).replaceAll("_", " "))}</div>
                        <div class="structured-value">${escapeHtml(value)}</div>
                    `;
                    container.appendChild(div);
                }
            });

            if (Array.isArray(result.suggestions) && result.suggestions.length) {
                const div = document.createElement("div");
                div.className = "structured-card";
                div.style.gridColumn = "1 / -1";
                div.innerHTML = `
                    <div class="structured-label">suggestions</div>
                    <div>${result.suggestions.map(x => `<div style="margin-bottom:6px;">• ${escapeHtml(x)}</div>`).join("")}</div>
                `;
                container.appendChild(div);
            }
        }

        function safeJsonParse(value, fallback = null) {
            try {
                return JSON.parse(value);
            } catch {
                return fallback;
            }
        }

        function renderThreadGroups() {
            const container = document.getElementById("threadGroupsContainer");
            if (!container) return;

            container.innerHTML = "";

            scenarioThreadGroups.forEach((tg, index) => {
                const tgNumber = index + 1;
                const canDelete = scenarioThreadGroups.length > 1;

                const block = document.createElement("div");
                block.className = "thread-group-box";

                block.innerHTML = `
                    <div class="thread-group-head">
                        <div class="thread-group-title">TG${tgNumber}</div>
                        <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                            <input
                                class="input"
                                type="text"
                                value="${escapeHtml(tg.key)}"
                                onchange="updateThreadGroupKey(${index}, this.value)"
                                placeholder="tg${tgNumber}"
                                style="max-width:140px;"
                            />
                            <button
                                class="btn btn-secondary btn-small"
                                type="button"
                                onclick="removeThreadGroup(${index})"
                                ${canDelete ? "" : "disabled"}
                            >
                                Delete
                            </button>
                        </div>
                    </div>

                    <div class="form-grid">
                        <div>
                            <label class="label">Threads</label>
                            <input class="input" type="number" min="1" value="${tg.threads}" onchange="updateThreadGroupField(${index}, 'threads', this.value)" />
                        </div>
                        <div>
                            <label class="label">Ramp Up Seconds</label>
                            <input class="input" type="number" min="1" value="${tg.ramp_up_seconds}" onchange="updateThreadGroupField(${index}, 'ramp_up_seconds', this.value)" />
                        </div>
                        <div>
                            <label class="label">Duration Seconds</label>
                            <input class="input" type="number" min="1" value="${tg.duration_seconds}" onchange="updateThreadGroupField(${index}, 'duration_seconds', this.value)" />
                        </div>
                        <div>
                            <label class="label">Ramp Down Seconds</label>
                            <input class="input" type="number" min="1" value="${tg.ramp_down_seconds}" onchange="updateThreadGroupField(${index}, 'ramp_down_seconds', this.value)" />
                        </div>
                    </div>
                `;

                container.appendChild(block);
            });
        }

        function addThreadGroup() {
            const nextNumber = scenarioThreadGroups.length + 1;
            scenarioThreadGroups.push({
                key: `tg${nextNumber}`,
                threads: 1,
                ramp_up_seconds: 1,
                duration_seconds: 60,
                ramp_down_seconds: 1
            });
            renderThreadGroups();
        }

        function removeThreadGroup(index) {
            if (scenarioThreadGroups.length <= 1) return;
            scenarioThreadGroups.splice(index, 1);
            renderThreadGroups();
        }

        function updateThreadGroupField(index, field, value) {
            scenarioThreadGroups[index][field] = Number(value);
        }

        function updateThreadGroupKey(index, value) {
            const cleaned = (value || "").trim();
            scenarioThreadGroups[index].key = cleaned || `tg${index + 1}`;
        }

        function resetScenarioThreadGroups() {
            scenarioThreadGroups = [
                {
                    key: "tg1",
                    threads: 1,
                    ramp_up_seconds: 1,
                    duration_seconds: 60,
                    ramp_down_seconds: 1
                }
            ];
            renderThreadGroups();
        }

        function useScriptForScenario(scriptId, scriptName) {
            document.getElementById("scenarioScriptId").value = scriptId;
            if (!document.getElementById("scenarioName").value.trim()) {
                document.getElementById("scenarioName").value = `${scriptName} Scenario`;
            }
            scrollToSection("scenarioName");
            setStatus(`Script ${scriptId} selected for scenario creation.`);
        }

        function scenarioThreadGroupSummary(threadGroupsJson) {
            const parsed = safeJsonParse(threadGroupsJson, []);
            if (!Array.isArray(parsed) || !parsed.length) return "-";
            return parsed.map(tg => `${tg.key}: ${tg.threads}u / ${tg.duration_seconds}s`).join(" | ");
        }

        function scenarioThreadGroupCount(threadGroupsJson) {
            const parsed = safeJsonParse(threadGroupsJson, []);
            return Array.isArray(parsed) ? parsed.length : 0;
        }

        function artifactLinksForRun(runId) {
            const a = latestArtifactsByRun[runId] || {};
            const report = a.run_id ? `<a class="link-btn" href="/files/custom-report/${a.run_id}" target="_blank">Report</a> <a class="link-btn" href="/files/report/${a.run_id}" target="_blank" style="opacity:0.6;font-size:11px;">JMeter</a>` : `<span class="link-btn disabled">Report</span>`;
            const log = a.log_path ? `<a class="link-btn" href="/files/text?path=${encodeURIComponent(a.log_path)}" target="_blank">Log</a>` : `<span class="link-btn disabled">Log</span>`;
            const jtl = a.result_jtl_path ? `<a class="link-btn" href="/files/download?path=${encodeURIComponent(a.result_jtl_path)}" target="_blank">JTL</a>` : `<span class="link-btn disabled">JTL</span>`;
            return report + log + jtl;
        }

        function grafanaLinkForRun(run) {
            if (run && run.grafana_url) {
                return `<a class="link-btn" href="${escapeHtml(run.grafana_url)}" target="_blank">Grafana</a>`;
            }
            return `<span class="link-btn disabled">Grafana</span>`;
        }

        function renderScriptsTable(data) {
            const body = document.getElementById("scriptsTableBody");
            body.innerHTML = "";

            const scripts = (data && data.result) ? data.result : [];
            if (!Array.isArray(scripts) || !scripts.length) {
                body.innerHTML = "<tr><td colspan='5'>No scripts yet.</td></tr>";
                return;
            }

            scripts.forEach(script => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${escapeHtml(script.id ?? "")}</td>
                    <td>${escapeHtml(script.name ?? "")}</td>
                    <td>${escapeHtml(script.version ?? "")}</td>
                    <td>${escapeHtml(script.entry_jmx ?? "")}</td>
                    <td>
                        <button class="btn btn-secondary btn-small" onclick="useScriptForScenario(${script.id}, '${String(script.name || "").replaceAll("'", "\\\\'")}')">Use Script</button>
                    </td>
                `;
                body.appendChild(tr);
            });
        }

        function renderScenariosTable(scenarios) {
            const body = document.getElementById("scenariosTableBody");
            body.innerHTML = "";

            if (!Array.isArray(scenarios) || !scenarios.length) {
                body.innerHTML = "<tr><td colspan='6'>No scenarios yet.</td></tr>";
                return;
            }

            scenarios.forEach(s => {
                const tgJson = s.thread_groups_json || "";
                const tgCount = scenarioThreadGroupCount(tgJson);
                const tgSummary = scenarioThreadGroupSummary(tgJson);

                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${escapeHtml(s.id ?? "")}</td>
                    <td>${escapeHtml(s.name ?? "")}</td>
                    <td>${escapeHtml(s.script_package_id ?? "")}</td>
                    <td>${escapeHtml(tgCount || 1)}</td>
                    <td>${escapeHtml(tgSummary)}</td>
                    <td>
                        <button class="btn btn-secondary btn-small" onclick="startScenario(${s.id})">Run</button>
                        <button class="btn btn-secondary btn-small" onclick="deleteScenario(${s.id})">Delete</button>
                    </td>
                `;
                body.appendChild(tr);
            });
        }

        function renderRunsTable(data) {
            const body = document.getElementById("runsTableBody");
            body.innerHTML = "";

            const runs = (data && data.result) ? data.result : [];
            if (!Array.isArray(runs) || !runs.length) {
                body.innerHTML = "<tr><td colspan='9'>No runs yet.</td></tr>";
                return;
            }

            runs.slice().reverse().slice(0, 20).forEach(run => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${escapeHtml(run.id ?? "")}</td>
                    <td>${escapeHtml(run.scenario_id ?? "")}</td>
                    <td>${statusBadge(run.status)}</td>
                    <td>${escapeHtml(run.exit_code ?? "")}</td>
                    <td>${escapeHtml(run.started_at ?? "-")}</td>
                    <td>${escapeHtml(run.ended_at ?? "-")}</td>
                    <td>${artifactLinksForRun(run.id)}</td>
                    <td>
                        <span class="link-btn" onclick="selectRun(${run.id})">Open</span>
                        <span class="link-btn" onclick="runCommand('why did run ${run.id} fail', 'why did run ${run.id} fail')">Diagnose</span>
                        <span class="link-btn" onclick="runCommand('how to fix run ${run.id}', 'how to fix run ${run.id}')">Fix</span>
                    </td>
                    <td>${grafanaLinkForRun(run)}</td>
                `;
                body.appendChild(tr);
            });
        }

        async function postAgent(command) {
            const response = await fetch("/agent/command", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ command })
            });
            return await response.json();
        }

        async function getScenarios() {
            const response = await fetch("/scenarios");
            return await response.json();
        }

        async function fetchArtifactsForRun(runId) {
            try {
                const data = await postAgent(`show run ${runId} artifacts`);
                if (data && data.result && data.result.run_id) {
                    latestArtifactsByRun[runId] = data.result;
                }
            } catch (error) {}
        }

        async function hydrateArtifactsForRuns(runs) {
            const targets = (runs || []).slice(-8);
            for (const run of targets) {
                if (run && run.id && !latestArtifactsByRun[run.id]) {
                    await fetchArtifactsForRun(run.id);
                }
            }
        }

        async function runCommand(command, historyText = null) {
            const output = document.getElementById("output");
            if (historyText) addHistory(historyText);

            setStatus("Sending command...");
            output.textContent = "Loading...";

            try {
                const data = await postAgent(command);
                output.textContent = JSON.stringify(data, null, 2);
                renderCards(data);
                setStatus("Command completed.");
            } catch (error) {
                output.textContent = "Error: " + error;
                setStatus("Request failed.");
            }
        }

        async function sendCommand() {
            const command = document.getElementById("commandInput").value.trim();
            if (!command) {
                setStatus("Please enter a command.");
                return;
            }
            await runCommand(command, command);
        }

        async function uploadPackage() {
            const name = document.getElementById("uploadName").value.trim();
            const version = document.getElementById("uploadVersion").value.trim() || "1.0";
            const filesInput = document.getElementById("uploadFiles");
            const output = document.getElementById("output");

            if (!name) {
                setStatus("Please enter package name.");
                return;
            }
            if (!filesInput.files.length) {
                setStatus("Please select files.");
                return;
            }

            const formData = new FormData();
            formData.append("name", name);
            formData.append("version", version);
            for (const file of filesInput.files) {
                formData.append("files", file);
            }

            setStatus("Uploading package...");
            output.textContent = "Uploading...";

            try {
                const response = await fetch("/scripts/upload", { method: "POST", body: formData });
                const data = await response.json();
                output.textContent = JSON.stringify(data, null, 2);
                renderCards({ intent: "upload_package", result: data.script_package || data });
                setStatus("Package uploaded.");
                await refreshAllData();
            } catch (error) {
                output.textContent = "Error: " + error;
                setStatus("Upload failed.");
            }
        }

        async function createScenario() {
            const payload = {
                name: document.getElementById("scenarioName").value.trim(),
                script_package_id: Number(document.getElementById("scenarioScriptId").value),
                notes: document.getElementById("scenarioNotes").value.trim() || null,
                thread_groups: scenarioThreadGroups.map((tg, index) => ({
                    key: (tg.key || `tg${index + 1}`).trim(),
                    threads: Number(tg.threads),
                    ramp_up_seconds: Number(tg.ramp_up_seconds),
                    duration_seconds: Number(tg.duration_seconds),
                    ramp_down_seconds: Number(tg.ramp_down_seconds)
                }))
            };

            const output = document.getElementById("output");

            if (!payload.name || !payload.script_package_id) {
                setStatus("Please fill scenario name and script package ID.");
                return;
            }

            if (!payload.thread_groups.length) {
                setStatus("Please add at least one thread group.");
                return;
            }

            setStatus("Creating scenario...");
            output.textContent = "Creating scenario...";

            try {
                const response = await fetch("/scenarios", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();
                output.textContent = JSON.stringify(data, null, 2);
                renderCards({ intent: "create_scenario", result: data });
                setStatus("Scenario created.");

                document.getElementById("scenarioName").value = "";
                document.getElementById("scenarioNotes").value = "";
                resetScenarioThreadGroups();

                await refreshAllData();
            } catch (error) {
                output.textContent = "Error: " + error;
                setStatus("Scenario creation failed.");
            }
        }

        async function deleteScenario(scenarioId) {
            const ok = confirm(`Delete scenario ${scenarioId}?`);
            if (!ok) return;

            setStatus(`Deleting scenario ${scenarioId}...`);

            try {
                const response = await fetch(`/scenarios/${scenarioId}`, { method: "DELETE" });
                const data = await response.json();
                document.getElementById("output").textContent = JSON.stringify(data, null, 2);
                renderCards({ intent: "delete_scenario", result: data });
                setStatus(`Scenario ${scenarioId} deleted.`);
                await refreshAllData();
            } catch (error) {
                document.getElementById("output").textContent = "Error: " + error;
                setStatus("Scenario delete failed.");
            }
        }

        async function startScenario(scenarioId) {
            setStatus(`Starting scenario ${scenarioId}...`);
            document.getElementById("output").textContent = "Starting scenario...";

            try {
                const response = await fetch(`/runs/start/${scenarioId}`, { method: "POST" });
                const data = await response.json();
                document.getElementById("output").textContent = JSON.stringify(data, null, 2);
                renderCards({ intent: "start_scenario", result: data });
                setStatus(`Scenario ${scenarioId} started.`);
                await refreshDashboard();
            } catch (error) {
                document.getElementById("output").textContent = "Error: " + error;
                setStatus("Scenario start failed.");
            }
        }

        async function selectRun(runId) {
            setStatus(`Loading run ${runId} details...`);

            try {
                const statusData = await postAgent(`show run ${runId} status`);
                const summaryData = await postAgent(`summary run ${runId}`);
                const diagnosisData = await postAgent(`why did run ${runId} fail`);
                const fixData = await postAgent(`how to fix run ${runId}`);
                const artifactsData = await postAgent(`show run ${runId} artifacts`);

                const latestStatus = statusData.result || {};
                const latestSummary = summaryData.result || {};
                const latestDiagnosis = diagnosisData.result || {};
                const latestFix = fixData.result || {};
                const latestArtifacts = artifactsData.result || {};

                if (latestArtifacts.run_id) {
                    latestArtifactsByRun[latestArtifacts.run_id] = latestArtifacts;
                }

                document.getElementById("latestStatusPanel").innerHTML = `
                    ${metricRow("Run ID", latestStatus.run_id)}
                    ${metricRow("Status", latestStatus.status)}
                    ${metricRow("Started At", latestStatus.started_at)}
                    ${metricRow("Ended At", latestStatus.ended_at)}
                    ${metricRow("Exit Code", latestStatus.exit_code)}
                    ${metricRow("Error Message", latestStatus.error_message ?? "-")}
                `;

                const overall = latestSummary.overall || {};
                document.getElementById("latestSummaryPanel").innerHTML = `
                    ${metricRow("Run ID", latestSummary.run_id)}
                    ${metricRow("Execution Status", latestSummary.execution_status)}
                    ${metricRow("JTL Found", latestSummary.jtl_found)}
                    ${metricRow("Total Samples", latestSummary.total_samples)}
                    ${metricRow("Error Count", latestSummary.error_count)}
                    ${metricRow("Error %", latestSummary.error_percentage)}
                    ${metricRow("Avg (ms)", overall.avg)}
                    ${metricRow("Min (ms)", overall.min)}
                    ${metricRow("Max (ms)", overall.max)}
                    ${metricRow("Median (ms)", overall.median)}
                    ${metricRow("P90 (ms)", overall.p90)}
                    ${metricRow("P95 (ms)", overall.p95)}
                    ${metricRow("P99 (ms)", overall.p99)}
                    ${metricRow("Throughput (req/s)", overall.throughput)}
                    ${metricRow("Passed", latestSummary.passed)}
                `;

                // Populate Transaction Controllers table
                const txns = latestSummary.transactions || [];
                const txnBody = document.getElementById("transactionMetricsBody");
                if (txns.length > 0) {
                    txnBody.innerHTML = txns.map(t => `<tr>
                        <td>${t.label}</td>
                        <td>${t.count}</td>
                        <td>${t.error_count}</td>
                        <td>${t.error_pct}%</td>
                        <td>${t.avg}</td>
                        <td>${t.min}</td>
                        <td>${t.max}</td>
                        <td>${t.median}</td>
                        <td>${t.p90}</td>
                        <td>${t.p95}</td>
                        <td>${t.p99}</td>
                        <td>${t.throughput}</td>
                    </tr>`).join("");
                } else {
                    txnBody.innerHTML = '<tr><td colspan="12">No transaction controller data.</td></tr>';
                }

                // Populate Individual Samplers table
                const smps = latestSummary.samplers || [];
                const smpBody = document.getElementById("samplerMetricsBody");
                if (smps.length > 0) {
                    smpBody.innerHTML = smps.map(t => `<tr>
                        <td>${t.label}</td>
                        <td>${t.count}</td>
                        <td>${t.error_count}</td>
                        <td>${t.error_pct}%</td>
                        <td>${t.avg}</td>
                        <td>${t.min}</td>
                        <td>${t.max}</td>
                        <td>${t.median}</td>
                        <td>${t.p90}</td>
                        <td>${t.p95}</td>
                        <td>${t.p99}</td>
                        <td>${t.throughput}</td>
                    </tr>`).join("");
                } else {
                    smpBody.innerHTML = '<tr><td colspan="12">No sampler data yet.</td></tr>';
                }

                document.getElementById("latestFailureReason").textContent =
                    latestDiagnosis.diagnosis || "No diagnosis yet.";

                document.getElementById("latestFixReason").textContent =
                    (latestFix.suggestions && latestFix.suggestions.length)
                        ? latestFix.suggestions.join("\\n")
                        : "No fix suggestion yet.";

                setLiveChip(latestStatus.status);
                document.getElementById("output").textContent = JSON.stringify({
                    status: statusData,
                    summary: summaryData,
                    diagnosis: diagnosisData,
                    fix: fixData,
                    artifacts: artifactsData
                }, null, 2);

                setStatus(`Run ${runId} details loaded.`);
            } catch (error) {
                document.getElementById("output").textContent = "Error: " + error;
                setStatus("Failed to load run details.");
            }
        }

        async function refreshAllData() {
            await refreshScriptsAndScenarios();
            await refreshDashboard();
        }

        async function refreshScriptsAndScenarios() {
            try {
                const scripts = await postAgent("list scripts");
                const scenarios = await getScenarios();

                renderScriptsTable(scripts);
                renderScenariosTable(scenarios);
            } catch (error) {
                setStatus("Failed to refresh scripts/scenarios.");
            }
        }

        async function refreshDashboard() {
            setStatus("Refreshing runs...");

            try {
                const statusData = await postAgent("show latest run status");
                const runsData = await postAgent("list runs");
                const latestStatus = statusData.result || {};
                const runs = (runsData && runsData.result) ? runsData.result : [];

                setLiveChip(latestStatus.status);
                await hydrateArtifactsForRuns(runs);
                renderRunsTable(runsData);

                if (latestStatus.run_id) {
                    await selectRun(latestStatus.run_id);
                } else {
                    setStatus("No runs found.");
                }
            } catch (error) {
                setStatus("Refresh failed.");
            }
        }

        window.onload = function () {
            renderThreadGroups();
            refreshAllData();
        };
    </script>
</body>
</html>
"""