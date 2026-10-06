(() => {
    "use strict";


    // ============================================================
    // HELPERS
    // ============================================================

    const $ = (id) => document.getElementById(id);


    function text(id, value) {
        const element = $(id);

        if (element) {
            element.textContent = value;
        }
    }


    function number(value, fallback = 0) {
        const parsed = Number(value);

        return Number.isFinite(parsed)
            ? parsed
            : fallback;
    }


    function safe(value) {
        return String(
            value ?? ""
        )
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }


    function formatTime(value) {

        if (!value) {
            return "—";
        }

        try {
            const date = new Date(value);

            return date.toLocaleTimeString(
                [],
                {
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                }
            );

        } catch {
            return value;
        }
    }


    async function getJSON(url, options = {}) {

        const response = await fetch(
            url,
            {
                cache: "no-store",
                ...options,
            }
        );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        return response.json();
    }


    // ============================================================
    // FRONT PAGE USB
    // ============================================================

    function updateFrontPage(state) {

        if (!state || !state.usb) {
            return;
        }

        const usb = state.usb;

        const connected = Boolean(
            usb.connected
        );

        text(
            "frontUsbStatus",
            connected
                ? usb.status || "CONNECTED"
                : "NOT CONNECTED"
        );

        text(
            "frontUsbDevice",
            connected
                ? usb.device || "USB DEVICE"
                : "—"
        );

        text(
            "frontUsbDrive",
            connected
                ? usb.drive || "—"
                : "—"
        );

        text(
            "frontUsbFiles",
            connected
                ? number(
                    usb.files_scanned
                )
                : 0
        );

        text(
            "frontUsbScore",
            `${number(
                usb.anomaly_score
            )}%`
        );

        const indicator = $(
            "frontUsbIndicator"
        );

        if (indicator) {

            indicator.classList.toggle(
                "danger",
                number(
                    usb.anomaly_score
                ) >= 70
            );
        }
    }


    // ============================================================
    // DASHBOARD STATUS
    // ============================================================

    function updateDashboard(state) {

        if (!state) {
            return;
        }

        const risk = number(
            state.risk
        );

        const aiRisk = number(
            state.ai_risk
        );

        text(
            "risk",
            risk
        );

        text(
            "aiRisk",
            aiRisk
        );

        text(
            "threats",
            number(
                state.threats
            )
        );

        text(
            "blocked",
            number(
                state.blocked
            )
        );

        text(
            "incidentScore",
            risk
        );

        text(
            "incidentText",
            state.incident ||
            "No active incident"
        );

        text(
            "lastUpdate",
            formatTime(
                state.last_update
            )
        );


        const riskBar = $(
            "riskBar"
        );

        if (riskBar) {
            riskBar.style.width =
                `${Math.min(
                    100,
                    Math.max(0, risk)
                )}%`;
        }


        const aiRiskBar = $(
            "aiRiskBar"
        );

        if (aiRiskBar) {
            aiRiskBar.style.width =
                `${Math.min(
                    100,
                    Math.max(0, aiRisk)
                )}%`;
        }


        const modules =
            state.modules || {};


        text(
            "endpointStatus",
            modules.endpoint ||
            "SECURE"
        );

        text(
            "networkStatus",
            modules.network ||
            "MONITORING"
        );

        text(
            "moduleEndpoint",
            modules.endpoint ||
            "SECURE"
        );

        text(
            "moduleNetwork",
            modules.network ||
            "MONITORING"
        );


        updateStatusBadge(
            "systemStatusBadge",
            state.status
        );

        updateStatusBadge(
            "endpointPageStatus",
            modules.endpoint
        );

        updateStatusBadge(
            "endpointUsbStatus",
            state.usb?.status
        );


        updateUSB(
            state.usb
        );


        updateWorkflow(
            state.workflow,
            state.usb
        );


        updateEndpointTelemetry(
            state.endpoint_telemetry
        );


        updateFrontPage(
            state
        );
    }


    // ============================================================
    // STATUS BADGES
    // ============================================================

    function updateStatusBadge(
        id,
        value
    ) {

        const element = $(id);

        if (!element) {
            return;
        }

        const status = String(
            value || "UNKNOWN"
        ).toUpperCase();

        element.textContent = status;

        element.classList.remove(
            "safe",
            "danger",
            "warning"
        );

        if (
            status.includes("BLOCK") ||
            status.includes("THREAT") ||
            status.includes("ISOLAT")
        ) {

            element.classList.add(
                "danger"
            );

        } else if (
            status.includes("WAIT") ||
            status.includes("ANALYZ") ||
            status.includes("DETECT")
        ) {

            element.classList.add(
                "warning"
            );

        } else {

            element.classList.add(
                "safe"
            );
        }
    }


    // ============================================================
    // USB
    // ============================================================

    function updateUSB(usb) {

        if (!usb) {
            return;
        }

        const connected = Boolean(
            usb.connected
        );

        const score = number(
            usb.anomaly_score
        );


        text(
            "usbDevice",
            connected
                ? usb.device || "USB DEVICE"
                : "NOT CONNECTED"
        );

        text(
            "usbDrive",
            connected
                ? usb.drive || "—"
                : "—"
        );

        text(
            "usbFilesystem",
            connected
                ? usb.filesystem || "—"
                : "—"
        );

        text(
            "usbFiles",
            connected
                ? number(
                    usb.files_scanned
                )
                : 0
        );

        text(
            "usbScan",
            connected
                ? usb.scan || "SCANNING"
                : "WAITING"
        );

        text(
            "usbScore",
            `${score}%`
        );

        text(
            "usbThreatClass",
            connected
                ? usb.threat_class ||
                    "NORMAL USB ACTIVITY"
                : "NO ACTIVE USB THREAT"
        );


        const scoreBar = $(
            "usbScoreBar"
        );

        if (scoreBar) {
            scoreBar.style.width =
                `${Math.min(
                    100,
                    Math.max(0, score)
                )}%`;

            scoreBar.style.background =
                score >= 70
                    ? "var(--red)"
                    : score >= 40
                        ? "var(--yellow)"
                        : "var(--cyan)";
        }


        const badge = $(
            "usbLiveBadge"
        );

        if (badge) {

            badge.innerHTML =
                `<i></i>${safe(
                    connected
                        ? usb.status || "CONNECTED"
                        : "WAITING"
                )}`;

            badge.style.color =
                score >= 70
                    ? "var(--red)"
                    : connected
                        ? "var(--green)"
                        : "var(--yellow)";
        }


        const endpointUsbName = $(
            "endpointUsbName"
        );

        if (endpointUsbName) {
            endpointUsbName.textContent =
                connected
                    ? usb.device || "USB DEVICE"
                    : "No USB connected";
        }


        const pulse = $(
            "usbPulse"
        );

        if (pulse) {

            pulse.style.background =
                score >= 70
                    ? "rgba(255,85,116,0.12)"
                    : connected
                        ? "rgba(85,242,162,0.08)"
                        : "rgba(85,229,255,0.05)";
        }
    }


    // ============================================================
    // WORKFLOW
    // ============================================================

    function updateWorkflow(
        workflow,
        usb
    ) {

        const state =
            workflow || {};

        setWorkflowStep(
            "workflowDevice",
            Boolean(
                state.device_detected
            ),
            usb?.connected
                ? "USB device detected"
                : "Waiting for telemetry"
        );


        setWorkflowStep(
            "workflowAnomaly",
            Boolean(
                state.anomaly_detected
            ),
            usb?.connected
                ? `Score: ${number(
                    usb?.anomaly_score
                )}%`
                : "ML analysis pending"
        );


        setWorkflowStep(
            "workflowClass",
            Boolean(
                state.threat_classified
            ),
            state.threat_classified
                ? usb?.threat_class || "CLASSIFIED"
                : "Classification pending"
        );


        setWorkflowStep(
            "workflowQuarantine",
            Boolean(
                state.device_quarantined
            ),
            state.device_quarantined
                ? "Autonomous response complete"
                : "Response pending"
        );


        setWorkflowStep(
            "workflowReport",
            Boolean(
                state.forensic_report
            ),
            state.forensic_report
                ? "Investigation available"
                : "Investigation pending"
        );
    }


    function setWorkflowStep(
        id,
        active,
        subtitle
    ) {

        const element = $(id);

        if (!element) {
            return;
        }

        element.classList.toggle(
            "active",
            active
        );

        const span =
            element.querySelector(
                "span"
            );

        if (span) {
            span.textContent =
                subtitle;
        }
    }


    // ============================================================
    // ENDPOINT TELEMETRY
    // ============================================================

    function updateEndpointTelemetry(
        telemetry
    ) {

        if (!telemetry) {
            return;
        }

        text(
            "endpointCpu",
            `${number(
                telemetry.cpu
            )}%`
        );

        text(
            "endpointMemory",
            `${number(
                telemetry.memory
            )}%`
        );
    }


    // ============================================================
    // THREATS
    // ============================================================

    async function loadThreats() {

        try {

            const data =
                await getJSON(
                    "/api/threats"
                );

            const threats =
                data.threats || [];

            text(
                "navThreatCount",
                threats.length
            );

            const table = $(
                "threatTable"
            );

            if (!table) {
                return;
            }

            if (!threats.length) {

                table.innerHTML = `
                    <tr>
                        <td colspan="6">
                            NO THREATS DETECTED
                        </td>
                    </tr>
                `;

                return;
            }


            table.innerHTML =
                threats
                    .map(
                        (event) => {

                            const severity =
                                String(
                                    event.severity ||
                                    "LOW"
                                ).toLowerCase();

                            return `
                                <tr>
                                    <td>
                                        ${safe(
                                            formatTime(
                                                event.timestamp
                                            )
                                        )}
                                    </td>

                                    <td>
                                        ${safe(
                                            event.source ||
                                            "UNKNOWN"
                                        )}
                                    </td>

                                    <td>
                                        ${safe(
                                            event.threat_type ||
                                            "UNKNOWN"
                                        )}
                                    </td>

                                    <td>
                                        ${number(
                                            event.anomaly_score ??
                                            event.risk_score
                                        )}%
                                    </td>

                                    <td class="severity-${severity}">
                                        ${safe(
                                            String(
                                                event.severity ||
                                                "LOW"
                                            ).toUpperCase()
                                        )}
                                    </td>

                                    <td class="action-blocked">
                                        ${safe(
                                            event.action ||
                                            "BLOCKED"
                                        )}
                                    </td>
                                </tr>
                            `;
                        }
                    )
                    .join("");

        } catch (error) {

            console.error(
                "Threat loading error:",
                error
            );
        }
    }


    // ============================================================
    // INVESTIGATIONS
    // ============================================================

    async function loadInvestigations() {

        try {

            const data =
                await getJSON(
                    "/api/investigations"
                );

            const records =
                data.investigations || [];

            const container = $(
                "investigationList"
            );

            if (!container) {
                return;
            }

            if (!records.length) {

                container.innerHTML = `
                    <div class="empty-state">
                        NO ACTIVE INVESTIGATIONS
                    </div>
                `;

                return;
            }


            container.innerHTML =
                records
                    .map(
                        (record) => `
                            <div class="investigation-card">

                                <div>
                                    <small>
                                        ${safe(
                                            formatTime(
                                                record.timestamp
                                            )
                                        )}
                                    </small>

                                    <h3>
                                        ${safe(
                                            record.id
                                        )}
                                    </h3>
                                </div>

                                <div>
                                    <small>
                                        INVESTIGATION
                                    </small>

                                    <h3>
                                        ${safe(
                                            record.title ||
                                            "USB ML INVESTIGATION"
                                        )}
                                    </h3>
                                </div>

                                <div>
                                    <small>
                                        STATUS
                                    </small>

                                    <h3>
                                        ${safe(
                                            record.status ||
                                            "AVAILABLE"
                                        )}
                                    </h3>
                                </div>

                                <div
                                    class="investigation-score"
                                >
                                    ${number(
                                        record.anomaly_score
                                    )}%
                                </div>

                            </div>
                        `
                    )
                    .join("");

        } catch (error) {

            console.error(
                "Investigation loading error:",
                error
            );
        }
    }


    // ============================================================
    // NAVIGATION
    // ============================================================

    function setupNavigation() {

        const items =
            document.querySelectorAll(
                ".nav-item"
            );

        items.forEach(
            (item) => {

                item.addEventListener(
                    "click",
                    () => {

                        const page =
                            item.dataset.page;

                        if (!page) {
                            return;
                        }

                        showPage(
                           page
                        );
                    }
                );
            }
        );
    }


    function showPage(page) {

        document
            .querySelectorAll(
                ".nav-item"
            )
            .forEach(
                (item) => {

                    item.classList.toggle(
                        "active",
                        item.dataset.page === page
                    );
                }
            );


        document
            .querySelectorAll(
                ".page-view"
            )
            .forEach(
                (view) => {

                    view.classList.toggle(
                        "active",
                        view.id ===
                        `page-${page}`
                    );
                }
            );


        const names = {
            dashboard:
                "DASHBOARD",

            threats:
                "THREATS",

            endpoints:
                "ENDPOINTS",

            cloud:
                "CLOUD",

            network:
                "NETWORK",

            iot:
                "IOT / SENSORS",

            ot:
                "INDUSTRIAL / OT",

            ai:
                "AI INTELLIGENCE",

            investigations:
                "INVESTIGATIONS",
        };


        text(
            "pageTitle",
            names[page] ||
            page.toUpperCase()
        );


        const headings = {
            dashboard:
                "Autonomous Defense Dashboard",

            threats:
                "Detected Threats",

            endpoints:
                "Protected Endpoints",

            cloud:
                "Cloud Infrastructure",

            network:
                "Network Security",

            iot:
                "IoT / Sensors",

            ot:
                "Industrial / OT",

            ai:
                "AI Intelligence Core",

            investigations:
                "Security Investigations",
        };


        text(
            "pageHeading",
            headings[page] ||
            "IronMind AI"
        );


        if (
            page === "threats"
        ) {
            loadThreats();
        }

        if (
            page === "investigations"
        ) {
            loadInvestigations();
        }
    }


    // ============================================================
    // POLLING
    // ============================================================

    async function refreshStatus() {

        try {

            const state =
                await getJSON(
                    "/api/status"
                );

            updateDashboard(
                state
            );

        } catch (error) {

            console.error(
                "Status error:",
                error
            );
        }
    }


    async function refreshData() {

        await refreshStatus();

        await loadThreats();

        await loadInvestigations();
    }


    // ============================================================
    // INITIALIZATION
    // ============================================================

    function init() {

        setupNavigation();

        refreshData();

        setInterval(
            refreshStatus,
            2500
        );

        setInterval(
            loadThreats,
            5000
        );

        setInterval(
            loadInvestigations,
            5000
        );
    }


    document.addEventListener(
        "DOMContentLoaded",
        init
    );

})();
