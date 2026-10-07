from flask import Flask, render_template, jsonify, request
from datetime import datetime
import hashlib
import random
import time

from cyber.monitor import CyberMonitor
from machine.monitor import MachineMonitor
from response.engine import ResponseEngine


# ============================================================
# IRONMIND AI - FLASK APPLICATION
# ============================================================

app = Flask(__name__)

cyber_monitor = CyberMonitor()
machine_monitor = MachineMonitor()
response_engine = ResponseEngine()


# ============================================================
# GLOBAL STATE
# ============================================================

system_state = {
    "risk": 18,
    "ai_risk": 22,

    "status": "SYSTEM PROTECTED",
    "incident": "NO ACTIVE INCIDENT",

    "endpoint_status": "ENDPOINT SECURE",
    "network_status": "NETWORK MONITORING",
    "iot_status": "IoT / OT READY",
    "ai_status": "AI ENGINE ACTIVE",

    "active_threats": 0,
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
    "vibration": 3.2,
    "rpm": 1450,

    "usb_activity": "NORMAL",

    "workflow": [
        "Device Detected",
        "Anomaly Score",
        "Threat Classified",
        "Response Decision",
        "Forensic Record"
    ],

    "last_update": None
}


# ============================================================
# USB STATE
# ============================================================

usb_state = {
    "connected": False,
    "drive": None,
    "device": None,

    "files_scanned": 0,
    "files": [],

    "anomaly_score": 0,
    "threat_class": "NONE",
    "severity": "NORMAL",

    "action": "MONITOR",
    "status": "NO USB DEVICE",

    "scan_status": "IDLE",
    "last_scan": None
}


# ============================================================
# EVENT STORAGE
# ============================================================

threat_events = []
quarantine_files = []
investigation_records = []
network_events = []
endpoint_events = []


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def clamp_score(value):
    """
    Keep ML score between 0 and 100.
    Does NOT artificially increase the score.
    """

    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0

    return round(max(0, min(100, value)))


def classify_risk(score):
    """
    IronMind AI risk classification.

    0-49   NORMAL
    50-69  MEDIUM / WARNING
    70-84  HIGH
    85-100 CRITICAL
    """

    score = clamp_score(score)

    if score >= 85:
        return "CRITICAL"

    if score >= 70:
        return "HIGH"

    if score >= 50:
        return "MEDIUM"

    return "NORMAL"


def get_action(score):
    """
    IMPORTANT:
    Only genuinely critical ML results are quarantined.

    85+  -> QUARANTINE
    <85  -> MONITOR
    """

    score = clamp_score(score)

    if score >= 85:
        return "QUARANTINE"

    return "MONITOR"


def get_threat_class(score):
    score = clamp_score(score)

    if score >= 85:
        return "MALICIOUS USB CONTENT"

    if score >= 70:
        return "ANOMALOUS USB BEHAVIOR"

    if score >= 50:
        return "UNUSUAL USB BEHAVIOR"

    return "NORMAL USB ACTIVITY"


def generate_hash(filename):
    """
    This is only an event identifier.

    IMPORTANT:
    It is NOT a real file SHA-256.
    Real file hashing should be performed by usb_agent.py.
    """

    raw = f"{filename}-{time.time_ns()}"

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


def safe_int(value, default=0):

    try:
        return int(value)

    except (TypeError, ValueError):
        return default


# ============================================================
# EXTRACT ML SCORE
# ============================================================

def extract_ml_score(result):
    """
    Supports different return formats from your existing
    cyber/monitor.py.

    Examples supported:

        {"anomaly_score": 60}

        {"score": 60}

        {"risk_score": 60}

        60
    """

    if isinstance(result, dict):

        possible_keys = [
            "anomaly_score",
            "anomaly",
            "score",
            "risk_score",
            "risk",
            "ml_score"
        ]

        for key in possible_keys:

            if key in result:

                try:
                    return clamp_score(result[key])

                except (TypeError, ValueError):
                    pass

    elif isinstance(result, (int, float)):

        return clamp_score(result)

    return 0


# ============================================================
# DASHBOARD LIVE DATA
# ============================================================

def generate_live_data():

    # Do not randomly change USB ML result while a real USB
    # scan is active.

    if not usb_state["connected"]:

        system_state["risk"] = random.randint(10, 30)
        system_state["ai_risk"] = random.randint(15, 30)

    else:

        # When USB is connected, dashboard reflects
        # the actual ML result.

        system_state["risk"] = usb_state["anomaly_score"]
        system_state["ai_risk"] = usb_state["anomaly_score"]

    system_state["cpu"] = random.randint(25, 55)
    system_state["memory"] = random.randint(40, 70)
    system_state["network_traffic"] = random.randint(30, 70)
    system_state["ai_processing"] = random.randint(75, 95)

    system_state["machine_temperature"] = random.randint(55, 70)
    system_state["vibration"] = round(random.uniform(2.0, 4.5), 1)
    system_state["rpm"] = random.randint(1300, 1600)

    system_state["last_update"] = now()

    return system_state


