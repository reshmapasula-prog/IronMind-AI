from flask import Flask, render_template, jsonify
from datetime import datetime
import random

# Import IronMind modules
from cyber.monitor import CyberMonitor
from machine.monitor import MachineMonitor
from response.engine import ResponseEngine


# ---------------------------------------------------------
# Flask Application
# ---------------------------------------------------------

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)


# ---------------------------------------------------------
# Initialize IronMind Modules
# ---------------------------------------------------------

cyber_monitor = CyberMonitor()
machine_monitor = MachineMonitor()
response_engine = ResponseEngine()


# ---------------------------------------------------------
# Demo System State
# ---------------------------------------------------------

system_state = {
    "risk": 18,
    "ai_risk": 22,

    "status": "SYSTEM PROTECTED",
    "incident": "NO ACTIVE INCIDENT",

    "ai_engine": "ACTIVE",
    "endpoint": "SECURE",
    "network": "MONITORING",
    "iot_ot": "READY",

    "threats": 0,
    "blocked": 24,
    "events": 1934,

    "critical": 2,
    "high": 8,
    "medium": 21,
    "low": 57,

    "endpoints": 7892,
    "cloud": 1256,
    "network_devices": 4325,

    "ai_processing": 87,

    "cpu": 34,
    "memory": 52,
    "network_traffic": 48,

    "machine_temperature": 62,
    "machine_vibration": 3.2,
    "machine_rpm": 1450,

    "usb_activity": "NORMAL",

    "last_update": ""
}


# ---------------------------------------------------------
# Demo Mode
# ---------------------------------------------------------

demo_mode = "normal"


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def safe_int(value, default=0):
    """Safely convert a value to an integer."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def clamp(value, minimum, maximum):
    """Keep a value inside a specified range."""
    return max(minimum, min(maximum, value))


# ---------------------------------------------------------
# Generate Simulated Live Data
# ---------------------------------------------------------

def generate_live_data():
    """
    Generate simulated cybersecurity and machine-monitoring
    data for the IronMind AI demonstration.

    NOTE:
    This is a prototype simulation. It does not perform
    real-world cybersecurity blocking or machine control.
    """

    global demo_mode

    # ---------------------------------------------
    # Normal Mode
    # ---------------------------------------------

    if demo_mode == "normal":

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

    # ---------------------------------------------
    # Cyber Attack Simulation
    # ---------------------------------------------

    elif demo_mode == "cyber":

        system_state["risk"] = random.randint(72, 96)
        system_state["ai_risk"] = random.randint(70, 99)

        system_state["status"] = "THREAT DETECTED"
        system_state["incident"] = "SUSPICIOUS USB DATA TRANSFER"

        system_state["threats"] = random.randint(1, 3)

        system_state["endpoint"] = "THREAT BLOCKED"
        system_state["network"] = "MONITORING"
        system_state["iot_ot"] = "READY"

        system_state["usb_activity"] = "SUSPICIOUS TRANSFER BLOCKED"

    # ---------------------------------------------
    # Machine Anomaly Simulation
    # ---------------------------------------------

    elif demo_mode == "machine":

        system_state["risk"] = random.randint(55, 78)
        system_state["ai_risk"] = random.randint(50, 88)

        system_state["status"] = "MACHINE WARNING"
        system_state["incident"] = "ABNORMAL MACHINE SENSOR VALUES"

        system_state["threats"] = 1

        system_state["endpoint"] = "MONITORING"
        system_state["network"] = "MONITORING"
        system_state["iot_ot"] = "ANOMALY DETECTED"

        system_state["usb_activity"] = "NORMAL"

    # ---------------------------------------------
    # Common Telemetry
    # ---------------------------------------------

    system_state["cpu"] = random.randint(20, 75)
    system_state["memory"] = random.randint(35, 80)
    system_state["network_traffic"] = random.randint(25, 90)

    system_state["ai_processing"] = random.randint(70, 99)

    # Machine telemetry
    system_state["machine_temperature"] = random.randint(45, 85)

    system_state["machine_vibration"] = round(
        random.uniform(1.2, 7.5),
        1
    )

    system_state["machine_rpm"] = random.randint(1200, 1800)

    # Event counters
    system_state["events"] += random.randint(1, 8)

    if demo_mode == "cyber":
        system_state["blocked"] += random.randint(1, 4)

    # Severity counters
    system_state["critical"] = random.randint(1, 5)
    system_state["high"] = random.randint(5, 15)
    system_state["medium"] = random.randint(15, 35)
    system_state["low"] = random.randint(40, 80)

    # Infrastructure
    system_state["endpoints"] = random.randint(7800, 8100)
    system_state["cloud"] = random.randint(1200, 1300)
    system_state["network_devices"] = random.randint(4200, 4400)

    # Timestamp
    system_state["last_update"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return system_state


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------

@app.route("/")
def dashboard():
    """Render the IronMind AI dashboard."""
    return render_template("dashboard.html")


# ---------------------------------------------------------
# Live Status API
# ---------------------------------------------------------

@app.route("/api/status")
def api_status():
    """
    Return current simulated IronMind system status.
    """

    try:
        data = generate_live_data()

        return jsonify({
            "success": True,
            "data": data
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error),
            "data": system_state
        }), 500


# ---------------------------------------------------------
# Cybersecurity Test
# ---------------------------------------------------------

@app.route("/api/cyber-test", methods=["GET", "POST"])
def cyber_test():
    """
    Trigger the cybersecurity attack simulation.
    """

    global demo_mode

    demo_mode = "cyber"

    system_state["events"] += 1
    system_state["blocked"] += 1

    generate_live_data()

    return jsonify({
        "success": True,
        "message": "Cybersecurity threat simulation activated.",
        "mode": "cyber",
        "data": system_state
    })


# ---------------------------------------------------------
# Machine Test
# ---------------------------------------------------------

@app.route("/api/machine-test", methods=["GET", "POST"])
def machine_test():
    """
    Trigger the machine anomaly simulation.
    """

    global demo_mode

    demo_mode = "machine"

    system_state["events"] += 1

    generate_live_data()

    return jsonify({
        "success": True,
        "message": "Machine anomaly simulation activated.",
        "mode": "machine",
        "data": system_state
    })


# ---------------------------------------------------------
# Reset System
# ---------------------------------------------------------

@app.route("/api/reset", methods=["GET", "POST"])
def reset_system():
    """
    Return IronMind to normal protected demo mode.
    """

    global demo_mode

    demo_mode = "normal"

    system_state.update({
        "risk": 18,
        "ai_risk": 22,

        "status": "SYSTEM PROTECTED",
        "incident": "NO ACTIVE INCIDENT",

        "ai_engine": "ACTIVE",
        "endpoint": "SECURE",
        "network": "MONITORING",
        "iot_ot": "READY",

        "threats": 0,

        "usb_activity": "NORMAL",

        "cpu": 34,
        "memory": 52,
        "network_traffic": 48,

        "machine_temperature": 62,
        "machine_vibration": 3.2,
        "machine_rpm": 1450,

        "ai_processing": 87
    })

    generate_live_data()

    return jsonify({
        "success": True,
        "message": "IronMind system returned to protected mode.",
        "mode": "normal",
        "data": system_state
    })


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@app.route("/api/health")
def health_check():
    """
    Simple health endpoint useful when deploying the app.
    """

    return jsonify({
        "status": "online",
        "application": "IronMind AI",
        "version": "1.0",
        "mode": demo_mode,
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    })


# ---------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


# ---------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
