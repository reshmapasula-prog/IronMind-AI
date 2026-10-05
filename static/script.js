/* =========================================================
   IRONMIND AI
   AUTONOMOUS CYBER DEFENSE
   LIVE SOC DASHBOARD
========================================================= */


/* =========================================================
   GLOBAL DATA
========================================================= */

let chartValues = [
    25, 35, 30, 45, 40, 55, 48, 65
];

let threatTimer = null;
let endpointTimer = null;
let networkTimer = null;
let cloudTimer = null;


/* =========================================================
   SAFE TEXT UPDATE
========================================================= */

function setText(id, value) {

    const element =
        document.getElementById(id);

    if (element) {
        element.textContent = value;
    }
}


/* =========================================================
   GET LIVE STATUS
========================================================= */

async function getStatus() {

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
                "Server error: " +
                response.status
            );
        }

        const data =
            await response.json();

        updateDashboard(data);

    }

    catch (error) {

        console.error(
            "Live status error:",
            error
        );
    }
}


/* =========================================================
   UPDATE DASHBOARD
========================================================= */

function updateDashboard(data) {

    if (!data) {
        return;
    }


    /* -----------------------------------------------------
       MAIN METRICS
    ----------------------------------------------------- */

    setText(
        "risk",
        data.risk
    );

    setText(
        "aiRisk",
        data.ai_risk
    );

    setText(
        "threats",
        data.threats
    );

    setText(
        "blocked",
        data.blocked
    );


    /* -----------------------------------------------------
       RISK LABEL
    ----------------------------------------------------- */

    const riskLabel =
        document.getElementById(
            "riskLabel"
        );

    if (riskLabel) {

        if (data.risk >= 85) {

            riskLabel.textContent =
                "CRITICAL RISK";

        }

        else if (data.risk >= 70) {

            riskLabel.textContent =
                "HIGH RISK";

        }

        else if (data.risk >= 50) {

            riskLabel.textContent =
                "MEDIUM RISK";

        }

        else if (data.risk >= 30) {

            riskLabel.textContent =
                "ELEVATED RISK";

        }

        else {

            riskLabel.textContent =
                "LOW RISK";
        }
    }


    /* -----------------------------------------------------
       THREAT COUNTS
    ----------------------------------------------------- */

    setText(
        "critical",
        data.critical
    );

    setText(
        "high",
        data.high
    );

    setText(
        "medium",
        data.medium
    );

    setText(
        "low",
        data.low
    );


    /* -----------------------------------------------------
       SYSTEM COUNTS
    ----------------------------------------------------- */

    if (typeof data.endpoints === "number") {

        setText(
            "endpoints",
            data.endpoints.toLocaleString()
        );
    }

    if (typeof data.cloud === "number") {

        setText(
            "cloud",
            data.cloud.toLocaleString()
        );
    }

    if (typeof data.network_devices === "number") {

        setText(
            "networkDevices",
            data.network_devices.toLocaleString()
        );
    }


    /* -----------------------------------------------------
       AI PROCESSING
    ----------------------------------------------------- */

    setText(
        "aiProcessing",
        data.ai_processing + "%"
    );

    setText(
        "aiModuleValue",
        data.ai_processing + "%"
    );

    const aiProgress =
        document.getElementById(
            "aiProgress"
        );

    if (aiProgress) {

        aiProgress.style.width =
            data.ai_processing + "%";
    }
   /* -----------------------------------------------------
       INCIDENT
    ----------------------------------------------------- */

    setText(
        "incident",
        data.incident
    );

    setText(
        "aiStatus",
        data.ai_engine
    );

    setText(
        "endpointStatus",
        data.endpoint
    );

    setText(
        "networkStatus",
        data.network
    );

    setText(
        "iotStatus",
        data.iot_ot
    );


    /* -----------------------------------------------------
       THREATS MODULE
    ----------------------------------------------------- */

    setText(
        "moduleThreats",
        data.threats
    );

    setText(
        "moduleCritical",
        data.critical
    );

    setText(
        "moduleBlocked",
        data.blocked
    );

    setText(
        "moduleRisk",
        data.risk
    );


    /* -----------------------------------------------------
       ENDPOINT MODULE
    ----------------------------------------------------- */

    if (typeof data.endpoints === "number") {

        setText(
            "endpointModuleValue",
            data.endpoints.toLocaleString()
        );
    }

    setText(
        "endpointThreats",
        data.threats
    );

    setText(
        "cpuValue",
        data.cpu + "%"
    );

    setText(
        "memoryValue",
        data.memory + "%"
    );

    setText(
        "usbStatus",
        data.usb_activity
    );


    /* -----------------------------------------------------
       CLOUD
    ----------------------------------------------------- */

    if (typeof data.cloud === "number") {

        setText(
            "cloudModuleValue",
            data.cloud.toLocaleString()
        );
    }

    setText(
        "cloudRisk",
        data.risk
    );


    /* -----------------------------------------------------
       NETWORK
    ----------------------------------------------------- */

    if (typeof data.network_devices === "number") {

        setText(
            "networkModuleValue",
            data.network_devices.toLocaleString()
        );
    }

    setText(
        "networkThreats",
        data.threats
    );

    setText(
        "networkTraffic",
        data.network_traffic + "%"
    );

    setText(
        "networkAI",
        data.ai_processing + "%"
    );


    /* -----------------------------------------------------
       IoT / OT
    ----------------------------------------------------- */

    setText(
        "machineTemperature",
        data.machine_temperature + "°C"
    );

    setText(
        "machineVibration",
        data.machine_vibration
    );

    setText(
        "machineRPM",
        data.machine_rpm
    );

    setText(
        "iotModuleStatus",
        data.iot_ot
    );


    /* -----------------------------------------------------
       AI
    ----------------------------------------------------- */

    setText(
        "aiModuleRisk",
        data.ai_risk
    );


    /* -----------------------------------------------------
       REPORTS
    ----------------------------------------------------- */

    setText(
        "reportEvents",
        data.events.toLocaleString()
    );

    setText(
        "reportBlocked",
        data.blocked
    );

    setText(
        "reportRisk",
        data.risk
    );


    /* -----------------------------------------------------
       CHART
    ----------------------------------------------------- */

    updateChart(
        data.risk
    );


    /* -----------------------------------------------------
       ATTACK VECTORS
    ----------------------------------------------------- */

    updateAttackVectors(
        data.risk
    );
}