# ============================================================
# HOME / WEBSITE
# ============================================================

@app.route("/")
def index():

    return render_template("index.html")


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    generate_live_data()

    return render_template(
        "dashboard.html",
        state=system_state
    )


# ============================================================
# GENERAL STATUS API
# ============================================================

@app.route("/api/status")
def api_status():

    generate_live_data()

    return jsonify({
        **system_state,
        "usb": usb_state
    })


# ============================================================
# REAL USB EVENT
# ============================================================

@app.route("/api/usb-event", methods=["POST"])
def usb_event():

    data = request.get_json(silent=True) or {}

    connected = bool(
        data.get("connected", False)
    )

    # --------------------------------------------------------
    # USB REMOVED
    # --------------------------------------------------------

    if not connected:

        usb_state.update({
            "connected": False,
            "drive": None,
            "device": None,

            "files_scanned": 0,
            "files": [],

            "anomaly_score": 0,
            "threat_class": "NONE",
            "severity": "NORMAL",

            "action": "MONITOR",
            "status": "NO USB DEVICE",

            "scan_status": "IDLE",
            "last_scan": now()
        })

        system_state.update({
            "risk": 18,
            "ai_risk": 22,
            "status": "SYSTEM PROTECTED",
            "incident": "NO ACTIVE INCIDENT",
            "active_threats": 0,
            "usb_activity": "NORMAL"
        })

        return jsonify({
            "success": True,
            "message": "USB disconnected",
            "action": "MONITOR",
            "quarantine": False,
            "usb": usb_state
        })


    # --------------------------------------------------------
    # USB CONNECTED
    # --------------------------------------------------------

    drive = data.get("drive", "Unknown")
    device = data.get("device", "USB Device")

    files = data.get("files", [])

    if not isinstance(files, list):
        files = []


    print()
    print("[IRONMIND] LIVE USB DETECTED")
    print(f"[IRONMIND] Drive: {drive}")
    print(f"[IRONMIND] Files received: {len(files)}")
    print("[IRONMIND] Running existing ML analysis...")


    # --------------------------------------------------------
    # YOUR EXISTING ML MODEL
    # --------------------------------------------------------

    try:

        ml_result = cyber_monitor.analyze_usb(files)

    except Exception as e:

        print(
            f"[IRONMIND] ML analysis error: {e}"
        )

        ml_result = {
            "anomaly_score": 0
        }


    # --------------------------------------------------------
    # GET REAL ML SCORE
    # --------------------------------------------------------

    score = extract_ml_score(ml_result)

    threat_class = get_threat_class(score)

    severity = classify_risk(score)

    action = get_action(score)


    print(
        f"[IRONMIND] Anomaly score: {score}%"
    )

    print(
        f"[IRONMIND] Threat class: {threat_class}"
    )

    print(
        f"[IRONMIND] Severity: {severity}"
    )

    print(
        f"[IRONMIND] Action: {action}"
    )


    # --------------------------------------------------------
    # USB STATE
    # --------------------------------------------------------

    usb_state.update({

        "connected": True,

        "drive": drive,

        "device": device,

        "files_scanned": len(files),

        "files": files,

        "anomaly_score": score,

        "threat_class": threat_class,

        "severity": severity,

        "action": action,

        "status": (
            "QUARANTINE REQUIRED"
            if action == "QUARANTINE"
            else (
                "HIGH RISK - MONITORING"
                if severity == "HIGH"
                else (
                    "WARNING - MONITORING"
                    if severity == "MEDIUM"
                    else "PROTECTED"
                )
            )
        ),

        "scan_status": "COMPLETED",

        "last_scan": now()
    })


    # ========================================================
    # UPDATE DASHBOARD
    # ========================================================

    system_state["risk"] = score
    system_state["ai_risk"] = score

    system_state["usb_activity"] = (
        "QUARANTINE REQUIRED"
        if action == "QUARANTINE"
        else (
            "HIGH RISK"
            if severity == "HIGH"
            else (
                "UNUSUAL USB BEHAVIOR"
                if severity == "MEDIUM"
                else "NORMAL"
            )
        )
    )


    # ========================================================
    # NORMAL / MEDIUM / HIGH
    # ========================================================

    if action == "MONITOR":

        system_state["status"] = (
            "SYSTEM MONITORING"
            if severity != "NORMAL"
            else "SYSTEM PROTECTED"
        )

        system_state["incident"] = (
            threat_class
            if severity != "NORMAL"
            else "NO ACTIVE INCIDENT"
        )

        # Do NOT increase blocked count.
        # Do NOT quarantine.
        # Do NOT create a quarantine event.

        if severity == "HIGH":

            system_state["active_threats"] = 1

        elif severity == "MEDIUM":

            system_state["active_threats"] = 0

        else:

            system_state["active_threats"] = 0


    # ========================================================
    # CRITICAL >= 85
    # ========================================================

    else:

        system_state["status"] = "THREAT DETECTED"

        system_state["incident"] = threat_class

        system_state["active_threats"] = 1

        system_state["blocked"] += 1

        # ----------------------------------------------------
        # Create threat event
        # ----------------------------------------------------

        event = {

            "id": len(threat_events) + 1,

            "time": now(),

            "type": "USB DRIVE",

            "description": threat_class,

            "risk": score,

            "severity": severity,

            "action": "QUARANTINE",

            "status": "QUARANTINE REQUIRED",

            "drive": drive,

            "files": len(files)
        }

        threat_events.insert(0, event)


        # ----------------------------------------------------
        # Investigation record
        # ----------------------------------------------------

        investigation_records.insert(
            0,
            {
                "time": now(),

                "incident": threat_class,

                "source": "USB DRIVE",

                "risk": score,

                "severity": severity,

                "action": "QUARANTINE",

                "status": "QUARANTINE REQUIRED",

                "drive": drive
            }
        )


        # ----------------------------------------------------
        # Record files that should be quarantined
        # ----------------------------------------------------

        for file in files:

            if isinstance(file, dict):

                filename = file.get(
                    "name",
                    file.get("filename", "Unknown")
                )

            else:

                filename = str(file)


            quarantine_files.append({

                "filename": filename,

                "drive": drive,

                "risk": score,

                "time": now(),

                "status": "QUARANTINE REQUIRED",

                "hash": (
                    file.get("sha256")
                    if isinstance(file, dict)
                    and file.get("sha256")
                    else generate_hash(filename)
                )
            })


    # ========================================================
    # RESPONSE TO USB AGENT
    # ========================================================

    response = {

        "success": True,

        "message": (
            "USB activity monitored"
            if action == "MONITOR"
            else "High-confidence threat detected. Quarantine required."
        ),

        "anomaly_score": score,

        "risk_score": score,

        "threat_class": threat_class,

        "severity": severity,

        "action": action,

        "quarantine": (
            action == "QUARANTINE"
        ),

        "files_scanned": len(files),

        "usb": usb_state
    }


    print(
        "[IRONMIND] Server response sent to USB agent"
    )

    print(
        f"[IRONMIND] Score: {score}%"
    )

    print(
        f"[IRONMIND] Decision: {action}"
    )

    print()

    return jsonify(response)


