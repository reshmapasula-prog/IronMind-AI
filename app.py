from flask import Flask, render_template, jsonify
from datetime import datetime
import random
import threading


# ============================================================
# IRONMIND AI - FLASK APPLICATION
# Cyber Defense + Machine / IoT Monitoring
# Prototype / Simulation
# ============================================================

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)


# ============================================================
# SYSTEM STATE
# ============================================================

state_lock = threading.Lock()

system_state = {
    # Main security state
    "risk": 18,
    "ai_risk": 22,
    "status": "SYSTEM PROTECTED",
    "incident": "NO ACTIVE INCIDENT",

    # Monitoring systems
    "ai_engine": "ACTIVE",
    "endpoint": "SECURE",
    "network": "MONITORING",
    "iot_ot": "READY",

    # Threat counters
    "threats": 0,
    "blocked": 24,
    "events": 1934,

    # Severity
    "critical": 2,
    "high": 8,
    "medium": 21,
    "low": 57,

    # Infrastructure
    "endpoints": 7892,
    "cloud": 1256,
    "network_devices": 4325,

    # Performance
    "ai_processing": 87,
    "cpu": 34,
    "memory": 52,
    "network_traffic": 48,

    # Machine / IoT
    "machine_temperature": 62,
    "machine_vibration": 3.2,
    "machine_rpm": 1450,

    # USB
    "usb_activity": "NORMAL",

    # Mode
    "demo_mode": "normal",

    # Timestamp
    "last_update": ""
}


# ============================================================
# HELPERS
# ============================================================

def update_timestamp():
    system_state["last_update"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def generate_live_data():
    """
    Generates simulated monitoring data for the prototype.
    """

    mode = system_state["demo_mode"]

    # --------------------------------------------------------
    # NORMAL MODE
    # --------------------------------------------------------

    if mode == "normal":

        system_state["risk"] = random.randint(10, 30)
        system_state["ai_risk"] = random.randint(5, 35)

        system_state["status"] = "SYSTEM PROTECTED"
        system_state["incident"] = "NO ACTIVE INCIDENT"

        system_state["threats"] = random.choice([0, 0, 0, 1])

        system_state["endpoint"] = "SECURE"
        system_state["network"] = "MONITORING"
        system_state["iot_ot"] = "READY"

        system_state["usb_activity"] = random.choice([
            "NORMAL",
            "NORMAL",
            "MONITORED"
        ])

    # --------------------------------------------------------
    # CYBER TEST MODE
    # --------------------------------------------------------

    elif mode == "cyber":

        system_state["risk"] = random.randint(72, 96)
        system_state["ai_risk"] = random.randint(70, 99)

        system_state["status"] = "THREAT DETECTED"
        system_state["incident"] = "SUSPICIOUS USB DATA TRANSFER"

        system_state["threats"] = random.randint(1, 3)

        system_state["endpoint"] = "THREAT BLOCKED"
        system_state["network"] = "MONITORING"
        system_state["iot_ot"] = "READY"

        system_state["usb_activity"] = "SUSPICIOUS TRANSFER BLOCKED"

    # --------------------------------------------------------
    # MACHINE TEST MODE
    # --------------------------------------------------------

    elif mode == "machine":

        system_state["risk"] = random.randint(55, 78)
        system_state["ai_risk"] = random.randint(50, 88)

        system_state["status"] = "MACHINE WARNING"
        system_state["incident"] = "ABNORMAL MACHINE SENSOR VALUES"

        system_state["threats"] = 1

        system_state["endpoint"] = "MONITORING"
        system_state["network"] = "MONITORING"
        system_state["iot_ot"] = "ANOMALY DETECTED"

        system_state["usb_activity"] = "NORMAL"

    # --------------------------------------------------------
    # COMMON LIVE VALUES
    # --------------------------------------------------------

    system_state["cpu"] = random.randint(20, 85)
    system_state["memory"] = random.randint(30, 80)
    system_state["network_traffic"] = random.randint(20, 90)

    system_state["ai_processing"] = random.randint(60, 99)

    system_state["machine_temperature"] = random.randint(55, 85)
    system_state["machine_vibration"] = round(
        random.uniform(1.5, 6.5), 1
    )
    system_state["machine_rpm"] = random.randint(1100, 1800)

    # Infrastructure values
    system_state["endpoints"] = random.randint(7800, 8050)
    system_state["cloud"] = random.randint(1200, 1300)
    system_state["network_devices"] = random.randint(4200, 4400)

    # Event counter
    system_state["events"] += random.randint(1, 8)

    # Blocked counter
    if mode == "cyber":
        system_state["blocked"] += random.randint(1, 3)
    else:
        if random.random() > 0.7:
            system_state["blocked"] += 1

    # Severity counts
    system_state["critical"] = random.randint(1, 5)
    system_state["high"] = random.randint(5, 15)
    system_state["medium"] = random.randint(15, 35)
    system_state["low"] = random.randint(40, 80)

    update_timestamp()


def get_state():
    """
    Return a safe copy of the current state.
    """
    with state_lock:
        return dict(system_state)


# ============================================================
# PAGE ROUTES
# ============================================================

@app.route("/")
def home():
    """
    Public IronMind AI landing page.
    """
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    """
    Security Operations Center dashboard.
    """
    return render_template("dashboard.html")


# ============================================================
# API - LIVE STATUS
# ============================================================

@app.route("/api/status", methods=["GET"])
def api_status():

    with state_lock:
        generate_live_data()
        data = dict(system_state)

    return jsonify({
        "success": True,
        "data": data
    })


# ============================================================
# API - CYBER SECURITY TEST
# ============================================================

@app.route("/api/cyber-test", methods=["POST"])
def cyber_test():

    with state_lock:

        system_state["demo_mode"] = "cyber"

        system_state["blocked"] += random.randint(1, 3)
        system_state["events"] += random.randint(5, 15)

        generate_live_data()

        data = dict(system_state)

    return jsonify({
        "success": True,
        "message": "Cyber security simulation completed.",
        "data": data
    })


# ============================================================
# API - MACHINE / IOT TEST
# ============================================================

@app.route("/api/machine-test", methods=["POST"])
def machine_test():

    with state_lock:

        system_state["demo_mode"] = "machine"

        system_state["events"] += random.randint(5, 15)

        generate_live_data()

        data = dict(system_state)

    return jsonify({
        "success": True,
        "message": "Machine and IoT simulation completed.",
        "data": data
    })


# ============================================================
# API - RESET
# ============================================================

@app.route("/api/reset", methods=["POST"])
def reset_system():

    with state_lock:

        system_state["demo_mode"] = "normal"

        system_state["risk"] = 18
        system_state["ai_risk"] = 22

        system_state["status"] = "SYSTEM PROTECTED"
        system_state["incident"] = "NO ACTIVE INCIDENT"

        system_state["threats"] = 0

        system_state["endpoint"] = "SECURE"
        system_state["network"] = "MONITORING"
        system_state["iot_ot"] = "READY"

        system_state["usb_activity"] = "NORMAL"

        generate_live_data()

        data = dict(system_state)

    return jsonify({
        "success": True,
        "message": "IronMind AI system has been reset.",
        "data": data
    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "online",
        "service": "IronMind AI",
        "timestamp": datetime.now().isoformat()
    })


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("IRONMIND AI")
    print("Cyber Defense + Machine / IoT Monitoring")
    print("=" * 60)
    print("Landing Page : http://127.0.0.1:5000/")
    print("Dashboard    : http://127.0.0.1:5000/dashboard")
    print("Health Check : http://127.0.0.1:5000/health")
    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