/* =========================================================
   THREAT CHART
========================================================= */

function updateChart(risk) {

    chartValues.push(
        risk
    );

    if (chartValues.length > 8) {

        chartValues.shift();
    }

    const points = [];

    const width = 600;
    const height = 180;

    const step =
        width /
        Math.max(
            chartValues.length - 1,
            1
        );

    chartValues.forEach(
        function(value, index) {

            const x =
                index * step;

            const y =
                height -
                (value / 100 * 150) -
                10;

            points.push(
                x + "," + y
            );
        }
    );

    const chart =
        document.getElementById(
            "chartLine"
        );

    if (chart) {

        chart.setAttribute(
            "points",
            points.join(" ")
        );
    }
}


/* =========================================================
   ATTACK VECTORS
========================================================= */

function updateAttackVectors(
    risk
) {

    const malware =
        Math.min(
            95,
            45 + risk
        );

    const phishing =
        Math.min(
            85,
            35 + risk / 2
        );

    const exploit =
        Math.min(
            75,
            25 + risk / 2
        );

    const unauthorized =
        Math.min(
            65,
            20 + risk / 2
        );

    updateBar(
        "malwareBar",
        "malwareValue",
        malware
    );

    updateBar(
        "phishingBar",
        "phishingValue",
        phishing
    );

    updateBar(
        "exploitBar",
        "exploitValue",
        exploit
    );

    updateBar(
        "unauthorizedBar",
        "unauthorizedValue",
        unauthorized
    );
}


function updateBar(
    barId,
    valueId,
    value
) {

    const bar =
        document.getElementById(
            barId
        );

    const text =
        document.getElementById(
            valueId
        );

    if (bar) {

        bar.style.width =
            value + "%";
    }

    if (text) {

        text.textContent =
            value.toFixed(1) + "%";
    }
}


/* =========================================================
   SIDEBAR NAVIGATION
========================================================= */

