from flask import Flask, render_template, jsonify
import random
from datetime import datetime

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

# =========================================================
# IRONMIND AI - LIVE SYSTEM STATE
# =========================================================

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


# =========================================================
# DEMO MODE
# =========================================================

demo_mode = "normal"


# =========================================================
# GENERATE LIVE TELEMETRY
# =========================================================

def generate_live_data():

    global demo_mode

    # -----------------------------------------------------
    # NORMAL MODE
    # -----------------------------------------------------

    if demo_mode == "normal":

        risk = random.randint(10, 30)

        ai_risk = max(
            5,
            min(
                35,
                risk + random.randint(-5, 7)
            )
        )

        system_state["risk"] = risk
        system_state["ai_risk"] = ai_risk

        system_state["status"] = "SYSTEM PROTECTED"
        system_state["incident"] = "NO ACTIVE INCIDENT"

        system_state["threats"] = random.choice([0, 0, 0, 1])

        system_state["endpoint"] = "SECURE"
        system_state["network"] = "MONITORING"
        system_state["iot_ot"] = "READY"

        system_state["usb_activity"] = random.choice([
            "NORMAL",
            "MONITORED",
            "NORMAL",
            "NORMAL"
        ])

    # -----------------------------------------------------
    # CYBER MODE
    # -----------------------------------------------------

    elif demo_mode == "cyber":

        risk = random.randint(72, 96)

        ai_risk = max(
            70,
            min(
                99,
                risk + random.randint(-4, 6)
            )
        )

        system_state["risk"] = risk
        system_state["ai_risk"] = ai_risk

        system_state["status"] = "THREAT DETECTED"

        system_state["incident"] = (
            "SUSPICIOUS USB DATA TRANSFER"
        )

        system_state["threats"] = random.randint(1, 3)

        system_state["endpoint"] = "THREAT BLOCKED"
        system_state["network"] = "MONITORING"
        system_state["iot_ot"] = "READY"

        system_state["usb_activity"] = (
            "SUSPICIOUS TRANSFER BLOCKED"
        )

    # -----------------------------------------------------
    # MACHINE MODE
    # -----------------------------------------------------

    elif demo_mode == "machine":

        risk = random.randint(55, 78)

        ai_risk = max(
            50,
            min(
                88,
                risk + random.randint(-5, 5)
            )
        )

        system_state["risk"] = risk
        system_state["ai_risk"] = ai_risk

        system_state["status"] = "MACHINE WARNING"

        system_state["incident"] = (
            "ABNORMAL MACHINE SENSOR VALUES"
        )

        system_state["threats"] = 1

        system_state["endpoint"] = "MONITORING"
        system_state["network"] = "MONITORING"
        system_state["iot_ot"] = "ANOMALY DETECTED"

        system_state["usb_activity"] = "NORMAL"

    # -----------------------------------------------------
    # COMMON LIVE VALUES
    # -----------------------------------------------------

    system_state["cpu"] = random.randint(20, 85)

    system_state["memory"] = random.randint(35, 82)

    system_state["network_traffic"] = random.randint(
        20,
        95
    )

    system_state["ai_processing"] = random.randint(
        65,
        98
    )

    system_state["machine_temperature"] = random.randint(
        45,
        88
    )

    system_state["machine_vibration"] = round(
        random.uniform(1.2, 8.5),
        1
    )

    system_state["machine_rpm"] = random.randint(
        900,
        1800
    )

    # Events continuously change
    system_state["events"] += random.randint(
        1,
        7
    )

    # Blocked events occasionally increase
    if random.random() < 0.35:

        system_state["blocked"] += random.randint(
            1,
            3
        )

    # Threat statistics change
    system_state["critical"] = random.randint(
        1,
        5
    )

    system_state["high"] = random.randint(
        5,
        15
    )

    system_state["medium"] = random.randint(
        15,
        35
    )

    system_state["low"] = random.randint(
        40,
        80
    )

    # System counts slightly vary
    system_state["endpoints"] = random.randint(
        7800,
        7950
    )

    system_state["cloud"] = random.randint(
        1200,
        1300
    )

    system_state["network_devices"] = random.randint(
        4250,
        4400
    )

    system_state["last_update"] = (
        datetime.now().strftime("%H:%M:%S")
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def dashboard():

    return render_template(
        "dashboard.html"
    )


# =========================================================
# LIVE STATUS
# =========================================================

@app.route("/api/status")
def status():

    generate_live_data()

    return jsonify(system_state)


# =========================================================
# CYBER TEST
# =========================================================

@app.route("/api/cyber-test")
def cyber_test():

    global demo_mode

    demo_mode = "cyber"

    system_state["blocked"] += 1
    system_state["events"] += 1

    generate_live_data()

    return jsonify({
        "success": True,
        "message": (
            "Suspicious USB data transfer "
            "detected and automatically blocked."
        ),
        "state": system_state
    })


# =========================================================
# MACHINE TEST
# =========================================================

@app.route("/api/machine-test")
def machine_test():

    global demo_mode

    demo_mode = "machine"

    system_state["events"] += 1

    generate_live_data()

    return jsonify({
        "success": True,
        "message": (
            "Machine sensor anomaly detected "
            "by AI monitoring."
        ),
        "state": system_state
    })


# =========================================================
# RESET
# =========================================================

@app.route("/api/reset")
def reset():

    global demo_mode

    demo_mode = "normal"

    system_state["risk"] = 18
    system_state["ai_risk"] = 22

    system_state["status"] = (
        "SYSTEM PROTECTED"
    )

    system_state["incident"] = (
        "NO ACTIVE INCIDENT"
    )

    system_state["threats"] = 0

    system_state["endpoint"] = "SECURE"
    system_state["network"] = "MONITORING"
    system_state["iot_ot"] = "READY"

    system_state["usb_activity"] = "NORMAL"

    generate_live_data()

    return jsonify({
        "success": True,
        "message": "System reset successfully.",
        "state": system_state
    })


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
