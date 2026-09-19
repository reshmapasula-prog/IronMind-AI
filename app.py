from flask import Flask, render_template, jsonify, request
from datetime import datetime
import random
import threading


# ============================================================
# IRONMIND AI
# Cyber Defense + Endpoint + USB Monitoring Platform
# ============================================================

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

state_lock = threading.Lock()


# ============================================================
# SYSTEM STATE
# ============================================================

system_state = {
    # -------------------------
    # General
    # -------------------------
    "risk": 18,
    "ai_risk": 16,
    "status": "PROTECTED",
    "incident": "No active security incident",
    "ai_engine": "ACTIVE",

    # -------------------------
    # Security modules
    # -------------------------
    "endpoint": "SECURE",
    "network": "MONITORING",
    "iot_ot": "MONITORING",

    # -------------------------
    # Threat information
    # -------------------------
    "threats": 3,
    "blocked": 24,
    "critical": 0,
    "high": 1,
    "medium": 1,
    "low": 1,

    # -------------------------
    # Infrastructure
    # -------------------------
    "endpoints": 12,
    "cloud": 8,
    "network_devices": 18,

    # -------------------------
    # AI
    # -------------------------
    "ai_processing": 72,

    # -------------------------
    # Endpoint telemetry
    # -------------------------
    "cpu": 32,
    "memory": 46,
    "network_traffic": 38,
    "usb_activity": "NO USB EVENT",

    # -------------------------
    # Machine / IoT
    # -------------------------
    "machine_temperature": 42.5,
    "machine_vibration": 1.2,
    "machine_rpm": 1498,

    # -------------------------
    # USB REAL-WORLD MONITORING
    # -------------------------
    "usb_connected": False,
    "usb_drive": "",
    "usb_event": "NO USB EVENT",
    "usb_time": "",

    # -------------------------
    # Event system
    # -------------------------
    "events": 18,

    # -------------------------
    # Last update
    # -------------------------
    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}


# ============================================================
# DEMO MODE
# ============================================================

demo_mode = "normal"


# ============================================================
# TIMESTAMP
# ============================================================

