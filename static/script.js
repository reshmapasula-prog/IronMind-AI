"use strict";


const $ = (id) => document.getElementById(id);


function setText(id, value) {
    const element = $(id);

    if (element) {
        element.textContent = value;
    }
}


function escapeHTML(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function showNotification(message) {
    const notification = $("notification");

    if (!notification) {
        return;
    }

    notification.textContent = message;
    notification.classList.add("show");

    setTimeout(() => {
        notification.classList.remove("show");
    }, 4500);
}


/* NAVIGATION */

function showPage(pageName) {

    document.querySelectorAll(".page").forEach((page) => {
        page.classList.remove("active-page");
    });

    document.querySelectorAll(".nav-item").forEach((button) => {
        button.classList.remove("active");
    });

    const page = $(`page-${pageName}`);

    if (page) {
        page.classList.add("active-page");
    }

    const navButton = document.querySelector(
        `.nav-item[data-page="${pageName}"]`
    );

    if (navButton) {
        navButton.classList.add("active");
    }

    if (pageName === "threats") {
        loadThreats();
    }

    if (pageName === "reports") {
        loadReports();
    }
}


document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".nav-item").forEach((button) => {

        button.addEventListener("click", () => {
            showPage(button.dataset.page);
        });

    });

    updateDashboard();
    loadThreats();
    loadReports();

    setInterval(updateDashboard, 2500);
});


/* STATUS */

async function updateDashboard() {

    try {

        const response = await fetch("/api/status", {
            cache: "no-store"
        });

        if (!response.ok) {
            return;
        }

        const state = await response.json();

        renderState(state);

    } catch (error) {

        console.error(
            "IronMind status update failed:",
            error
        );

    }
}


function renderState(state) {

    setText("risk", `${state.risk}%`);
    setText("aiRisk", `${state.ai_risk}%`);
    setText("threats", state.threats);
    setText("blocked", state.blocked);

    setText(
        "riskStatus",
        state.status
    );

    setText(
        "endpointStatus",
        state.modules?.endpoint || "UNKNOWN"
    );

    setText(
        "networkStatus",
        state.modules?.network || "UNKNOWN"
    );

    setText(
        "endpointModule",
        state.modules?.endpoint || "UNKNOWN"
    );

    setText(
        "networkModule",
        state.modules?.network || "UNKNOWN"
    );


    /* ENDPOINT */

    const endpoint = state.endpoint_telemetry || {};

    setText(
        "cpu",
        `${Math.round(endpoint.cpu ?? 0)}%`
    );

    setText(
        "memory",
        `${Math.round(endpoint.memory ?? 0)}%`
    );

    setText(
        "endpointNetwork",
        `${Math.round(endpoint.network_traffic ?? 0)}%`
    );

    setText(
        "processCount",
        Math.round(endpoint.process_count ?? 0)
    );

    setText(
        "detailCpu",
        `${Math.round(endpoint.cpu ?? 0)}%`
    );

    setText(
        "detailMemory",
        `${Math.round(endpoint.memory ?? 0)}%`
    );

    setText(
        "detailNetwork",
        `${Math.round(endpoint.network_traffic ?? 0)}%`
    );

    setText(
        "detailProcesses",
        Math.round(endpoint.process_count ?? 0)
    );

    setText(
        "endpointDetailStatus",
        state.modules?.endpoint || "UNKNOWN"
    );


    /* NETWORK */

    const network = state.network_telemetry || {};

    setText(
        "trafficRate",
        `${Math.round(network.traffic_rate ?? 0)}%`
    );

    setText(
        "connectionCount",
        Math.round(network.connection_count ?? 0)
    );

    setText(
        "failedConnections",
        Math.round(network.failed_connections ?? 0)
    );

    setText(
        "destinations",
        Math.round(network.unique_destinations ?? 0)
    );

    setText(
        "detailTraffic",
        `${Math.round(network.traffic_rate ?? 0)}%`
    );

    setText(
        "detailConnections",
        Math.round(network.connection_count ?? 0)
    );

    setText(
        "detailFailed",
        Math.round(network.failed_connections ?? 0)
    );

    setText(
        "detailDestinations",
        Math.round(network.unique_destinations ?? 0)
    );

    setText(
        "networkDetailStatus",
        state.modules?.network || "UNKNOWN"
    );


    /* USB */

    const usb = state.usb || {};

    setText(
        "usbStatus",
        usb.connected
            ? usb.scan || "CONNECTED"
            : "WAITING"
    );

    setText(
        "usbDevice",
        usb.device || "WAITING FOR USB AGENT"
    );

    setText(
        "usbDrive",
        usb.drive || "--"
    );

    setText(
        "usbFiles",
        usb.files_scanned ?? 0
    );

    setText(
        "usbSuspicious",
        usb.suspicious ?? 0
    );


    /* WORKFLOW */

    renderWorkflow(
        state.workflow || {},
        state.risk
    );
}


