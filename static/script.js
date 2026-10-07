/* ============================================================
   IRONMIND AI - SOC DASHBOARD
============================================================ */

"use strict";


/* ============================================================
   HELPERS
============================================================ */

const $ = (id) => document.getElementById(id);

function safeNumber(value, fallback = 0) {
    const number = Number(value);

    return Number.isFinite(number)
        ? number
        : fallback;
}

function setText(id, value) {

    const element = $(id);

    if (element) {
        element.textContent = value;
    }
}

function clamp(value, min = 0, max = 100) {
    return Math.max(min, Math.min(max, value));
}


/* ============================================================
   CLOCK
============================================================ */

function updateClock() {

    const element = $("systemClock");

    if (!element) {
        return;
    }

    const now = new Date();

    element.textContent =
        now.toLocaleTimeString([], {
            hour12: false
        });
}

setInterval(updateClock, 1000);
updateClock();


/* ============================================================
   NAVIGATION
============================================================ */

function setupNavigation() {

    const navItems =
        document.querySelectorAll(".nav-item");

    const sections =
        document.querySelectorAll(".dashboard-section");

    navItems.forEach((button) => {

        button.addEventListener("click", () => {

            const sectionName =
                button.dataset.section;

            navItems.forEach((item) => {
                item.classList.remove("active");
            });

            button.classList.add("active");

            sections.forEach((section) => {
                section.classList.remove("active");
            });

            const target =
                $(`section-${sectionName}`);

            if (target) {
                target.classList.add("active");
            }
        });

    });
}

setupNavigation();


/* ============================================================
   WORKFLOW
============================================================ */

function resetWorkflow() {

    const ids = [
        "workflowDetected",
        "workflowAnomaly",
        "workflowClassified",
        "workflowQuarantine",
        "workflowReport"
    ];

    ids.forEach((id) => {

        const element = $(id);

        if (element) {
            element.classList.remove("active");
        }

    });

    setText(
        "workflowDetectedText",
        "Waiting"
    );

    setText(
        "workflowAnomalyText",
        "ML pending"
    );

    setText(
        "workflowClassifiedText",
        "Pending"
    );

    setText(
        "workflowQuarantineText",
        "Pending"
    );

    setText(
        "workflowReportText",
        "Pending"
    );
}


function activateWorkflow(
    connected,
    anomalyScore,
    threatClass,
    action
) {

    resetWorkflow();

    if (!connected) {
        return;
    }

    const detected = $("workflowDetected");
    const anomaly = $("workflowAnomaly");
    const classified = $("workflowClassified");
    const quarantine = $("workflowQuarantine");
    const report = $("workflowReport");

    detected?.classList.add("active");

    setText(
        "workflowDetectedText",
        "Device telemetry received"
    );

    anomaly?.classList.add("active");

    setText(
        "workflowAnomalyText",
        `${anomalyScore}% ML anomaly`
    );

    classified?.classList.add("active");

    setText(
        "workflowClassifiedText",
        threatClass || "Analyzed"
    );

    if (
        String(action).toUpperCase() === "QUARANTINE"
    ) {

        quarantine?.classList.add("active");

        setText(
            "workflowQuarantineText",
            "Autonomous response"
        );

        report?.classList.add("active");

        setText(
            "workflowReportText",
            "Forensic evidence available"
        );

    } else {

        setText(
            "workflowQuarantineText",
            "No quarantine required"
        );

        setText(
            "workflowReportText",
            "Monitoring"
        );
    }
}


/* ============================================================
   USB DISPLAY
============================================================ */

function updateUSB(usb, workflow) {

    if (!usb) {
        return;
    }

    const connected =
        Boolean(usb.connected);

    const score =
        clamp(
            safeNumber(
                usb.anomaly_score,
                0
            )
        );

    const threatClass =
        usb.threat_class ||
        "WAITING FOR TELEMETRY";

    const status =
        usb.status ||
        (connected
            ? "SECURE"
            : "NOT CONNECTED");

    const action =
        usb.action ||
        "No active USB event";

    setText(
        "usbDevice",
        usb.device ||
        "USB REMOVABLE DEVICE"
    );

    setText(
        "usbDrive",
        connected
            ? (
                usb.drive ||
                "USB CONNECTED"
            )
            : "NOT CONNECTED"
    );

    setText(
        "usbScore",
        score
    );

    const scoreBar =
        $("usbScoreBar");

    if (scoreBar) {
        scoreBar.style.width =
            `${score}%`;
    }

    setText(
        "usbThreatClass",
        threatClass
    );

    setText(
        "usbStatus",
        status
    );

    setText(
        "usbAction",
        action
    );

    setText(
        "endpointUsbStatus",
        status
    );

    setText(
        "endpointUsbFiles",
        safeNumber(
            usb.files_scanned,
            0
        )
    );

    setText(
        "endpointUsbRisk",
        `${score}%`
    );

    setText(
        "usbActivity",
        connected ? 1 : 0
    );

    activateWorkflow(
        connected,
        score,
        threatClass,
        action
    );

    if (score >= 85) {

        document
            .querySelector(".usb-status strong")
            ?.style
            .setProperty(
                "color",
                "var(--red)"
            );

    } else if (score >= 70) {

        document
            .querySelector(".usb-status strong")
            ?.style
            .setProperty(
                "color",
                "var(--yellow)"
            );

    } else {

        document
            .querySelector(".usb-status strong")
            ?.style
            .setProperty(
                "color",
                "var(--green)"
            );
    }
}