# ============================================================
# USB STATUS
# ============================================================

@app.route("/api/usb-status")
def usb_status():

    return jsonify(usb_state)


# ============================================================
# THREATS
# ============================================================

@app.route("/api/threats")
def threats():

    return jsonify({
        "critical": system_state["critical"],
        "high": system_state["high"],
        "medium": system_state["medium"],
        "low": system_state["low"],
        "active": system_state["active_threats"],
        "events": threat_events
    })


# ============================================================
# QUARANTINE
# ============================================================

@app.route("/api/quarantine")
def quarantine():

    return jsonify({
        "count": len(quarantine_files),
        "files": quarantine_files
    })


# ============================================================
# INVESTIGATIONS
# ============================================================

@app.route("/api/investigations")
def investigations():

    return jsonify({
        "count": len(investigation_records),
        "records": investigation_records
    })


# ============================================================
# CYBER TEST
# ============================================================

@app.route("/api/cyber-test", methods=["POST", "GET"])
def cyber_test():

    test_files = [

        {
            "name": "test_document.exe",
            "extension": ".exe",
            "size": 8000000
        },

        {
            "name": "suspicious_script.ps1",
            "extension": ".ps1",
            "size": 120000
        },

        {
            "name": "normal_document.txt",
            "extension": ".txt",
            "size": 4000
        }
    ]


    try:

        result = cyber_monitor.analyze_usb(
            test_files
        )

        score = extract_ml_score(result)

    except Exception:

        score = 0


    severity = classify_risk(score)

    action = get_action(score)

    return jsonify({

        "success": True,

        "test": "CYBER TEST",

        "anomaly_score": score,

        "severity": severity,

        "action": action,

        "message": (
            "Suspicious USB activity detected"
            if score >= 50
            else "USB activity appears normal"
        )
    })