function renderWorkflow(workflow, fallbackScore) {

    const steps = [
        "stepDetected",
        "stepAnomaly",
        "stepClassified",
        "stepResponse",
        "stepReport"
    ];

    steps.forEach((id) => {
        const element = $(id);

        if (element) {
            element.classList.remove("active");
        }
    });


    if (workflow.device_detected) {
        $("stepDetected")?.classList.add("active");
    }

    if (workflow.anomaly_detected) {
        $("stepAnomaly")?.classList.add("active");
    }

    if (workflow.threat_classified) {
        $("stepClassified")?.classList.add("active");
    }

    if (workflow.response_executed) {
        $("stepResponse")?.classList.add("active");
    }

    if (workflow.forensic_report) {
        $("stepReport")?.classList.add("active");
    }


    const score =
        workflow.anomaly_detected
            ? `${fallbackScore}%`
            : "--";

    setText(
        "workflowScore",
        score
    );

    setText(
        "workflowStage",
        workflow.current_stage || "MONITORING"
    );
}


/* ENDPOINT TEST */

async function runEndpointTest() {

    showNotification(
        "Running endpoint ML anomaly detection..."
    );

    try {

        const response = await fetch(
            "/api/endpoint-test",
            {
                method: "POST"
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.message || "Endpoint test failed"
            );
        }

        showNotification(
            `Endpoint threat detected — ${data.detection.anomaly_score}% anomaly score. Device quarantined.`
        );

        renderState(data.state);

        loadThreats();
        loadReports();

    } catch (error) {

        console.error(error);

        showNotification(
            "Endpoint test failed."
        );
    }
}


/* NETWORK TEST */

async function runNetworkTest() {

    showNotification(
        "Running network ML anomaly detection..."
    );

    try {

        const response = await fetch(
            "/api/network-test",
            {
                method: "POST"
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.message || "Network test failed"
            );
        }

        showNotification(
            `Network anomaly detected — ${data.detection.anomaly_score}% score. Connection isolated.`
        );

        renderState(data.state);

        loadThreats();
        loadReports();

    } catch (error) {

        console.error(error);

        showNotification(
            "Network test failed."
        );
    }
}


/* USB TEST */

async function runUSBThreatTest() {

    showNotification(
        "Running USB ML threat simulation..."
    );

    try {

        const response = await fetch(
            "/api/usb-threat-test",
            {
                method: "POST"
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.message || "USB test failed"
            );
        }

        showNotification(
            `USB threat detected — ${data.detection.anomaly_score}% score. Device quarantined.`
        );

        renderState(data.state);

        loadThreats();
        loadReports();

    } catch (error) {

        console.error(error);

        showNotification(
            "USB test failed."
        );
    }
}


/* THREATS */