/* ============================================================
   METRICS
============================================================ */

function updateMetrics(data) {

    if (!data) {
        return;
    }

    const risk =
        clamp(
            safeNumber(
                data.risk,
                0
            )
        );

    const aiRisk =
        clamp(
            safeNumber(
                data.ai_risk,
                0
            )
        );

    setText(
        "risk",
        risk
    );

    setText(
        "aiRisk",
        aiRisk
    );

    setText(
        "threats",
        safeNumber(
            data.threats,
            0
        )
    );

    setText(
        "blocked",
        safeNumber(
            data.blocked,
            0
        )
    );

    setText(
        "riskStatus",
        data.status ||
        "SYSTEM PROTECTED"
    );

    setText(
        "endpointStatus",
        data.modules?.endpoint ||
        "SECURE"
    );

    setText(
        "cpu",
        `${safeNumber(data.endpoint?.cpu, 0)}%`
    );

    setText(
        "memory",
        `${safeNumber(data.endpoint?.memory, 0)}%`
    );

    setText(
        "endpointCpu",
        `${safeNumber(data.endpoint?.cpu, 0)}%`
    );

    setText(
        "endpointMemory",
        `${safeNumber(data.endpoint?.memory, 0)}%`
    );

    setText(
        "networkTraffic",
        `${safeNumber(data.endpoint?.network_traffic, 0)}%`
    );

    setText(
        "networkPanelTraffic",
        `${safeNumber(data.endpoint?.network_traffic, 0)}%`
    );

    setText(
        "networkRisk",
        `${safeNumber(data.network?.risk, 0)}%`
    );

    setText(
        "networkDevices",
        safeNumber(
            data.infrastructure?.network_devices,
            18
        )
    );

    setText(
        "networkPanelDevices",
        safeNumber(
            data.infrastructure?.network_devices,
            18
        )
    );

    setText(
        "endpointCount",
        safeNumber(
            data.infrastructure?.endpoints,
            12
        )
    );

    setText(
        "cloudCount",
        safeNumber(
            data.infrastructure?.cloud,
            8
        )
    );

    setText(
        "networkCount",
        safeNumber(
            data.infrastructure?.network_devices,
            18
        )
    );

    setText(
        "aiProcessing",
        `${safeNumber(data.ai_processing, 0)}%`
    );

    setText(
        "lastUpdate",
        data.last_update
            ? new Date(
                data.last_update
              ).toLocaleTimeString()
            : "LIVE"
    );

    updateUSB(
        data.usb,
        data.workflow
    );
}


/* ============================================================
   STATUS
============================================================ */

async function loadStatus() {

    try {

        const response =
            await fetch(
                "/api/status",
                {
                    cache: "no-store"
                }
            );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const data =
            await response.json();

        updateMetrics(data);

    } catch (error) {

        console.error(
            "IronMind status error:",
            error
        );
    }
}


/* ============================================================
   THREAT TABLE
============================================================ */

function severityClass(severity) {

    const value =
        String(severity || "")
            .toUpperCase();

    if (value === "CRITICAL") {
        return "CRITICAL";
    }

    if (value === "HIGH") {
        return "HIGH";
    }

    if (value === "MEDIUM") {
        return "MEDIUM";
    }

    return "LOW";
}


function renderThreats(data) {

    if (!Array.isArray(data)) {
        return;
    }

    const table =
        $("threatTable");

    if (!table) {
        return;
    }

    if (data.length === 0) {

        table.innerHTML = `
            <tr>
                <td colspan="7" class="table-empty">
                    No threats detected
                </td>
            </tr>
        `;

        return;
    }

    table.innerHTML =
        data.map((threat) => {

            const severity =
                severityClass(
                    threat.severity
                );

            return `
                <tr>
                    <td>
                        ${threat.timestamp || "--"}
                    </td>

                    <td>
                        ${threat.source || "UNKNOWN"}
                    </td>

                    <td>
                        ${threat.threat_type || "UNKNOWN"}
                    </td>

                    <td>
                        ${safeNumber(
                            threat.risk_score,
                            0
                        )}%
                    </td>

                    <td>
                        ${severity}
                    </td>

                    <td>
                        ${threat.action || "MONITOR"}
                    </td>

                    <td>
                        ${threat.status || "OPEN"}
                    </td>
                </tr>
            `;

        })
        .join("");

    updateThreatCounters(data);
}