def update_timestamp():
    system_state["last_update"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# ============================================================
# LIVE SIMULATION
# ============================================================

def generate_live_data():

    global demo_mode

    with state_lock:

        # ----------------------------------------------------
        # NORMAL MODE
        # ----------------------------------------------------

        if demo_mode == "normal":

            system_state["risk"] = random.randint(10, 28)
            system_state["ai_risk"] = random.randint(8, 25)

            system_state["threats"] = random.randint(1, 5)
            system_state["critical"] = 0
            system_state["high"] = random.randint(0, 2)
            system_state["medium"] = random.randint(1, 3)
            system_state["low"] = random.randint(1, 4)

            system_state["endpoint"] = "SECURE"
            system_state["network"] = "MONITORING"
            system_state["iot_ot"] = "MONITORING"

            system_state["cpu"] = random.randint(20, 55)
            system_state["memory"] = random.randint(35, 65)
            system_state["network_traffic"] = random.randint(20, 55)

            system_state["machine_temperature"] = round(
                random.uniform(38, 48), 1
            )

            system_state["machine_vibration"] = round(
                random.uniform(0.8, 1.8), 1
            )

            system_state["machine_rpm"] = random.randint(
                1450, 1550
            )

            system_state["status"] = "PROTECTED"
            system_state["incident"] = "No active security incident"

        # ----------------------------------------------------
        # CYBER TEST MODE
        # ----------------------------------------------------

        elif demo_mode == "cyber":

            system_state["risk"] = random.randint(65, 90)
            system_state["ai_risk"] = random.randint(70, 95)

            system_state["threats"] = random.randint(7, 14)
            system_state["critical"] = random.randint(1, 3)
            system_state["high"] = random.randint(2, 5)
            system_state["medium"] = random.randint(2, 5)
            system_state["low"] = random.randint(1, 4)

            system_state["endpoint"] = "THREAT DETECTED"
            system_state["network"] = "ANALYZING"
            system_state["iot_ot"] = "MONITORING"

            system_state["status"] = "UNDER ATTACK"

            system_state["incident"] = (
                "Cybersecurity test event detected"
            )

            system_state["cpu"] = random.randint(55, 90)
            system_state["memory"] = random.randint(55, 85)
            system_state["network_traffic"] = random.randint(60, 95)

        # ----------------------------------------------------
        # MACHINE TEST MODE
        # ----------------------------------------------------

        elif demo_mode == "machine":

            system_state["risk"] = random.randint(55, 85)
            system_state["ai_risk"] = random.randint(60, 90)

            system_state["machine_temperature"] = round(
                random.uniform(65, 85), 1
            )

            system_state["machine_vibration"] = round(
                random.uniform(4.0, 7.0), 1
            )

            system_state["machine_rpm"] = random.randint(
                1050, 1250
            )

            system_state["endpoint"] = "SECURE"
            system_state["network"] = "MONITORING"
            system_state["iot_ot"] = "ANOMALY DETECTED"

            system_state["status"] = "MACHINE ANOMALY"

            system_state["incident"] = (
                "Machine telemetry anomaly detected"
            )

        update_timestamp()


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():
    return render_template("dashboard.html")


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ============================================================
# API - CURRENT STATUS
# ============================================================

@app.route("/api/status")
def api_status():

    # Update simulated values
    generate_live_data()

    with state_lock:
        data = dict(system_state)

    return jsonify(data)


# ============================================================
# API - USB EVENT
# REAL HARDWARE CONNECTION
# ============================================================

@app.route("/api/usb-event", methods=["POST"])
def usb_event():

    data = request.get_json(silent=True) or {}

    event = data.get(
        "event",
        "unknown"
    )

    drive = data.get(
        "drive",
        "Unknown USB"
    )

    timestamp = data.get(
        "timestamp",
        datetime.now().isoformat()
    )

    with state_lock:

        # ----------------------------------------------------
        # USB CONNECTED
        # ----------------------------------------------------

        if event == "connected":

            system_state["usb_connected"] = True

            system_state["usb_drive"] = drive

            system_state["usb_event"] = (
                "USB DEVICE DETECTED"
            )

            system_state["usb_activity"] = (
                "USB DEVICE CONNECTED"
            )

            system_state["incident"] = (
                f"USB device detected on {drive}"
            )

            # Increase risk slightly for visibility
            system_state["risk"] = max(
                system_state["risk"],
                32
            )

            system_state["ai_risk"] = max(
                system_state["ai_risk"],
                28
            )

        # ----------------------------------------------------
        # USB REMOVED
        # ----------------------------------------------------

        elif event == "removed":

            system_state["usb_connected"] = False

            system_state["usb_drive"] = ""

            system_state["usb_event"] = (
                "USB DEVICE REMOVED"
            )

            system_state["usb_activity"] = (
                "USB DEVICE REMOVED"
            )

            system_state["incident"] = (
                "USB device removed from endpoint"
            )

        # ----------------------------------------------------
        # UNKNOWN EVENT
        # ----------------------------------------------------

        else:

            system_state["usb_event"] = (
                "UNKNOWN USB EVENT"
            )

            system_state["usb_activity"] = (
                "UNKNOWN USB EVENT"
            )

        system_state["usb_time"] = timestamp

        system_state["events"] += 1

        update_timestamp()

        response_data = dict(system_state)

    return jsonify({
        "success": True,
        "message": "USB event received by IronMind AI",
        "data": response_data
    })


# ============================================================
# API - CYBER TEST
# ============================================================

@app.route("/api/cyber-test", methods=["GET", "POST"])
def cyber_test():

    global demo_mode

    demo_mode = "cyber"

    generate_live_data()

    with state_lock:
        system_state["blocked"] += random.randint(
            1,
            3
        )

        system_state["events"] += 1

        data = dict(system_state)

    return jsonify({
        "success": True,
        "message": "Cybersecurity test executed",
        "data": data
    })


# ============================================================
# API - MACHINE TEST
# ============================================================

@app.route("/api/machine-test", methods=["GET", "POST"])
def machine_test():

    global demo_mode

    demo_mode = "machine"

    generate_live_data()

    with state_lock:

        system_state["events"] += 1

        data = dict(system_state)

    return jsonify({
        "success": True,
        "message": "Machine anomaly test executed",
        "data": data
    })


# ============================================================
# API - RESET SYSTEM
# ============================================================

@app.route("/api/reset", methods=["GET", "POST"])
def reset_system():

    global demo_mode

    demo_mode = "normal"

    with state_lock:

        system_state["risk"] = 18
        system_state["ai_risk"] = 16

        system_state["status"] = "PROTECTED"

        system_state["incident"] = (
            "No active security incident"
        )

        system_state["endpoint"] = "SECURE"
        system_state["network"] = "MONITORING"
        system_state["iot_ot"] = "MONITORING"

        system_state["threats"] = 3
        system_state["critical"] = 0
        system_state["high"] = 1
        system_state["medium"] = 1
        system_state["low"] = 1

        system_state["cpu"] = 32
        system_state["memory"] = 46
        system_state["network_traffic"] = 38

        system_state["machine_temperature"] = 42.5
        system_state["machine_vibration"] = 1.2
        system_state["machine_rpm"] = 1498

        system_state["usb_activity"] = "NO USB EVENT"
        system_state["usb_event"] = "NO USB EVENT"

        system_state["events"] = 18

        update_timestamp()

        data = dict(system_state)

    return jsonify({
        "success": True,
        "message": "IronMind AI system reset",
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
        "usb_monitoring": True,
        "timestamp": datetime.now().isoformat()
    })


# ============================================================
# RUN LOCAL SERVER
# Render uses Gunicorn instead of this section.
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