function setupNavigation() {

    const navItems =
        document.querySelectorAll(
            ".nav-item"
        );

    navItems.forEach(
        function(button) {

            button.addEventListener(
                "click",
                function() {

                    const page =
                        button.getAttribute(
                            "data-page"
                        );

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


/* =========================================================
   SHOW PAGE
========================================================= */

function showPage(
    pageName
) {

    const pages =
        document.querySelectorAll(
            ".page"
        );

    pages.forEach(
        function(page) {

            page.classList.remove(
                "active-page"
            );
        }
    );

    const selected =
        document.getElementById(
            pageName
        );

    if (selected) {

        selected.classList.add(
            "active-page"
        );
    }

    const navItems =
        document.querySelectorAll(
            ".nav-item"
        );

    navItems.forEach(
        function(button) {

            button.classList.remove(
                "active"
            );
        }
    );

    const activeButton =
        document.querySelector(
            '.nav-item[data-page="' +
            pageName +
            '"]'
           );

    if (activeButton) {

        activeButton.classList.add(
            "active"
        );
    }

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


/* =========================================================
   CYBER TEST
========================================================= */

async function runCyberTest() {

    try {

        const response =
            await fetch(
                "/api/cyber-test",
                {
                    cache: "no-store"
                }
            );

        const result =
            await response.json();

        const data =
            result.data ||
            result.state;

        updateDashboard(
            data
        );

        showPage(
            "threats"
        );

    }

    catch (error) {

        console.error(
            "Cyber test error:",
            error
        );
    }
}


/* =========================================================
   USB THREAT TEST
========================================================= */

async function runUSBThreatTest() {

    try {

        const response =
            await fetch(
                "/api/usb-threat-test",
                {
                    method: "POST",
                    cache: "no-store"
                }
            );

        const result =
            await response.json();

        const data =
            result.data ||
            result.state;

        updateDashboard(
            data
        );

        showPage(
            "threats"
        );

        loadThreats();

        showSecurityNotification(
            "CRITICAL THREAT BLOCKED",
            "invoice.exe was blocked and quarantined."
        );

    }

    catch (error) {

        console.error(
            "USB threat test error:",
            error
        );
    }
}


/* =========================================================
   MACHINE TEST
========================================================= */

async function runMachineTest() {

    try {

        const response =
            await fetch(
                "/api/machine-test",
                {
                    cache: "no-store"
                }
            );

        const result =
            await response.json();

        const data =
            result.data ||
            result.state;

        updateDashboard(
            data
        );

        showPage(
            "iot"
        );

    }

    catch (error) {

        console.error(
            "Machine test error:",
            error
        );
    }
}


/* =========================================================
   ENDPOINT TEST
========================================================= */

async function runEndpointTest() {

    try {

        const response =
            await fetch(
                "/api/endpoint-test",
                {
                    method: "POST",
                    cache: "no-store"
                }
            );

        const result =
            await response.json();

        const data =
            result.data ||
            result.state;

        updateDashboard(
            data
        );

        showPage(
            "endpoints"
        );

    }

    catch (error) {

        console.error(
            "Endpoint test error:",
            error
        );
    }
}


/* =========================================================
   NETWORK TEST
========================================================= */

async function runNetworkTest() {

    try {

        const response =
            await fetch(
                "/api/network-test",
                {
                    method: "POST",
                    cache: "no-store"
                }
            );

        const result =
            await response.json();

        const data =
            result.data ||
            result.state;

        updateDashboard(
            data
        );

        showPage(
            "network"
        );

    }

    catch (error) {

        console.error(
            "Network test error:",
            error
        );
    }
}


/* =========================================================
   RESET
========================================================= */

async function resetSystem() {

    try {

        const response =
            await fetch(
                "/api/reset",
                {
                    method: "POST",
                    cache: "no-store"
                }
            );

        const result =
            await response.json();

        const data =
            result.data ||
            result.state;

        updateDashboard(
            data
        );

        showPage(
            "dashboard"
        );

    }

    catch (error) {

        console.error(
            "Reset error:",
            error
        );
    }
}


/* =========================================================
   LOAD THREATS
========================================================= */

async function loadThreats() {

    try {

        const response =
            await fetch(
                "/api/threats",
                {
                    cache: "no-store"
                }
            );

        const result =
            await response.json();

        renderThreatRecords(
            result.threats || []
        );

    }

    catch (error) {

        console.error(
            "Threat loading error:",
            error
        );
    }
}


/* =========================================================
   RENDER THREAT RECORDS
========================================================= */

function renderThreatRecords(
    threats
) {

    const container =
        document.getElementById(
            "investigationThreats"
        );

    if (!container) {
        return;
    }

    if (!threats.length) {

        container.innerHTML = `
            <div class="empty-security-state">
                NO BLOCKED THREATS
            </div>
        `;

        return;
    }

    container.innerHTML =
        threats.map(
            function(threat) {

                return `
                    <div class="im-threat-record">

                        <div class="threat-record-top">

                            <span class="severity critical">
                                ${threat.severity}
                            </span>

                            <strong>
                                ${escapeHTML(
                                    threat.filename
                                )}
                            </strong>

                            <span class="blocked-badge">
                                BLOCKED
                            </span>

                        </div>

                        <div class="threat-record-grid">

                            <div>
                                <small>RISK SCORE</small>
                                <b>
                                    ${threat.risk_score}/100
                                </b>
                            </div>

                            <div>
                                <small>THREAT</small>
                                <b>
                                    ${escapeHTML(
                                        threat.threat_type
                                    )}
                                </b>
                            </div>

                            <div>
                                <small>SOURCE</small>
                                <b>
                                    ${escapeHTML(
                                        threat.source
                                    )}
                                </b>
                            </div>

                            <div>
                                <small>STATUS</small>
                                <b>
                                    QUARANTINED
                                </b>
                            </div>

                        </div>

                        <div class="threat-reason">

                            <span>WHY BLOCKED:</span>

                            ${escapeHTML(
                                threat.reason
                            )}

                        </div>

                        <div class="threat-hash">

                            SHA-256:
                            ${escapeHTML(
                                threat.sha256
                            )}

                        </div>

                        <div class="threat-time">

                            ${escapeHTML(
                                threat.timestamp
                            )}

                        </div>

                    </div>
                `;
            }
        )
        .join("");
}


/* =========================================================
   HTML ESCAPE
========================================================= */

function escapeHTML(
    value
) {

    if (value === null ||
        value === undefined) {

        return "";
    }

    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );
}


/* =========================================================
   SECURITY NOTIFICATION
========================================================= */

function showSecurityNotification(
    title,
    message
) {

    let notification =
        document.getElementById(
            "ironmindSecurityNotification"
        );

    if (!notification) {

        notification =
            document.createElement(
                "div"
            );

        notification.id =
            "ironmindSecurityNotification";

        notification.style.position =
            "fixed";

        notification.style.right =
            "25px";

        notification.style.bottom =
            "25px";

        notification.style.zIndex =
            "99999";

        notification.style.padding =
            "18px 22px";

        notification.style.border =
            "1px solid rgba(255,80,80,.4)";

        notification.style.background =
            "rgba(20,10,20,.96)";

        notification.style.borderRadius =
            "12px";
       notification.style.boxShadow =
            "0 15px 40px rgba(0,0,0,.4)";

        document.body.appendChild(
            notification
        );
    }

    notification.innerHTML = `

        <div style="
            color:#ff5b62;
            font-size:11px;
            font-weight:800;
            letter-spacing:1px;
            margin-bottom:5px;
        ">
            ${escapeHTML(title)}
        </div>

        <div style="
            color:#ffffff;
            font-size:13px;
        ">
            ${escapeHTML(message)}
        </div>
    `;

    setTimeout(
        function() {

            if (notification) {

                notification.remove();
            }

        },
        5000
    );
}


/* =========================================================
   START APPLICATION
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function() {

        setupNavigation();

        getStatus();

        loadThreats();
    }
);


/* =========================================================
   LIVE UPDATE
   EVERY 10 SECONDS
========================================================= */

setInterval(
    function() {

        getStatus();

        loadThreats();

    },
    10000
);


/* =========================================================
   PROFESSIONAL THREAT PAGE FIX
========================================================= */

(function () {

    function getMainContainer() {

        return document.querySelector(
            ".main-content, .content-area, .dashboard-content, main"
        );
    }


    function getSidebar() {

        return document.querySelector(
            ".sidebar, aside, .side-nav, .navigation"
        );
    }


    function getPageTitle(
        name,
        subtitle
    ) {

        return `

            <div class="page-header">

                <div>

                    <div class="section-label">
                        IRONMIND AI • SECURITY OPERATIONS
                    </div>

                    <h1>
                        ${name}
                    </h1>

                    <p>
                        ${subtitle}
                    </p>

                </div>

                <div class="live-indicator">

                    <span class="live-dot"></span>

                    LIVE MONITORING

                </div>

            </div>

        `;
    }


    function statCard(
        title,
        value,
        status
    ) {

        return `

            <div class="im-stat-card">

                <div class="im-stat-title">
                    ${title}
                </div>

                <div class="im-stat-value">
                    ${value}
                </div>

                <div class="im-stat-status">
                    ${status}
                </div>

            </div>

        `;
    }


    /* =====================================================
       THREATS
    ===================================================== */

    function showThreats() {

        const main =
            getMainContainer();

        if (!main) {
            return;
        }

        main.innerHTML = `

            ${getPageTitle(
                "Threat Intelligence",
                "Detection, autonomous response and investigation"
            )}

            <div class="im-stat-grid">

                ${statCard(
                    "ACTIVE THREATS",
                    `<span id="threatActive">0</span>`,
                    "LIVE MONITORING"
                )}

                ${statCard(
                    "CRITICAL",
                    `<span id="threatCritical">0</span>`,
                    "IMMEDIATE ATTENTION"
                )}

                ${statCard(
                    "HIGH RISK",
                    `<span id="threatHigh">0</span>`,
                    "UNDER ANALYSIS"
                )}

                ${statCard(
                    "BLOCKED",
                    `<span id="threatBlocked">0</span>`,
                    "PROTECTION ACTIVE"
                )}

            </div>


            <div class="im-two-column">


                <div class="im-panel">

                    <div class="im-panel-header">

                        <div>

                            <div class="section-label">
                                AUTONOMOUS RESPONSE
                            </div>

                            <h2>
                                Threat Response
                            </h2>

                        </div>

                        <span class="live-badge">
                            AI ACTIVE
                        </span>

                    </div>


                    <div class="response-flow">

                        <div>

                            <span>01</span>

                            Threat Detected

                        </div>

                        <div class="flow-arrow">
                            →
                        </div>

                        <div>

                            <span>02</span>

                            AI Analyzed

                        </div>

                        <div class="flow-arrow">
                            →
                        </div>

                        <div>

                            <span>03</span>

                            Risk Scored

                        </div>

                        <div class="flow-arrow">
                            →
                        </div>

                        <div>

                            <span>04</span>

                            Blocked

                        </div>

                    </div>


                    <div class="protection-status">

                        <span class="live-dot"></span>

                        AUTONOMOUS PROTECTION ACTIVE

                    </div>

                </div>


                <div class="im-panel">

                    <div class="section-label">
                        DEMONSTRATION
                    </div>

                    <h2>
                        USB Threat Simulation
                    </h2>

                    <p style="
                        opacity:.6;
                        font-size:12px;
                        line-height:1.7;
                    ">

                        Simulate a critical executable
                        arriving through removable media.

                    </p>


                    <button
                        onclick="runUSBThreatTest()"
                        style="
                            width:100%;
                            padding:14px;
                            border:0;
                            border-radius:8px;
                            background:#d83d48;
                            color:white;
                            font-weight:800;
                            cursor:pointer;
                            margin-top:12px;
                        "
                    >

                        SIMULATE HIGH-RISK USB FILE

                    </button>

                </div>

            </div>


            <div class="im-panel">

                <div class="im-panel-header">

                    <div>

                        <div class="section-label">
                            FORENSICS
                        </div>

                        <h2>
                            Blocked Threat Investigation
                        </h2>

                    </div>

                    <span class="live-badge">
                        RETAINED
                    </span>

                </div>


                <div id="investigationThreats">

                    Loading investigation records...

                </div>

            </div>

        `;

        loadThreats();

        startThreatUpdates();
    }


    /* =====================================================
       ENDPOINTS
    ===================================================== */

    function showEndpoints() {

        const main =
            getMainContainer();

        if (!main) {
            return;
        }

        main.innerHTML = `

            ${getPageTitle(
                "Endpoint Security",
                "Continuous monitoring and autonomous endpoint protection"
            )}


            <div class="im-stat-grid">

                ${statCard(
                    "ENDPOINTS",
                    `<span id="endpointCount">12</span>`,
                    "MONITORED"
                )}

                ${statCard(
                    "PROTECTED",
                    `<span id="endpointProtected">12</span>`,
                    "AI DEFENSE ACTIVE"
                )}

                ${statCard(
                    "AT RISK",
                    `<span id="endpointRisk">0</span>`,
                    "UNDER ANALYSIS"
                )}

                ${statCard(
                    "BLOCKED",
                    `<span id="endpointIsolated">0</span>`,
                    "AUTOMATED RESPONSE"
                )}

            </div>


            <div class="im-two-column">


                <div class="im-panel">

                    <div class="section-label">
                        LOCAL ENDPOINT
                    </div>

                    <h2>
                        Laptop Security Monitor
                    </h2>


                    <div class="endpoint-details">

                        <div class="endpoint-detail">

                            <span>
                                Platform
                            </span>

                            <strong>
                                ${navigator.platform ||
                                "Windows Endpoint"}
                            </strong>

                        </div>


                        <div class="endpoint-detail">

                            <span>
                                Connection
                            </span>

                            <strong class="online-text">
                                ONLINE
                            </strong>

                        </div>


                        <div class="endpoint-detail">

                            <span>
                                AI Protection
                            </span>

                            <strong class="online-text">
                                ACTIVE
                            </strong>

                        </div>


                        <div class="endpoint-detail">

                            <span>
                                USB Protection
                            </span>

                            <strong class="online-text">
                                ACTIVE
                            </strong>

                        </div>

                    </div>

                </div>


                <div class="im-panel">

                    <div class="section-label">
                        REAL-TIME TELEMETRY
                    </div>

                    <h2>
                        Endpoint Health
                    </h2>


                    <div class="metric-line">

                        <span>
                            CPU Load
                        </span>

                        <b id="endpointCPU">
                            32%
                        </b>

                    </div>

                    <div class="metric-track">

                        <i
                            id="cpuBar"
                            style="width:32%"
                        ></i>

                    </div>


                    <div class="metric-line">

                        <span>
                            Memory
                        </span>

                        <b id="endpointMemory">
                            46%
                        </b>

                    </div>

                    <div class="metric-track">

                        <i
                            id="memoryBar"
                            style="width:46%"
                        ></i>

                    </div>


                    <div class="metric-line">

                        <span>
                            AI Security Score
                        </span>

                        <b id="endpointScore">
                            96%
                        </b>

                    </div>

                    <div class="metric-track">

                        <i
                            id="scoreBar"
                            style="width:96%"
                        ></i>

                    </div>

                </div>

            </div>


            <div class="im-panel">

                <div class="section-label">
                    ENDPOINT SECURITY
                </div>

                <h2>
                    Protection Pipeline
                </h2>


                <div class="response-flow">

                    <div>

                        <span>01</span>

                        Monitor

                    </div>

                    <div class="flow-arrow">
                        →
                    </div>

                    <div>

                        <span>02</span>

                        Detect

                    </div>

                    <div class="flow-arrow">
                        →
                    </div>

                    <div>

                        <span>03</span>

                        Analyze

                    </div>

                    <div class="flow-arrow">
                        →
                    </div>

                    <div>

                        <span>04</span>

                        Respond

                    </div>

                </div>


                <button
                    onclick="runEndpointTest()"
                    style="
                        padding:12px 18px;
                        border:1px solid rgba(80,150,255,.3);
                        border-radius:8px;
                        background:rgba(40,100,255,.1);
                        color:white;
                        cursor:pointer;
                    "
                >

                    RUN ENDPOINT SECURITY TEST

                </button>

            </div>

        `;

        startEndpointUpdates();
    }


    /* =====================================================
       NETWORK
    ===================================================== */

    function showNetwork() {

        const main =
            getMainContainer();

        if (!main) {
            return;
        }

        main.innerHTML = `

            ${getPageTitle(
                "Network Security",
                "Continuous traffic analysis and autonomous network response"
            )}


            <div class="im-stat-grid">

                ${statCard(
                    "NETWORK DEVICES",
                    `<span id="networkDeviceCount">18</span>`,
                    "MONITORED"
                )}

                ${statCard(
                    "TRAFFIC",
                    `<span id="networkTrafficPage">38%</span>`,
                    "ANALYZING"
                )}

                ${statCard(
                    "THREATS",
                    `<span id="networkThreatPage">0</span>`,
                    "DETECTED"
                )}

                ${statCard(
                    "AI ANALYSIS",
                    `<span id="networkAIPage">72%</span>`,
                    "ACTIVE"
                )}

            </div>


            <div class="im-two-column">


                <div class="im-panel">

                    <div class="section-label">
                        NETWORK TELEMETRY
                    </div>

                    <h2>
                        Live Traffic Analysis
                    </h2>


                    <div class="metric-line">

                        <span>
                            Network Traffic
                        </span>

                        <b id="networkTrafficMeter">
                            38%
                        </b>

                    </div>

                    <div class="metric-track">

                        <i
                            id="networkTrafficBar"
                            style="width:38%"
                        ></i>

                    </div>


                    <div class="metric-line">

                        <span>
                            AI Analysis
                        </span>

                        <b id="networkAI">
                            72%
                        </b>

                    </div>

                    <div class="metric-track">

                        <i
                            id="networkAIBar"
                            style="width:72%"
                        ></i>

                    </div>

                </div>


                <div class="im-panel">

                    <div class="section-label">
                        NETWORK RESPONSE
                    </div>

                    <h2>
                        Autonomous Protection
                    </h2>


                    <div class="endpoint-detail">

                        <span>
                            Network Status
                        </span>

                        <strong
                            id="networkPageStatus"
                            class="online-text"
                        >
                            MONITORING
                        </strong>

                    </div>


                    <br>


                    <button
                        onclick="runNetworkTest()"
                        style="
                            width:100%;
                            padding:14px;
                            border:0;
                            border-radius:8px;
                            background:#286cff;
                            color:white;
                            font-weight:800;
                            cursor:pointer;
                        "
                    >

                        RUN NETWORK SECURITY TEST

                    </button>

                </div>

            </div>


            <div class="im-panel">

                <div class="section-label">
                    SECURITY MODEL
                </div>

                <h2>
                    Network Defense Flow
                </h2>


                <div class="response-flow">

                    <div>

                        <span>01</span>

                        Traffic

                    </div>

                    <div class="flow-arrow">
                        →
                    </div>

                    <div>

                        <span>02</span>

                        Analyze

                    </div>

                    <div class="flow-arrow">
                        →
                    </div>

                    <div>

                        <span>03</span>

                        Risk Score

                    </div>

                    <div class="flow-arrow">
                        →
                    </div>

                    <div>

                        <span>04</span>

                        Block / Monitor

                    </div>

                </div>

            </div>

        `;

        startNetworkUpdates();
    }


    /* =====================================================
       CLOUD
    ===================================================== */

    function showCloud() {

        const main =
            getMainContainer();

        if (!main) {
            return;
        }

        main.innerHTML = `

            ${getPageTitle(
                "Cloud Security",
                "AI-powered cloud infrastructure monitoring"
            )}
            <div class="im-stat-grid">

                ${statCard(
                    "CLOUD SYSTEMS",
                    `<span id="cloudSystems">8</span>`,
                    "SECURE"
                )}

                ${statCard(
                    "PROTECTED",
                    `<span id="cloudProtected">8</span>`,
                    "AI DEFENSE ACTIVE"
                )}

                ${statCard(
                    "CLOUD EVENTS",
                    `<span id="cloudEvents">0</span>`,
                    "MONITORED"
                )}

                ${statCard(
                    "RISK SCORE",
                    `<span id="cloudRisk">18</span>`,
                    "LOW RISK"
                )}

            </div>


            <div class="im-panel">

                <div class="section-label">
                    CLOUD SECURITY
                </div>

                <h2>
                    Infrastructure Protection
                </h2>


                <div class="cloud-service">

                    <span class="service-dot"></span>

                    <div>

                        <strong>
                            Cloud Storage
                        </strong>

                        <small>
                            Data protection active
                        </small>

                    </div>

                    <b>
                        SECURE
                    </b>

                </div>


                <div class="cloud-service">

                    <span class="service-dot"></span>

                    <div>

                        <strong>
                            Application Services
                        </strong>

                        <small>
                            Runtime monitoring
                        </small>

                    </div>

                    <b>
                        SECURE
                    </b>

                </div>


                <div class="cloud-service">

                    <span class="service-dot"></span>

                    <div>

                        <strong>
                            Identity & Access
                        </strong>

                        <small>
                            Authentication monitoring
                        </small>

                    </div>

                    <b>
                        SECURE
                    </b>

                </div>

            </div>

        `;

        startCloudUpdates();
    }


    /* =====================================================
       THREAT LIVE UPDATE
    ===================================================== */

    function startThreatUpdates() {

        clearInterval(
            threatTimer
        );

        async function update() {

            try {

                const response =
                    await fetch(
                        "/api/status",
                        {
                            cache:
                                "no-store"
                        }
                    );

                const data =
                    await response.json();

                const active =
                    document.getElementById(
                        "threatActive"
                    );

                if (!active) {

                    clearInterval(
                        threatTimer
                    );
                   return;
                }

                setText(
                    "threatActive",
                    data.threats
                );

                setText(
                    "threatCritical",
                    data.critical
                );

                setText(
                    "threatHigh",
                    data.high
                );

                setText(
                    "threatBlocked",
                    data.blocked
                );

            }

            catch (error) {

                console.error(
                    error
                );
            }
        }

        update();

        threatTimer =
            setInterval(
                update,
                10000
            );
    }


    /* =====================================================
       ENDPOINT LIVE UPDATE
    ===================================================== */

    function startEndpointUpdates() {

        clearInterval(
            endpointTimer
        );

        async function update() {

            const cpu =
                document.getElementById(
                    "endpointCPU"
                );

            if (!cpu) {

                clearInterval(
                    endpointTimer
                );

                return;
            }

            try {

                const response =
                    await fetch(
                        "/api/status",
                        {
                            cache:
                                "no-store"
                        }
                    );

                const data =
                    await response.json();

                setText(
                    "endpointCPU",
                    data.cpu + "%"
                );

                setText(
                    "endpointMemory",
                    data.memory + "%"
                );

                const cpuBar =
                    document.getElementById(
                        "cpuBar"
                    );

                const memoryBar =
                    document.getElementById(
                        "memoryBar"
                    );

                if (cpuBar) {

                    cpuBar.style.width =
                        data.cpu + "%";
                }

                if (memoryBar) {

                    memoryBar.style.width =
                        data.memory + "%";
                }

                setText(
                    "endpointRisk",
                    data.threats
                );

            }

            catch (error) {

                console.error(
                    error
                );
            }
        }

        update();

        endpointTimer =
            setInterval(
                update,
                10000
            );
    }


    /* =====================================================
       NETWORK LIVE UPDATE
    ===================================================== */

    function startNetworkUpdates() {

        clearInterval(
            networkTimer
        );

        async function update() {

            const traffic =
                document.getElementById(
                    "networkTrafficMeter"
                );

            if (!traffic) {

                clearInterval(
                    networkTimer
                );

                return;
            }

            try {

                const response =
                    await fetch(
                        "/api/status",
                        {
                            cache:
                                "no-store"
                        }
                    );

                const data =
                    await response.json();

                setText(
                    "networkDeviceCount",
                    data.network_devices
                );

                setText(
                    "networkTrafficPage",
                    data.network_traffic + "%"
                );

                setText(
                    "networkTrafficMeter",
                    data.network_traffic + "%"
                );

                setText(
                    "networkThreatPage",
                    data.threats
                );

                setText(
                    "networkAIPage",
                    data.ai_processing + "%"
                );

                setText(
                    "networkAI",
                    data.ai_processing + "%"
                );

                const trafficBar =
                    document.getElementById(
                        "networkTrafficBar"
                    );

                const aiBar =
                    document.getElementById(
                        "networkAIBar"
                    );

                if (trafficBar) {

                    trafficBar.style.width =
                        data.network_traffic + "%";
                }

                if (aiBar) {

                    aiBar.style.width =
                        data.ai_processing + "%";
                }

            }

            catch (error) {

                console.error(
                    error
                );
            }
        }

        update();

        networkTimer =
            setInterval(
                update,
                10000
            );
    }


    /* =====================================================
       CLOUD LIVE UPDATE
    ===================================================== */

    function startCloudUpdates() {

        clearInterval(
            cloudTimer
        );

        async function update() {

            const systems =
                document.getElementById(
                    "cloudSystems"
                );

            if (!systems) {

                clearInterval(
                    cloudTimer
                );

                return;
            }

            try {

                const response =
                    await fetch(
                        "/api/status",
                        {
                            cache:
                                "no-store"
                        }
                    );

                const data =
                    await response.json();

                setText(
                    "cloudSystems",
                    data.cloud
                );

                setText(
                    "cloudProtected",
                    data.cloud
                );

                setText(
                    "cloudEvents",
                    data.events
                );

                setText(
                    "cloudRisk",
                    data.risk
                );

            }

            catch (error) {

                console.error(
                    error
                );
            }
        }

        update();

        cloudTimer =
            setInterval(
                update,
                10000
            );
    }


    /* =====================================================
       SIDEBAR HANDLER
    ===================================================== */

    document.addEventListener(
        "click",
        function(event) {

            const sidebar =
                getSidebar();

            if (!sidebar ||
                !sidebar.contains(
                    event.target
                )) {

                return;
            }

            const item =
                event.target.closest(
                    "a, button, .nav-item, .menu-item, .sidebar-item"
                );

            if (!item ||
                !sidebar.contains(item)) {

                return;
            }

            const text =
                item.textContent
                    .trim()
                    .replace(
                        /\s+/g,
                        " "
                    )
                    .toLowerCase();


            if (
                text.includes(
                    "threat"
                )
            ) {

                event.preventDefault();

                event.stopPropagation();

                showThreats();

                setActiveSidebar(
                    item
                );

                return;
            }


            if (
                text.includes(
                    "endpoint"
                )
            ) {

                event.preventDefault();

                event.stopPropagation();

                showEndpoints();

                setActiveSidebar(
                    item
                );

                return;
            }


            if (
                text === "cloud" ||
                text.includes("cloud")
            ) {

                event.preventDefault();

                event.stopPropagation();

                showCloud();

                setActiveSidebar(
                    item
                );

                return;
            }


            if (
                text.includes(
                    "network"
                )
            ) {

                event.preventDefault();

                event.stopPropagation();

                showNetwork();

                setActiveSidebar(
                    item
);

                return;
            }

        },
        true
    );


    /* =====================================================
       ACTIVE SIDEBAR
    ===================================================== */

    function setActiveSidebar(
        activeItem
    ) {

        const sidebar =
            getSidebar();

        if (!sidebar) {
            return;
        }

        sidebar.querySelectorAll(
            "a, button, .nav-item, .menu-item, .sidebar-item"
        )
        .forEach(
            function(item) {

                item.classList.remove(
                    "active",
                    "selected",
                    "current"
                );
            }
        );

        activeItem.classList.add(
            "active"
        );

        activeItem.classList.add(
            "selected"
        );
    }


    /* =====================================================
       PROFESSIONAL STYLES
    ===================================================== */

    const style =
        document.createElement(
            "style"
        );

    style.textContent = `

        .page-header {
            display:flex;
            justify-content:space-between;
            align-items:center;
            margin-bottom:28px;
            gap:20px;
        }

        .page-header h1 {
            margin:5px 0;
            font-size:32px;
        }

        .page-header p {
            margin:0;
            opacity:.65;
        }

        .section-label {
            color:#55aaff;
            font-size:11px;
            letter-spacing:1.5px;
            font-weight:700;
        }

        .live-indicator {
            font-size:11px;
            color:#48e6a1;
            border:1px solid rgba(72,230,161,.25);
            padding:10px 15px;
            border-radius:20px;
            white-space:nowrap;
        }

        .live-dot {
            width:7px;
            height:7px;
            display:inline-block;
            border-radius:50%;
            background:#48e6a1;
            box-shadow:0 0 10px #48e6a1;
            margin-right:6px;
        }

        .im-stat-grid {
            display:grid;
            grid-template-columns:
                repeat(4,1fr);
            gap:16px;
            margin-bottom:18px;
        }

        .im-stat-card,
        .im-panel {

            background:
                rgba(11,19,38,.78);

            border:
                1px solid
                rgba(100,150,220,.16);

            border-radius:12px;

            padding:20px;

            box-shadow:
                0 10px 35px
                rgba(0,0,0,.16);
        }

        .im-stat-title {
            font-size:11px;
            letter-spacing:1.2px;
            opacity:.6;
        }

        .im-stat-value {
            font-size:30px;
            font-weight:700;
            margin:8px 0;
        }

        .im-stat-status {
            color:#45e0a0;
            font-size:11px;
            font-weight:700;
        }

        .im-two-column {

            display:grid;

            grid-template-columns:
                1.35fr 1fr;

            gap:18px;

            margin-bottom:18px;
        }

        .im-panel h2 {

            margin:
                5px 0 20px;

            font-size:20px;
        }

        .im-panel-header {

            display:flex;

            justify-content:
                space-between;

            align-items:center;
        }

        .live-badge {

            color:#48e6a1;

            border:
                1px solid
                rgba(72,230,161,.25);

            padding:5px 9px;

            border-radius:15px;

            font-size:9px;
        }

        .endpoint-details {

            display:grid;

            grid-template-columns:
                1fr 1fr;

            gap:15px;
        }

        .endpoint-detail {

            padding:15px;

            background:
                rgba(255,255,255,.025);

            border-radius:8px;
        }

        .endpoint-detail span {

            display:block;

            font-size:10px;

            opacity:.5;

            margin-bottom:6px;
        }

        .endpoint-detail strong {

            font-size:13px;
        }

        .online-text,
        .secure-text {

            color:#48e6a1 !important;
        }

        .metric-line {

            display:flex;

            justify-content:
                space-between;

            margin-top:18px;

            font-size:12px;
        }

        .metric-track {

            height:7px;

            border-radius:10px;

            background:
                rgba(255,255,255,.07);

            overflow:hidden;

            margin-top:7px;
        }

        .metric-track i {

            display:block;

            height:100%;

            background:#348cff;

            border-radius:inherit;

            transition:
                width .8s ease;
        }

        .response-flow {

            display:flex;

            align-items:center;

            justify-content:
                space-between;

            gap:10px;

            margin:25px 0;
        }

        .response-flow div:not(.flow-arrow) {

            padding:14px;

            background:
                rgba(40,120,255,.08);

            border:
                1px solid
                rgba(80,150,255,.15);

            border-radius:8px;

            font-size:11px;
        }

        .response-flow span {

            display:block;

            color:#55aaff;

            font-size:9px;

            margin-bottom:5px;
        }

        .flow-arrow {

            opacity:.4;
        }

        .protection-status {

            color:#48e6a1;

            font-size:11px;

            font-weight:700;
        }

        .cloud-service {

            display:flex;

            align-items:center;

            gap:15px;

            padding:15px 0;

            border-bottom:
                1px solid
                rgba(255,255,255,.06);
        }

        .cloud-service div {

            flex:1;
        }

        .cloud-service small {

            display:block;

            opacity:.5;

            margin-top:4px;
        }

        .service-dot {

            width:9px;

            height:9px;

            border-radius:50%;

            background:#48e6a1;

            box-shadow:
                0 0 9px
                rgba(72,230,161,.7);
        }

        .im-threat-record {

            padding:18px;

            margin-top:12px;

            border:
                1px solid
                rgba(255,80,80,.15);

            border-radius:10px;

            background:
                rgba(255,50,60,.035);
        }

        .threat-record-top {

            display:flex;

            align-items:center;

            gap:12px;

            margin-bottom:18px;
        }

        .threat-record-top strong {

            flex:1;

            font-size:14px;
        }

        .blocked-badge {

            color:#ff626b;

            border:
                1px solid
                rgba(255,80,80,.3);

            padding:5px 9px;

            border-radius:12px;

            font-size:9px;

            font-weight:800;
        }

        .threat-record-grid {

            display:grid;

            grid-template-columns:
                repeat(4,1fr);

            gap:10px;
        }

        .threat-record-grid div {

            padding:12px;

            background:
                rgba(255,255,255,.025);

            border-radius:7px;
        }

        .threat-record-grid small {

            display:block;

            opacity:.45;

            font-size:9px;

            margin-bottom:5px;
        }

        .threat-record-grid b {

            font-size:11px;
        }

        .threat-reason {

            margin-top:14px;

            padding:12px;

            border-left:
                2px solid
                #ff5b62;

            background:
                rgba(255,80,80,.04);

            font-size:11px;

            line-height:1.6;
        }

        .threat-reason span {

            color:#ff666d;

            font-weight:800;
        }

        .threat-hash {

            margin-top:12px;

            font-family:
                monospace;

            font-size:9px;

            opacity:.45;

            word-break:break-all;
        }

        .threat-time {

            margin-top:8px;

            font-size:9px;

            opacity:.4;
        }
        .empty-security-state {

            padding:30px;

            text-align:center;

            opacity:.45;

            font-size:11px;

            letter-spacing:1px;
        }

        .critical {

            color:#ff5555;
        }

        @media(max-width:900px) {

            .im-stat-grid {

                grid-template-columns:
                    repeat(2,1fr);
            }

            .im-two-column {

                grid-template-columns:
                    1fr;
            }

            .threat-record-grid {

                grid-template-columns:
                    repeat(2,1fr);
            }

        }

        @media(max-width:600px) {

            .im-stat-grid {

                grid-template-columns:
                    1fr;
            }

            .endpoint-details {

                grid-template-columns:
                    1fr;
            }

            .response-flow {

                flex-direction:
                    column;
            }

            .flow-arrow {

                transform:
                    rotate(90deg);
            }

            .threat-record-grid {

                grid-template-columns:
                    1fr;
            }

        }

    `;

    document.head.appendChild(
        style
    );

})();
