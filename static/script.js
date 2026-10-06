"use strict";


/* ============================================================
   HELPERS
   ============================================================ */

function setText(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = value;
    }
}


function numberValue(value, fallback = 0) {
    const number = Number(value);

    if (Number.isFinite(number)) {
        return number;
    }

    return fallback;
}


function escapeHTML(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/* ============================================================
   NAVIGATION
   ============================================================ */

const navItems = document.querySelectorAll(
    ".nav-item"
);

const pages = document.querySelectorAll(
    ".page"
);


navItems.forEach((button) => {

    button.addEventListener(
        "click",
        () => {

            const pageName =
                button.dataset.page;

            navItems.forEach((item) => {
                item.classList.remove("active");
            });

            button.classList.add("active");

            pages.forEach((page) => {
                page.classList.remove("active");
            });

            const target =
                document.getElementById(
                    `page-${pageName}`
                );

            if (target) {
                target.classList.add("active");
            }

            const titleMap = {
                dashboard:
                    "Security Operations Center",

                threats:
                    "Detected Threats",

                endpoints:
                    "Protected Endpoints",

                network:
                    "Network Security",

                iot:
                    "IoT / Sensors",

                ot:
                    "Industrial / OT",

                ai:
                    "AI Intelligence",

                reports:
                    "Forensic Reports",
            };

            setText(
                "pageTitle",
                titleMap[pageName] ||
                    "Security Operations Center"
            );
        }
    );

});


/* ============================================================
   STATUS
   ============================================================ */

async function loadStatus() {

    try {

        const response = await fetch(
            "/api/status",
            {
                cache: "no-store",
            }
        );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const data =
            await response.json();

        updateDashboard(data);

    } catch (error) {

        console.error(
            "Status error:",
            error
        );
    }
}


/* ============================================================
   DASHBOARD
   ============================================================ */

function updateDashboard(data) {

    if (!data) {
        return;
    }


    /* --------------------------------------------------------
       MAIN METRICS
       -------------------------------------------------------- */

    setText(
        "risk",
        numberValue(
            data.risk,
            0
        )
    );

    setText(
        "aiRisk",
        numberValue(
            data.ai_risk,
            0
        )
    );

    setText(
        "threats",
        numberValue(
            data.threats,
            0
        )
    );

    setText(
        "blocked",
        numberValue(
            data.blocked,
            0
        )
    );


    /* --------------------------------------------------------
       SYSTEM
       -------------------------------------------------------- */

    setText(
        "systemStatus",
        data.status ||
            "PROTECTED"
    );


    /* --------------------------------------------------------
       MODULES
       -------------------------------------------------------- */

    const modules =
        data.modules || {};

    setText(
        "endpointStatus",
        modules.endpoint ||
            "SECURE"
    );

    setText(
        "networkStatus",
        modules.network ||
            "MONITORING"
    );


    setText(
        "endpointPageStatus",
        modules.endpoint ||
            "SECURE"
    );

    setText(
        "networkPageStatus",
        modules.network ||
            "MONITORING"
    );


    /* --------------------------------------------------------
       ENDPOINT
       -------------------------------------------------------- */

    const endpoint =
        data.endpoint || {};

    setText(
        "cpu",
        `${numberValue(
            endpoint.cpu,
            0
        )}%`
    );

    setText(
        "memory",
        `${numberValue(
            endpoint.memory,
            0
        )}%`
    );

    setText(
        "networkTraffic",
        `${numberValue(
            endpoint.network_traffic,
            0
        )}%`
    );


    /* --------------------------------------------------------
       USB
       -------------------------------------------------------- */

    updateUSB(
        data.usb || {}
    );


    /* --------------------------------------------------------
       NETWORK
       -------------------------------------------------------- */

    updateNetwork(
        data.network || {}
    );


    /* --------------------------------------------------------
       WORKFLOW
       -------------------------------------------------------- */

    updateWorkflow(
        data.workflow || {}
    );
}


/* ============================================================
   USB
   ============================================================ */

function updateUSB(usb) {

    const score =
        Math.max(
            0,
            Math.min(
                100,
                numberValue(
                    usb.anomaly_score,
                    0
                )
            )
        );


    setText(
        "usbStatus",
        usb.status ||
            "NOT CONNECTED"
    );

    setText(
        "usbDevice",
        usb.device ||
            "WAITING"
    );

    setText(
        "usbDrive",
        usb.drive ||
            "-"
    );

    setText(
        "usbFilesystem",
        usb.filesystem ||
            "-"
    );

    setText(
        "usbFiles",
        numberValue(
            usb.files_scanned,
            0
        )
    );


    /* --------------------------------------------------------
       THIS FIXES "None"
       -------------------------------------------------------- */

    setText(
        "usbScore",
        `${score}%`
    );

    setText(
        "usbThreatClass",
        usb.threat_class ||
            "NONE"
    );

    setText(
        "usbSeverity",
        usb.severity ||
            "LOW"
    );

    setText(
        "usbAction",
        usb.action ||
            "MONITOR"
    );


    setText(
        "usbPageScore",
        `ANOMALY SCORE: ${score}%`
    );


    const scoreBar =
        document.getElementById(
            "usbScoreBar"
        );

    if (scoreBar) {
        scoreBar.style.width =
            `${score}%`;
    }
}


/* ============================================================
   WORKFLOW
   ============================================================ */

function updateWorkflow(workflow) {

    if (!workflow) {
        return;
    }


    updateStep(
        "step-device",
        workflow.device_detected
    );

    updateStep(
        "step-anomaly",
        workflow.anomaly_detected
    );

    updateStep(
        "step-classified",
        workflow.threat_classified
    );

    updateStep(
        "step-quarantine",
        workflow.device_quarantined
    );

    updateStep(
        "step-report",
        workflow.forensic_report_generated
    );


    const usbScore =
        numberValue(
            document
                .getElementById(
                    "usbScore"
                )
                ?.textContent
                ?.replace("%", ""),
            0
        );

    setText(
        "workflowScore",
        `${usbScore}%`
    );


    setText(
        "workflowClass",
        document
            .getElementById(
                "usbThreatClass"
            )
            ?.textContent ||
            "Waiting"
    );


    const completed =
        Boolean(
            workflow.forensic_report_generated
        );

    setText(
        "workflowStatus",
        completed
            ? "COMPLETE"
            : workflow.device_detected
                ? "ACTIVE"
                : "STANDBY"
    );
}


function updateStep(
    id,
    active
) {

    const element =
        document.getElementById(id);

    if (!element) {
        return;
    }

    element.classList.toggle(
        "complete",
        Boolean(active)
    );

    element.classList.toggle(
        "active",
        Boolean(active)
    );
}


/* ============================================================
   NETWORK
   ============================================================ */

function updateNetwork(network) {

    setText(
        "networkScore",
        numberValue(
            network.anomaly_score,
            0
        )
    );

    setText(
        "networkTrafficValue",
        numberValue(
            network.traffic,
            0
        )
    );

    setText(
        "networkConnections",
        numberValue(
            network.connections,
            0
        )
    );

    setText(
        "networkPageStatus",
        network.status ||
            "MONITORING"
    );
}


/* ============================================================
   USB TEST
   ============================================================ */

async function runUSBTest() {

    try {

        const response =
            await fetch(
                "/api/usb-threat-test",
                {
                    method: "POST",
                }
            );

        const data =
            await response.json();

        console.log(
            "USB ML result:",
            data
        );

        await loadStatus();
        await loadThreats();
        await loadReports();

    } catch (error) {

        console.error(
            "USB test failed:",
            error
        );
    }
}


/* ============================================================
   NETWORK TEST
   ============================================================ */

async function runNetworkTest() {

    try {

        const response =
            await fetch(
                "/api/network-test",
                {
                    method: "POST",
                }
            );

        const data =
            await response.json();

        console.log(
            "Network ML result:",
            data
        );

        await loadStatus();

    } catch (error) {

        console.error(
            "Network test failed:",
            error
        );
    }
}


/* ============================================================
   ENDPOINT TEST
   ============================================================ */

async function runEndpointTest() {

    try {

        const response =
            await fetch(
                "/api/endpoint-test",
                {
                    method: "POST",
                }
            );

        const data =
            await response.json();

        console.log(
            "Endpoint ML result:",
            data
        );

        await loadStatus();

    } catch (error) {

        console.error(
            "Endpoint test failed:",
            error
        );
    }
}


/* ============================================================
   RESET
   ============================================================ */

async function resetSystem() {

    try {

        await fetch(
            "/api/reset",
            {
                method: "POST",
            }
        );

        await loadStatus();
        await loadThreats();
        await loadReports();

    } catch (error) {

        console.error(
            "Reset failed:",
            error
        );
    }
}


/* ============================================================
   THREATS
   ============================================================ */

async function loadThreats() {

    try {

        const response =
            await fetch(
                "/api/threats",
                {
                    cache: "no-store",
                }
            );

        const data =
            await response.json();

        renderThreats(
            data.threats || []
        );

    } catch (error) {

        console.error(
            "Threat loading failed:",
            error
        );
    }
}


function renderThreats(threats) {

    const table =
        document.getElementById(
            "threatTable"
        );

    if (!table) {
        return;
    }

    if (!threats.length) {

        table.innerHTML = `
            <tr>
                <td colspan="7">
                    No threats detected.
                </td>
            </tr>
        `;

        return;
    }


    table.innerHTML =
        threats.map(
            (threat) => {

                return `
                    <tr>
                        <td>
                            ${escapeHTML(
                                threat.timestamp
                            )}
                        </td>

                        <td>
                            ${escapeHTML(
                                threat.source
                            )}
                        </td>

                        <td>
                            ${escapeHTML(
                                threat.threat_type
                            )}
                        </td>

                        <td>
                            ${numberValue(
                                threat.anomaly_score ??
                                threat.risk_score,
                                0
                            )}%
                        </td>

                        <td>
                            ${escapeHTML(
                                threat.severity
                            )}
                        </td>

                        <td>
                            ${escapeHTML(
                                threat.action
                            )}
                        </td>

                        <td>
                            ${escapeHTML(
                                threat.status
                            )}
                        </td>
                    </tr>
                `;
            }
        ).join("");
}


/* ============================================================
   REPORTS
   ============================================================ */

async function loadReports() {

    try {

        const response =
            await fetch(
                "/api/investigations",
                {
                    cache: "no-store",
                }
            );

        const data =
            await response.json();

        renderReports(
            data.investigations || []
        );

    } catch (error) {

        console.error(
            "Report loading failed:",
            error
        );
    }
}


function renderReports(reports) {

    const container =
        document.getElementById(
            "reportList"
        );

    if (!container) {
        return;
    }

    if (!reports.length) {

        container.innerHTML = `
            <div class="empty-state">
                No forensic reports generated yet.
            </div>
        `;

        return;
    }


    container.innerHTML =
        reports.map(
            (report) => {

                return `
                    <div class="panel">

                        <div class="panel-header">

                            <div>
                                <span class="eyebrow">
                                    FORENSIC REPORT
                                </span>

                                <h3>
                                    Incident #${escapeHTML(
                                        report.id
                                    )}
                                </h3>
                            </div>

                            <span class="badge success">
                                REPORT GENERATED
                            </span>

                        </div>

                        <div class="telemetry-grid">

                            <div>
                                <label>
                                    SOURCE
                                </label>

                                <strong>
                                    ${escapeHTML(
                                        report.source
                                    )}
                                </strong>
                            </div>

                            <div>
                                <label>
                                    ANOMALY
                                </label>

                                <strong>
                                    ${numberValue(
                                        report.anomaly_score,
                                        0
                                    )}%
                                </strong>
                            </div>

                            <div>
                                <label>
                                    THREAT
                                </label>

                                <strong>
                                    ${escapeHTML(
                                        report.threat_class
                                    )}
                                </strong>
                            </div>

                            <div>
                                <label>
                                    STATUS
                                </label>

                                <strong>
                                    ${escapeHTML(
                                        report.status
                                    )}
                                </strong>
                            </div>

                        </div>

                    </div>
                `;
            }
        ).join("");
}


/* ============================================================
   START
   ============================================================ */

async function startDashboard() {

    await loadStatus();
    await loadThreats();
    await loadReports();

    setInterval(
        loadStatus,
        3000
    );

    setInterval(
        loadThreats,
        5000
    );

    setInterval(
        loadReports,
        5000
    );
}


document.addEventListener(
    "DOMContentLoaded",
    startDashboard
);
