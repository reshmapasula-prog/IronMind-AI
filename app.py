from flask import Flask, render_template, jsonify
from datetime import datetime
import random

from cyber.monitor import CyberMonitor
from machine.monitor import MachineMonitor
from response.engine import ResponseEngine


# ---------------------------------------------------------
# FLASK APPLICATION
# ---------------------------------------------------------

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)


# ---------------------------------------------------------
# IRONMIND AI MODULES
# ---------------------------------------------------------

cyber_monitor = CyberMonitor()
machine_monitor = MachineMonitor()
response_engine = ResponseEngine()


# ---------------------------------------------------------
# SYSTEM STATE
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


# Current demonstration mode
demo_mode = "normal"


# ---------------------------------------------------------
# LIVE DEMO DATA
# ---------------------------------------------------------

def generate_live_data():
    global system_state

    if demo_mode == "cyber":

        system_state["risk"] = random.randint(72, 96)
        system_state["ai_risk"] = random.randint(70, 99)

        system_state["status"] = "THREAT DETECTED"
        system_state["incident"] = "SUSPICIOUS USB DATA TRANSFER"

        system_state["threats"] = random.randint(1, 3)
        system_state["endpoint"] = "THREAT BLOCKED"
        system_state["network"] = "MONITORING"
        system_state["iot_ot"] = "READY"

        system_state["usb_activity"] = "SUSPICIOUS TRANSFER BLOCKED"

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

    else:

        system_state["risk"] = random.randint(10, 30)
        system_state["ai_risk"] = random.randint(5, 35)

        system_state["status"] = "SYSTEM PROTECTED"
        system_state["incident"] = "NO ACTIVE INCIDENT"

        system_state["threats"] = random.choice([0, 0, 0, 1])

        system_state["endpoint"] = "SECURE"
        system_state["network"] = "MONITORING"
        system_state["iot_ot"] = "READY"

        system_state["usb_activity"] = random.choice(
            ["NORMAL", "NORMAL", "MONITORED"]
        )

    # -----------------------------------------------------
    # SYSTEM METRICS
    # -----------------------------------------------------

    system_state["cpu"] = random.randint(25, 70)
    system_state["memory"] = random.randint(35, 75)
    system_state["network_traffic"] = random.randint(30, 85)

    system_state["ai_processing"] = random.randint(65, 98)

    system_state["machine_temperature"] = random.randint(55, 85)
    system_state["machine_vibration"] = round(
        random.uniform(2.0, 7.5), 1
    )
    system_state["machine_rpm"] = random.randint(1350, 1850)

    # -----------------------------------------------------
    # SECURITY COUNTERS
    # -----------------------------------------------------

    system_state["events"] += random.randint(1, 8)

    if demo_mode == "cyber":
        system_state["blocked"] += random.randint(0, 2)

    system_state["critical"] = random.randint(1, 4)
    system_state["high"] = random.randint(5, 12)
    system_state["medium"] = random.randint(15, 30)
    system_state["low"] = random.randint(40, 70)

    # -----------------------------------------------------
    # INFRASTRUCTURE COUNTERS
    # -----------------------------------------------------

    system_state["endpoints"] = random.randint(7800, 8100)
    system_state["cloud"] = random.randint(1200, 1300)
    system_state["network_devices"] = random.randint(4200, 4400)

    # -----------------------------------------------------
    # TIMESTAMP
    # -----------------------------------------------------

    system_state["last_update"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return system_state


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------

@app.route("/")
def index():
    return render_template("dashboard.html")


# ---------------------------------------------------------
# LIVE STATUS API
# ---------------------------------------------------------

@app.route("/api/status")
def api_status():

    generate_live_data()

    return jsonify(system_state)


# ---------------------------------------------------------
# CYBER TEST
# ---------------------------------------------------------

@app.route("/api/cyber-test", methods=["GET", "POST"])
def cyber_test():

    global demo_mode

    demo_mode = "cyber"

    system_state["blocked"] += 1
    system_state["events"] += 1

    generate_live_data()

    response = response_engine.respond_to_threat(
        "SUSPICIOUS USB DATA TRANSFER"
    )

    return jsonify({
        "success": True,
        "message": "Cybersecurity threat simulation completed.",
        "response": response,
        "state": system_state
    })


# ---------------------------------------------------------
# MACHINE TEST
# ---------------------------------------------------------

@app.route("/api/machine-test", methods=["GET", "POST"])
def machine_test():

    global demo_mode

    demo_mode = "machine"

    system_state["events"] += 1

    # Simulate machine anomaly
    try:
        machine_monitor.simulate_anomaly()
    except AttributeError:
        pass

    generate_live_data()

    response = response_engine.respond_to_machine_anomaly()

    return jsonify({
        "success": True,
        "message": "Machine anomaly simulation completed.",
        "response": response,
        "state": system_state
    })


# ---------------------------------------------------------
# RESET SYSTEM
# ---------------------------------------------------------

@app.route("/api/reset", methods=["GET", "POST"])
def reset_system():

    global demo_mode

    demo_mode = "normal"

    system_state["risk"] = 18
    system_state["ai_risk"] = 22

    system_state["status"] = "SYSTEM PROTECTED"
    system_state["incident"] = "NO ACTIVE INCIDENT"

    system_state["threats"] = 0

    system_state["endpoint"] = "SECURE"
    system_state["network"] = "MONITORING"
    system_state["iot_ot"] = "READY"

    system_state["usb_activity"] = "NORMAL"

    # Reset machine module
    try:
        machine_monitor.reset()
    except AttributeError:
        pass

    # Reset response engine
    try:
        response_engine.reset()
    except AttributeError:
        pass

    generate_live_data()

    return jsonify({
        "success": True,
        "message": "IronMind AI system reset successfully.",
        "state": system_state
    })


# ---------------------------------------------------------
# APPLICATION START
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