function updateThreatCounters(data) {

    let critical = 0;
    let high = 0;
    let medium = 0;
    let low = 0;

    data.forEach((threat) => {

        const severity =
            String(
                threat.severity || ""
            ).toUpperCase();

        if (severity === "CRITICAL") {
            critical++;
        } else if (severity === "HIGH") {
            high++;
        } else if (severity === "MEDIUM") {
            medium++;
        } else {
            low++;
        }

    });

    setText(
        "criticalThreats",
        critical
    );

    setText(
        "highThreats",
        high
    );

    setText(
        "mediumThreats",
        medium
    );

    setText(
        "lowThreats",
        low
    );
}


async function loadThreats() {

    try {

        const response =
            await fetch(
                "/api/threats",
                {
                    cache: "no-store"
                }
            );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const data =
            await response.json();

        renderThreats(data);

        if (Array.isArray(data) &&
            data.length > 0) {

            const latest = data[0];

            setText(
                "reportThreat",
                latest.threat_type ||
                "Security incident"
            );

            setText(
                "reportDetails",
                `${latest.source || "Unknown source"} • ${
                    latest.status || "OPEN"
                } • ${
                    latest.action || "MONITOR"
                }`
            );

            setText(
                "reportRisk",
                `${safeNumber(
                    latest.risk_score,
                    0
                )}%`
            );
        }

    } catch (error) {

        console.error(
            "IronMind threat error:",
            error
        );
    }
}


/* ============================================================
   EVENT STREAM
============================================================ */

function addEvent(text, detail) {

    const list =
        $("eventList");

    if (!list) {
        return;
    }

    const empty =
        list.querySelector(".empty-event");

    if (empty) {
        empty.remove();
    }

    const row =
        document.createElement("div");

    row.className =
        "event-row";

    row.innerHTML = `
        <span>◉</span>
        <div>
            <strong>${text}</strong>
            <small>${detail}</small>
        </div>
    `;

    list.prepend(row);

    while (list.children.length > 8) {
        list.removeChild(
            list.lastElementChild
        );
    }
}


/* ============================================================
   TEST BUTTON SUPPORT
   ============================================================ */

async function postTest(endpoint) {

    try {

        const response =
            await fetch(
                endpoint,
                {
                    method: "POST"
                }
            );

        const data =
            await response.json();

        updateMetrics(
            data.state || data
        );

        await loadThreats();

        return data;

    } catch (error) {

        console.error(
            "IronMind test error:",
            error
        );

        return null;
    }
}


async function runUSBThreatTest() {

    const result =
        await postTest(
            "/api/usb-threat-test"
        );

    if (result) {

        addEvent(
            "USB ML test executed",
            `Anomaly score ${
                result.anomaly_score ?? 0
            }%`
        );
    }
}


async function runEndpointTest() {

    const result =
        await postTest(
            "/api/endpoint-test"
        );

    if (result) {
        addEvent(
            "Endpoint anomaly test",
            "Endpoint response workflow executed"
        );
    }
}


async function runNetworkTest() {

    const result =
        await postTest(
            "/api/network-test"
        );

    if (result) {
        addEvent(
            "Network anomaly test",
            "Network response workflow executed"
        );
    }
}


async function resetSystem() {

    try {

        await fetch(
            "/api/reset",
            {
                method: "POST"
            }
        );

        resetWorkflow();

        await loadStatus();
        await loadThreats();

        addEvent(
            "System reset",
            "IronMind defense state restored"
        );

    } catch (error) {

        console.error(
            "Reset error:",
            error
        );
    }
}


/* ============================================================
   GLOBAL FUNCTIONS
============================================================ */

window.runUSBThreatTest =
    runUSBThreatTest;

window.runEndpointTest =
    runEndpointTest;

window.runNetworkTest =
    runNetworkTest;

window.resetSystem =
    resetSystem;


/* ============================================================
   INITIALIZATION
============================================================ */

async function initializeDashboard() {

    resetWorkflow();

    await loadStatus();

    await loadThreats();

}

initializeDashboard();


/* ============================================================
   LIVE POLLING
============================================================ */

setInterval(
    loadStatus,
    3000
);

setInterval(
    loadThreats,
    5000
);
