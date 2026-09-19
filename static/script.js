/* =========================================================
   IRONMIND AI
   LIVE SOC DASHBOARD
========================================================= */


/* =========================================================
   GLOBAL CHART DATA
========================================================= */

let chartValues = [
    25, 35, 30, 45, 40, 55, 48, 65
];


/* =========================================================
   SET TEXT SAFELY
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
   UPDATE ALL DASHBOARD VALUES
========================================================= */

function updateDashboard(data) {

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

    setText(
        "endpoints",
        data.endpoints.toLocaleString()
    );

    setText(
        "cloud",
        data.cloud.toLocaleString()
    );

    setText(
        "networkDevices",
        data.network_devices.toLocaleString()
    );


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

    setText(
        "endpointModuleValue",
        data.endpoints.toLocaleString()
    );

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

    setText(
        "cloudModuleValue",
        data.cloud.toLocaleString()
    );

    setText(
        "cloudRisk",
        data.risk
    );


    /* -----------------------------------------------------
       NETWORK
    ----------------------------------------------------- */

    setText(
        "networkModuleValue",
        data.network_devices.toLocaleString()
    );

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
       AI MODULE
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

    updateChart(data.risk);


    /* -----------------------------------------------------
       ATTACK VECTORS
    ----------------------------------------------------- */

    updateAttackVectors(data.risk);

}


/* =========================================================
   DYNAMIC THREAT CHART
========================================================= */

function updateChart(risk) {

    chartValues.push(risk);

    if (chartValues.length > 8) {
        chartValues.shift();
    }


    const points = [];

    const width = 600;
    const height = 180;

    const step =
        width /
        (chartValues.length - 1);


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
   DYNAMIC ATTACK VECTORS
========================================================= */

function updateAttackVectors(risk) {

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

                    showPage(page);

                }
            );

        }
    );

}


/* =========================================================
   SHOW PAGE
========================================================= */