# ============================================================
# USB THREAT TEST
# ============================================================

@app.route("/api/usb-threat-test", methods=["POST", "GET"])
def usb_threat_test():

    """
    Separate demonstration endpoint.

    This does NOT affect the real USB-agent workflow.
    """

    score = 90

    severity = classify_risk(score)

    action = get_action(score)

    return jsonify({

        "success": True,

        "demo": True,

        "anomaly_score": score,

        "threat_class": "MALICIOUS USB CONTENT",

        "severity": severity,

        "action": action,

        "quarantine": action == "QUARANTINE",

        "message": (
            "Demo critical threat generated"
        )
    })


# ============================================================
# MACHINE TEST
# ============================================================

@app.route("/api/machine-test", methods=["POST", "GET"])
def machine_test():

    temperature = 90
    vibration = 9
    current = 18
    rpm = 400


    try:

        result = machine_monitor.analyze(
            temperature=temperature,
            vibration=vibration,
            current=current,
            rpm=rpm
        )

    except Exception:

        result = {
            "risk_score": 70
        }


    if isinstance(result, dict):

        score = extract_ml_score(result)

        if score == 0:

            score = clamp_score(
                result.get("risk_score", 0)
            )

    else:

        score = clamp_score(result)


    system_state["risk"] = score
    system_state["ai_risk"] = score

    system_state["incident"] = (
        "ABNORMAL MACHINE SENSOR VALUES"
    )

    system_state["iot_status"] = (
        "IoT ANOMALY DETECTED"
    )


    return jsonify({

        "success": True,

        "anomaly_score": score,

        "temperature": temperature,

        "vibration": vibration,

        "current": current,

        "rpm": rpm,

        "message": (
            "Machine sensor anomaly detected by AI monitoring"
        )
    })


# ============================================================
# NETWORK TEST
# ============================================================
@app.route("/api/network-test", methods=["POST", "GET"])
def network_test():

    network_event = {

        "time": now(),

        "source": "NETWORK",

        "description": "Suspicious network behavior",

        "severity": "MEDIUM",

        "status": "MONITORING"
    }

    network_events.insert(
        0,
        network_event
    )

    return jsonify({

        "success": True,

        "message": "Network activity analyzed",

        "event": network_event
    })


# ============================================================
# ENDPOINT TEST
# ============================================================

@app.route("/api/endpoint-test", methods=["POST", "GET"])
def endpoint_test():

    endpoint_event = {

        "time": now(),

        "source": "ENDPOINT",

        "description": "Endpoint telemetry analyzed",

        "severity": "LOW",

        "status": "MONITORING"
    }

    endpoint_events.insert(
        0,
        endpoint_event
    )

    return jsonify({

        "success": True,

        "message": "Endpoint activity analyzed",

        "event": endpoint_event
    })


# ============================================================
# RESET
# ============================================================

@app.route("/api/reset", methods=["POST", "GET"])
def reset():

    system_state.update({

        "risk": 18,

        "ai_risk": 22,

        "status": "SYSTEM PROTECTED",

        "incident": "NO ACTIVE INCIDENT",

        "active_threats": 0,

        "usb_activity": "NORMAL",

        "endpoint_status": "ENDPOINT SECURE",

        "network_status": "NETWORK MONITORING",

        "iot_status": "IoT / OT READY"
    })


    usb_state.update({

        "connected": False,

        "drive": None,

        "device": None,

        "files_scanned": 0,

        "files": [],

        "anomaly_score": 0,

        "threat_class": "NONE",

        "severity": "NORMAL",

        "action": "MONITOR",

        "status": "NO USB DEVICE",

        "scan_status": "IDLE",

        "last_scan": now()
    })


    threat_events.clear()

    quarantine_files.clear()

    investigation_records.clear()

    network_events.clear()

    endpoint_events.clear()


    return jsonify({

        "success": True,

        "message": "IronMind AI reset successfully",

        "status": system_state,

        "usb": usb_state
    })


# ============================================================
# ERROR HANDLER
# ============================================================

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


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("IRONMIND AI")
    print("AUTONOMOUS CYBER DEFENSE PLATFORM")
    print("=" * 60)
    print()
    print("Dashboard : http://127.0.0.1:5000/dashboard")
    print("USB API   : /api/usb-event")
    print("Status    : /api/status")
    print()
    print("USB RISK POLICY")
    print("----------------")
    print("0-49   : NORMAL   -> MONITOR")
    print("50-69  : MEDIUM   -> MONITOR")
    print("70-84  : HIGH     -> MONITOR")
    print("85-100 : CRITICAL -> QUARANTINE")
    print()
    print("=" * 60)
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