async function loadThreats() {

    try {

        const response = await fetch(
            "/api/threats",
            {
                cache: "no-store"
            }
        );

        if (!response.ok) {
            return;
        }

        const threats = await response.json();

        renderThreats(threats);

    } catch (error) {

        console.error(
            "Threat loading failed:",
            error
        );
    }
}


function renderThreats(threats) {

    const container = $("threatList");

    if (!container) {
        return;
    }

    if (!threats.length) {

        container.innerHTML = `
            <div class="empty-state">
                No threat records.
            </div>
        `;

        return;
    }


    container.innerHTML = threats
        .map((threat) => {

            return `
                <article class="threat-card">

                    <div class="threat-card-header">

                        <div>
                            <div class="eyebrow">
                                ${escapeHTML(threat.source)}
                            </div>

                            <h3>
                                ${escapeHTML(threat.threat_type)}
                            </h3>
                        </div>

                        <span class="badge danger">
                            ${escapeHTML(threat.status)}
                        </span>

                    </div>

                    <p>
                        ${escapeHTML(threat.reason)}
                    </p>

                    <div class="threat-meta">

                        <div>
                            <span>ANOMALY SCORE</span>
                            <strong>
                                ${escapeHTML(threat.risk_score)}%
                            </strong>
                        </div>

                        <div>
                            <span>SEVERITY</span>
                            <strong>
                                ${escapeHTML(threat.severity)}
                            </strong>
                        </div>

                        <div>
                            <span>ACTION</span>
                            <strong>
                                ${escapeHTML(threat.action)}
                            </strong>
                        </div>

                        <div>
                            <span>SHA-256</span>
                            <strong>
                                ${escapeHTML(
                                    String(threat.sha256).slice(0, 16)
                                )}...
                            </strong>
                        </div>

                    </div>

                </article>
            `;

        })
        .join("");
}


/* REPORTS */

async function loadReports() {

    try {

        const response = await fetch(
            "/api/investigations",
            {
                cache: "no-store"
            }
        );

        if (!response.ok) {
            return;
        }

        const reports = await response.json();

        renderReports(reports);

    } catch (error) {

        console.error(
            "Report loading failed:",
            error
        );
    }
}


function renderReports(reports) {

    const container = $("reportList");

    if (!container) {
        return;
    }

    if (!reports.length) {

        container.innerHTML = `
            <div class="empty-state">
                No forensic reports generated.
            </div>
        `;

        return;
    }


    container.innerHTML = reports
        .map((report) => {

            return `
                <article class="report-card">

                    <div class="report-card-header">

                        <div>
                            <div class="eyebrow">
                                FORENSIC REPORT
                            </div>

                            <h3>
                                ${escapeHTML(report.threat_type)}
                            </h3>
                        </div>

                        <span class="badge success">
                            GENERATED
                        </span>

                    </div>

                    <p>
                        ${escapeHTML(report.reason)}
                    </p>

                    <div class="threat-meta">

                        <div>
                            <span>SOURCE</span>
                            <strong>
                                ${escapeHTML(report.source)}
                            </strong>
                        </div>

                        <div>
                            <span>RISK</span>
                            <strong>
                                ${escapeHTML(report.risk_score)}%
                            </strong>
                        </div>

                        <div>
                            <span>SEVERITY</span>
                            <strong>
                                ${escapeHTML(report.severity)}
                            </strong>
                        </div>

                        <div>
                            <span>REPORT ID</span>
                            <strong>
                                ${escapeHTML(report.id)}
                            </strong>
                        </div>

                    </div>

                </article>
            `;

        })
        .join("");
}


/* RESET */

async function resetSystem() {

    try {

        const response = await fetch(
            "/api/reset",
            {
                method: "POST"
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.message || "Reset failed"
            );
        }

        renderState(data.state);

        loadThreats();
        loadReports();

        showNotification(
            "IronMind AI system reset to protected monitoring."
        );

    } catch (error) {

        console.error(error);

        showNotification(
            "System reset failed."
        );
    }
}