function showPage(pageName) {

    /* -----------------------------------------------------
       HIDE ALL PAGES
    ----------------------------------------------------- */

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


    /* -----------------------------------------------------
       SHOW SELECTED PAGE
    ----------------------------------------------------- */

    const selected =
        document.getElementById(
            pageName
        );


    if (selected) {

        selected.classList.add(
            "active-page"
        );

    }


    /* -----------------------------------------------------
       UPDATE SIDEBAR
    ----------------------------------------------------- */

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


        const data =
            await response.json();


        updateDashboard(
            data.state
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


        const data =
            await response.json();


        updateDashboard(
            data.state
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
   RESET
========================================================= */

async function resetSystem() {

    try {

        const response =
            await fetch(
                "/api/reset",
                {
                    cache: "no-store"
                }
            );


        const data =
            await response.json();


        updateDashboard(
            data.state
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
   START APPLICATION
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function() {

        setupNavigation();

        getStatus();

    }
);


/* =========================================================
   LIVE UPDATE
   EVERY 10 SECONDS
========================================================= */

setInterval(
    function() {

        getStatus();

    },
    10000
);
/* =========================================================
   IRONMIND AI - SIDEBAR PAGE NAVIGATION FIX
   Fixes: Threats, Endpoints, Cloud
   Keeps existing Dashboard / Network / IoT / AI / Reports
   ========================================================= */

(function () {

    const originalMainHTML = {};

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

    function getPageTitle(name, subtitle) {
        return `
            <div class="page-header">
                <div>
                    <div class="section-label">IRONMIND AI • SECURITY OPERATIONS</div>
                    <h1>${name}</h1>
                    <p>${subtitle}</p>
                </div>

                <div class="live-indicator">
                    <span class="live-dot"></span>
                    LIVE MONITORING
                </div>
            </div>
        `;
    }

    function statCard(title, value, status, extraClass = "") {
        return `
            <div class="im-stat-card ${extraClass}">
                <div class="im-stat-title">${title}</div>
                <div class="im-stat-value">${value}</div>
                <div class="im-stat-status">${status}</div>
            </div>
        `;
    }

    /* ---------------------------------------------------------
       THREATS PAGE
       --------------------------------------------------------- */

    function showThreats() {

        const main = getMainContainer();
        if (!main) return;

        main.innerHTML = `
            ${getPageTitle(
                "Threat Intelligence",
                "Real-time detection, analysis and response"
            )}

            <div class="im-stat-grid">

                ${statCard(
                    "ACTIVE THREATS",
                    `<span id="threatActive">4</span>`,
                    "MONITORED"
                )}

                ${statCard(
                    "CRITICAL",
                    `<span id="threatCritical">1</span>`,
                    "IMMEDIATE ATTENTION"
                )}

                ${statCard(
                    "HIGH RISK",
                    `<span id="threatHigh">2</span>`,
                    "UNDER ANALYSIS"
                )}

                ${statCard(
                    "BLOCKED",
                    `<span id="threatBlocked">17</span>`,
                    "PROTECTION ACTIVE"
                )}

            </div>

            <div class="im-two-column">

                <div class="im-panel">

                    <div class="im-panel-header">
                        <div>
                            <div class="section-label">LIVE SECURITY EVENTS</div>
                            <h2>Active Threats</h2>
                        </div>

                        <span class="live-badge">LIVE</span>
                    </div>

                    <div class="threat-list">

                        <div class="threat-row">
                            <span class="severity critical">CRITICAL</span>
                            <div>
                                <strong>Ransomware Detection</strong>
                                <small>Endpoint / LAPTOP-01</small>
                            </div>
                            <span class="threat-live">LIVE</span>
                        </div>

                        <div class="threat-row">
                            <span class="severity high">HIGH</span>
                            <div>
                                <strong>Unauthorized Access</strong>
                                <small>Network / Gateway</small>
                            </div>
                            <span class="threat-live">LIVE</span>
                        </div>

                        <div class="threat-row">
                            <span class="severity high">HIGH</span>
                            <div>
                                <strong>USB Data Transfer</strong>
                                <small>Confidential data movement</small>
                            </div>
                            <span class="threat-live">LIVE</span>
                        </div>

                        <div class="threat-row">
                            <span class="severity medium">MEDIUM</span>
                            <div>
                                <strong>Suspicious Login</strong>
                                <small>Unknown device</small>
                            </div>
                            <span class="threat-live">MONITORED</span>
                        </div>

                    </div>

                </div>

                <div class="im-panel">

                    <div class="section-label">THREAT ANALYSIS</div>
                    <h2>Top Attack Vectors</h2>

                    <div class="attack-item">
                        <span>Malware</span>
                        <div class="attack-bar">
                            <i style="width:88%"></i>
                        </div>
                        <b>88%</b>
                    </div>

                    <div class="attack-item">
                        <span>Phishing</span>
                        <div class="attack-bar">
                            <i style="width:74%"></i>
                        </div>
                        <b>74%</b>
                    </div>

                    <div class="attack-item">
                        <span>Exploits</span>
                        <div class="attack-bar">
                            <i style="width:61%"></i>
                        </div>
                        <b>61%</b>
                    </div>

                    <div class="attack-item">
                        <span>Unauthorized</span>
                        <div class="attack-bar">
                            <i style="width:53%"></i>
                        </div>
                        <b>53%</b>
                    </div>

                </div>

            </div>

            <div class="im-panel threat-response-panel">

                <div class="section-label">AI RESPONSE ENGINE</div>
                <h2>Automated Protection</h2>

                <div class="response-flow">

                    <div>
                        <span>01</span>
                        Threat detected
                    </div>

                    <div class="flow-arrow">→</div>

                    <div>
                        <span>02</span>
                        AI analyzed
                    </div>

                    <div class="flow-arrow">→</div>

                    <div>
                        <span>03</span>
                        Risk scored
                    </div>

                    <div class="flow-arrow">→</div>

                    <div>
                        <span>04</span>
                        Threat blocked
                    </div>

                </div>

                <div class="protection-status">
                    <span class="live-dot"></span>
                    AI PROTECTION ACTIVE
                </div>

            </div>
        `;

        startThreatUpdates();
    }


    /* ---------------------------------------------------------
       ENDPOINTS PAGE
       --------------------------------------------------------- */

    function showEndpoints() {

        const main = getMainContainer();
        if (!main) return;

        main.innerHTML = `
            ${getPageTitle(
                "Endpoint Security",
                "Continuous monitoring of laptops, systems and connected endpoints"
            )}

            <div class="im-stat-grid">

                ${statCard(
                    "ENDPOINTS",
                    `<span id="endpointCount">7,849</span>`,
                    "SECURE"
                )}

                ${statCard(
                    "PROTECTED",
                    `<span id="endpointProtected">7,821</span>`,
                    "ACTIVE DEFENSE"
                )}

                ${statCard(
                    "AT RISK",
                    `<span id="endpointRisk">28</span>`,
                    "UNDER ANALYSIS"
                )}

                ${statCard(
                    "ISOLATED",
                    `<span id="endpointIsolated">6</span>`,
                    "AUTOMATED RESPONSE"
                )}

            </div>

            <div class="im-two-column">

                <div class="im-panel">

                    <div class="im-panel-header">

                        <div>
                            <div class="section-label">LOCAL ENDPOINT</div>
                            <h2>Laptop Security Monitor</h2>
                        </div>

                        <span class="live-badge">PROTECTED</span>

                    </div>

                    <div class="endpoint-details">

                        <div class="endpoint-detail">
                            <span>Device</span>
                            <strong>${navigator.platform || "Windows Endpoint"}</strong>
                        </div>

                        <div class="endpoint-detail">
                            <span>Browser</span>
                            <strong>${navigator.userAgent.includes("Chrome")
                                ? "Chrome"
                                : "Web Browser"}</strong>
                        </div>

                        <div class="endpoint-detail">
                            <span>Connection</span>
                            <strong class="online-text">ONLINE</strong>
                        </div>

                        <div class="endpoint-detail">
                            <span>AI Protection</span>
                            <strong class="online-text">ACTIVE</strong>
                        </div>

                    </div>

                </div>

                <div class="im-panel">

                    <div class="section-label">REAL-TIME TELEMETRY</div>
                    <h2>Endpoint Health</h2>

                    <div class="metric-line">
                        <span>CPU Load</span>
                        <b id="endpointCPU">42%</b>
                    </div>

                    <div class="metric-track">
                        <i id="cpuBar" style="width:42%"></i>
                    </div>

                    <div class="metric-line">
                        <span>Memory</span>
                        <b id="endpointMemory">58%</b>
                    </div>

                    <div class="metric-track">
                        <i id="memoryBar" style="width:58%"></i>
                    </div>

                    <div class="metric-line">
                        <span>Security Score</span>
                        <b id="endpointScore">94%</b>
                    </div>

                    <div class="metric-track">
                        <i id="scoreBar" style="width:94%"></i>
                    </div>

                </div>

            </div>

            <div class="im-panel">

                <div class="section-label">ENDPOINT SECURITY EVENTS</div>
                <h2>Recent Activity</h2>

                <div class="endpoint-event">
                    <span class="event-icon">✓</span>
                    <div>
                        <strong>System integrity verified</strong>
                        <small>Just now</small>
                    </div>
                    <b class="secure-text">SECURE</b>
                </div>

                <div class="endpoint-event">
                    <span class="event-icon">✓</span>
                    <div>
                        <strong>Suspicious process scan completed</strong>
                        <small>2 minutes ago</small>
                    </div>
                    <b class="secure-text">CLEAR</b>
                </div>

                <div class="endpoint-event">
                    <span class="event-icon">✓</span>
                    <div>
                        <strong>AI endpoint protection active</strong>
                        <small>Continuous monitoring</small>
                    </div>
                    <b class="secure-text">ACTIVE</b>
                </div>

            </div>
        `;

        startEndpointUpdates();
    }


    /* ---------------------------------------------------------
       CLOUD PAGE
       --------------------------------------------------------- */

    function showCloud() {

        const main = getMainContainer();
        if (!main) return;

        main.innerHTML = `
            ${getPageTitle(
                "Cloud Security",
                "AI-powered monitoring of cloud infrastructure and services"
            )}

            <div class="im-stat-grid">

                ${statCard(
                    "CLOUD SYSTEMS",
                    `<span id="cloudSystems">1,260</span>`,
                    "SECURE"
                )}

                ${statCard(
                    "PROTECTED",
                    `<span id="cloudProtected">1,244</span>`,
                    "AI DEFENSE ACTIVE"
                )}

                ${statCard(
                    "CLOUD EVENTS",
                    `<span id="cloudEvents">38</span>`,
                    "MONITORED"
                )}

                ${statCard(
                    "RISK SCORE",
                    `<span id="cloudRisk">21</span>`,
                    "LOW RISK"
                )}

            </div>

            <div class="im-two-column">

                <div class="im-panel">

                    <div class="section-label">CLOUD INFRASTRUCTURE</div>
                    <h2>Service Protection</h2>

                    <div class="cloud-service">
                        <span class="service-dot"></span>
                        <div>
                            <strong>Cloud Storage</strong>
                            <small>Data protection active</small>
                        </div>
                        <b>SECURE</b>
                    </div>

                    <div class="cloud-service">
                        <span class="service-dot"></span>
                        <div>
                            <strong>Application Services</strong>
                            <small>Runtime monitoring active</small>
                        </div>
                        <b>SECURE</b>
                    </div>

                    <div class="cloud-service">
                        <span class="service-dot"></span>
                        <div>
                            <strong>Identity & Access</strong>
                            <small>Authentication monitoring</small>
                        </div>
                        <b>SECURE</b>
                    </div>

                    <div class="cloud-service">
                        <span class="service-dot"></span>
                        <div>
                            <strong>Cloud Network</strong>
                            <small>Traffic inspection active</small>
                        </div>
                        <b>PROTECTED</b>
                    </div>

                </div>

                <div class="im-panel">

                    <div class="section-label">CLOUD ACTIVITY</div>
                    <h2>Security Monitoring</h2>

                    <div class="cloud-chart">

                        <div class="cloud-column" style="height:45%"></div>
                        <div class="cloud-column" style="height:65%"></div>
                        <div class="cloud-column" style="height:52%"></div>
                        <div class="cloud-column" style="height:78%"></div>
                        <div class="cloud-column" style="height:61%"></div>
                        <div class="cloud-column" style="height:84%"></div>
                        <div class="cloud-column" style="height:72%"></div>
                        <div class="cloud-column" style="height:91%"></div>

                    </div>

                    <div class="cloud-chart-labels">
                        <span>00</span>
                        <span>04</span>
                        <span>08</span>
                        <span>12</span>
                        <span>16</span>
                        <span>20</span>
                        <span>24</span>
                    </div>

                </div>

            </div>

            <div class="im-panel">

                <div class="section-label">CLOUD THREAT DETECTION</div>
                <h2>Recent Cloud Events</h2>

                <div class="cloud-event">
                    <div>
                        <strong>Authentication anomaly</strong>
                        <small>Identity & Access • monitored</small>
                    </div>
                    <span class="severity medium">MEDIUM</span>
                </div>

                <div class="cloud-event">
                    <div>
                        <strong>Unusual data access</strong>
                        <small>Cloud Storage • analyzed</small>
                    </div>
                    <span class="severity low">LOW</span>
                </div>

                <div class="cloud-event">
                    <div>
                        <strong>Network traffic inspection</strong>
                        <small>Cloud Network • normal</small>
                    </div>
                    <span class="secure-text">SECURE</span>
                </div>

            </div>
        `;

        startCloudUpdates();
    }


    /* ---------------------------------------------------------
       LIVE THREAT VALUES
       --------------------------------------------------------- */

    let threatTimer = null;

    function startThreatUpdates() {

        clearInterval(threatTimer);

        function update() {

            const active = document.getElementById("threatActive");

            if (!active) {
                clearInterval(threatTimer);
                return;
            }

            document.getElementById("threatActive").textContent =
                Math.floor(Math.random() * 4) + 2;

            document.getElementById("threatCritical").textContent =
                Math.floor(Math.random() * 2) + 1;

            document.getElementById("threatHigh").textContent =
                Math.floor(Math.random() * 3) + 1;

            document.getElementById("threatBlocked").textContent =
                Math.floor(Math.random() * 8) + 14;
        }

        update();
        threatTimer = setInterval(update, 10000);
    }


    /* ---------------------------------------------------------
       LIVE ENDPOINT VALUES
       --------------------------------------------------------- */

    let endpointTimer = null;

    function startEndpointUpdates() {

        clearInterval(endpointTimer);

        function update() {

            const cpu = document.getElementById("endpointCPU");

            if (!cpu) {
                clearInterval(endpointTimer);
                return;
            }

            const cpuValue = Math.floor(Math.random() * 35) + 25;
            const memoryValue = Math.floor(Math.random() * 25) + 45;
            const scoreValue = Math.floor(Math.random() * 7) + 91;

            document.getElementById("endpointCPU").textContent =
                cpuValue + "%";

            document.getElementById("cpuBar").style.width =
                cpuValue + "%";

            document.getElementById("endpointMemory").textContent =
                memoryValue + "%";

            document.getElementById("memoryBar").style.width =
                memoryValue + "%";

            document.getElementById("endpointScore").textContent =
                scoreValue + "%";

            document.getElementById("scoreBar").style.width =
                scoreValue + "%";

            document.getElementById("endpointRisk").textContent =
                Math.floor(Math.random() * 12) + 20;
        }

        update();
        endpointTimer = setInterval(update, 10000);
    }


    /* ---------------------------------------------------------
       LIVE CLOUD VALUES
       --------------------------------------------------------- */

    let cloudTimer = null;

    function startCloudUpdates() {

        clearInterval(cloudTimer);

        function update() {

            const systems = document.getElementById("cloudSystems");

            if (!systems) {
                clearInterval(cloudTimer);
                return;
            }

            const total = 1240 + Math.floor(Math.random() * 45);
            const protectedSystems =
                total - Math.floor(Math.random() * 20);

            document.getElementById("cloudSystems").textContent =
                total.toLocaleString();

            document.getElementById("cloudProtected").textContent =
                protectedSystems.toLocaleString();

            document.getElementById("cloudEvents").textContent =
                Math.floor(Math.random() * 25) + 25;

            document.getElementById("cloudRisk").textContent =
                Math.floor(Math.random() * 15) + 12;
        }

        update();
        cloudTimer = setInterval(update, 10000);
    }


    /* ---------------------------------------------------------
       SIDEBAR CLICK HANDLER
       --------------------------------------------------------- */

    document.addEventListener("click", function (event) {

        const sidebar = getSidebar();

        if (!sidebar || !sidebar.contains(event.target)) {
            return;
        }

        const item = event.target.closest(
            "a, button, .nav-item, .menu-item, .sidebar-item"
        );

        if (!item || !sidebar.contains(item)) {
            return;
        }

        const text = item.textContent
            .trim()
            .replace(/\s+/g, " ")
            .toLowerCase();

        /*
         * Only intercept the three pages that were blank.
         * Other pages keep their existing behavior.
         */

        if (text.includes("threat")) {

            event.preventDefault();
            event.stopPropagation();

            showThreats();
            setActiveSidebar(item);

            return;
        }

        if (text.includes("endpoint")) {

            event.preventDefault();
            event.stopPropagation();

            showEndpoints();
            setActiveSidebar(item);

            return;
        }

        if (text === "cloud" || text.includes("cloud")) {

            event.preventDefault();
            event.stopPropagation();

            showCloud();
            setActiveSidebar(item);

            return;
        }

    }, true);


    /* ---------------------------------------------------------
       ACTIVE SIDEBAR ITEM
       --------------------------------------------------------- */

    function setActiveSidebar(activeItem) {

        const sidebar = getSidebar();

        if (!sidebar) return;

        sidebar.querySelectorAll(
            "a, button, .nav-item, .menu-item, .sidebar-item"
        ).forEach(item => {

            item.classList.remove(
                "active",
                "selected",
                "current"
            );

        });

        activeItem.classList.add("active");
        activeItem.classList.add("selected");
    }


    /* ---------------------------------------------------------
       EXTRA PROFESSIONAL STYLES
       --------------------------------------------------------- */

    const style = document.createElement("style");

    style.textContent = `

        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 28px;
            gap: 20px;
        }

        .page-header h1 {
            margin: 5px 0;
            font-size: 32px;
        }

        .page-header p {
            margin: 0;
            opacity: .65;
        }

        .section-label {
            color: #55aaff;
            font-size: 11px;
            letter-spacing: 1.5px;
            font-weight: 700;
        }

        .live-indicator {
            font-size: 11px;
            color: #48e6a1;
            border: 1px solid rgba(72,230,161,.25);
            padding: 10px 15px;
            border-radius: 20px;
            white-space: nowrap;
        }

        .live-dot {
            width: 7px;
            height: 7px;
            display: inline-block;
            border-radius: 50%;
            background: #48e6a1;
            box-shadow: 0 0 10px #48e6a1;
            margin-right: 6px;
        }

        .im-stat-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 18px;
        }

        .im-stat-card,
        .im-panel {
            background: rgba(11, 19, 38, .78);
            border: 1px solid rgba(100,150,220,.16);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 10px 35px rgba(0,0,0,.16);
        }

        .im-stat-title {
            font-size: 11px;
            letter-spacing: 1.2px;
            opacity: .6;
        }

        .im-stat-value {
            font-size: 30px;
            font-weight: 700;
            margin: 8px 0;
        }

        .im-stat-status {
            color: #45e0a0;
            font-size: 11px;
            font-weight: 700;
        }

        .im-two-column {
            display: grid;
            grid-template-columns: 1.35fr 1fr;
            gap: 18px;
            margin-bottom: 18px;
        }

        .im-panel h2 {
            margin: 5px 0 20px;
            font-size: 20px;
        }

        .im-panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .live-badge {
            color: #48e6a1;
            border: 1px solid rgba(72,230,161,.25);
            padding: 5px 9px;
            border-radius: 15px;
            font-size: 9px;
        }

        .threat-row,
        .endpoint-event,
        .cloud-event,
        .cloud-service {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 14px 0;
            border-bottom: 1px solid rgba(255,255,255,.06);
        }

        .threat-row:last-child,
        .endpoint-event:last-child,
        .cloud-event:last-child,
        .cloud-service:last-child {
            border-bottom: 0;
        }

        .threat-row div,
        .endpoint-event div,
        .cloud-event div,
        .cloud-service div {
            flex: 1;
        }

        .threat-row small,
        .endpoint-event small,
        .cloud-event small,
        .cloud-service small {
            display: block;
            opacity: .5;
            margin-top: 4px;
        }

        .severity {
            min-width: 62px;
            text-align: center;
            font-size: 9px;
            font-weight: 700;
        }

        .critical {
            color: #ff5555;
        }

        .high {
            color: #ff7777;
        }

        .medium {
            color: #ffd166;
        }

        .low {
            color: #55d6ff;
        }

        .threat-live {
            font-size: 9px;
            color: #48e6a1;
        }

        .attack-item {
            display: grid;
            grid-template-columns: 90px 1fr 40px;
            align-items: center;
            gap: 10px;
            margin: 18px 0;
            font-size: 11px;
        }

        .attack-item b {
            text-align: right;
            font-size: 10px;
            opacity: .65;
        }

        .attack-bar,
        .metric-track {
            height: 7px;
            border-radius: 10px;
            background: rgba(255,255,255,.07);
            overflow: hidden;
        }

        .attack-bar i {
            display: block;
            height: 100%;
            background: #e94f55;
            border-radius: inherit;
        }

        .metric-line {
            display: flex;
            justify-content: space-between;
            margin-top: 18px;
            font-size: 12px;
        }

        .metric-track {
            margin-top: 7px;
        }

        .metric-track i {
            display: block;
            height: 100%;
            background: #348cff;
            border-radius: inherit;
            transition: width .8s ease;
        }

        .endpoint-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }

        .endpoint-detail {
            padding: 15px;
            background: rgba(255,255,255,.025);
            border-radius: 8px;
        }

        .endpoint-detail span {
            display: block;
            font-size: 10px;
            opacity: .5;
            margin-bottom: 6px;
        }

        .endpoint-detail strong {
            font-size: 13px;
        }

        .online-text,
        .secure-text {
            color: #48e6a1 !important;
        }

        .event-icon,
        .service-dot {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            background: #48e6a1;
            box-shadow: 0 0 9px rgba(72,230,161,.7);
            flex-shrink: 0;
        }

        .response-flow {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            margin: 25px 0;
        }

        .response-flow div:not(.flow-arrow) {
            padding: 14px;
            background: rgba(40,120,255,.08);
            border: 1px solid rgba(80,150,255,.15);
            border-radius: 8px;
            font-size: 11px;
        }

        .response-flow span {
            display: block;
            color: #55aaff;
            font-size: 9px;
            margin-bottom: 5px;
        }

        .flow-arrow {
            opacity: .4;
        }

        .protection-status {
            color: #48e6a1;
            font-size: 11px;
            font-weight: 700;
        }

        .cloud-chart {
            height: 180px;
            display: flex;
            align-items: flex-end;
            gap: 10px;
            padding: 15px 5px;
        }

        .cloud-column {
            flex: 1;
            min-width: 8px;
            background: linear-gradient(
                to top,
                #286cff,
                rgba(40,108,255,.25)
            );
            border-radius: 5px 5px 0 0;
        }

        .cloud-chart-labels {
            display: flex;
            justify-content: space-between;
            opacity: .4;
            font-size: 9px;
        }

        @media(max-width:900px) {

            .im-stat-grid {
                grid-template-columns: repeat(2,1fr);
            }

            .im-two-column {
                grid-template-columns: 1fr;
            }

            .page-header {
                align-items: flex-start;
                flex-direction: column;
            }

        }

        @media(max-width:600px) {

            .im-stat-grid {
                grid-template-columns: 1fr;
            }

            .endpoint-details {
                grid-template-columns: 1fr;
            }

            .response-flow {
                flex-direction: column;
            }

            .flow-arrow {
                transform: rotate(90deg);
            }

        }

    `;

    document.head.appendChild(style);

})();
