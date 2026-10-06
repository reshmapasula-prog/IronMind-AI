from flask import Flask, jsonify, render_template, request
from datetime import datetime
from threading import RLock
import hashlib
import os
import traceback

from cyber.monitor import CyberMonitor
from machine.monitor import MachineMonitor
from response.engine import ResponseEngine


# ============================================================
# IRONMIND AI
# Autonomous AI Cyber Defense Platform
#
# Flow:
# Endpoint -> Network -> IoT -> Industrial / OT
#
# Live:
#   Endpoint Defense
#   Network Defense
#   USB / Removable Media Defense
#
# Not connected:
#   IoT / Sensors
#   Industrial / OT
#
# Detection:
#   Server-side ML / IsolationForest
# ============================================================


app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

state_lock = RLock()

# ------------------------------------------------------------
# CORE ENGINES
# ------------------------------------------------------------

cyber_monitor = CyberMonitor()
machine_monitor = MachineMonitor()
response_engine = ResponseEngine()


# ------------------------------------------------------------
# DATABASE-LIKE IN-MEMORY STORAGE
# ------------------------------------------------------------

threat_events = []
quarantine_files = []
investigation_records = []
network_events = []
endpoint_events = []


# ------------------------------------------------------------
# DEMO / TEST STATE
# ------------------------------------------------------------

demo_mode = "normal"


# ------------------------------------------------------------
# SYSTEM STATE
# ------------------------------------------------------------

system_state = {
    "risk": 18,
    "ai_risk": 16,
    "status": "PROTECTED",
    "incident": "No active incident",
    "ai_engine": "ACTIVE",

    "modules": {
        "endpoint": "SECURE",
        "network": "MONITORING",
        "iot_ot": "NOT CONNECTED"
    },

    "threats": 0,
    "blocked": 0,

    "severity": {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    },

    "infrastructure": {
        "endpoints": 12,
        "cloud": 8,
        "network_devices": 18
    },

    "ai": {
        "ai_processing": 72,
        "engine": "IsolationForest",
        "detection": "SERVER-SIDE ML",
        "classification": "ACTIVE",
        "prediction": "READY",
        "response": "AUTONOMOUS"
    },

    "endpoint": {
        "cpu": 32,
        "memory": 46,
        "network_traffic": 38,
        "processes": 0,
        "status": "SECURE"
    },

    "network": {
        "traffic": 38,
        "connections": 24,
        "status": "MONITORING",
        "devices": 18
    },

    "cloud": {
        "status": "ONLINE",
        "api_security": "ACTIVE",
        "data_security": "ACTIVE"
    },

    "usb": {
        "connected": False,
        "drive": "",
        "device": "",
        "filesystem": "",
        "status": "NOT CONNECTED",
        "scan": "WAITING",
        "files_scanned": 0,
        "suspicious": 0,
        "storage": 0,

        "anomaly_score": 0,
        "threat_class": "NONE",
        "severity": "LOW",
        "action": "NONE",

        "detection": "SERVER-SIDE ML",
        "threat_analysis": "LLM",
        "autonomous_response": "SERVER DECISION",

        "last_update": None
    },

    "iot": {
        "status": "NOT CONNECTED",
        "sensors": 0,
        "alerts": 0,
        "temperature": None,
        "vibration": None,
        "rpm": None
    },

    "industrial_ot": {
        "status": "NOT CONNECTED",
        "controllers": 0,
        "plcs": 0,
        "alerts": 0
    },

    "workflow": {
        "device_detected": False,
        "anomaly_detected": False,
        "threat_classified": False,
        "device_quarantined": False,
        "forensic_report": False
    },

    "events": [],

    "last_update": None
}


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def update_timestamp():
    system_state["last_update"] = datetime.now().isoformat()


def current_time():
    return datetime.now().isoformat()


def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def generate_hash(value):
    raw = f"{value}-{datetime.now().isoformat()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def add_event(
    event_type,
    message,
    severity="INFO",
    score=0,
    source="IRONMIND AI"
):
    event = {
        "id": len(system_state["events"]) + 1,
        "timestamp": current_time(),
        "type": event_type,
        "message": message,
        "severity": severity,
        "score": score,
        "source": source
    }

    system_state["events"].insert(0, event)

    # Keep memory under control
    system_state["events"] = system_state["events"][:100]

    return event


def update_threat_counters():
    critical = 0
    high = 0
    medium = 0
    low = 0

    for event in threat_events:
        severity = str(event.get("severity", "")).upper()

        if severity == "CRITICAL":
            critical += 1
        elif severity == "HIGH":
            high += 1
        elif severity == "MEDIUM":
            medium += 1
        else:
            low += 1

    system_state["threats"] = len(threat_events)
    system_state["blocked"] = sum(
        1
        for event in threat_events
        if str(event.get("action", "")).upper()
        in {
            "BLOCKED",
            "QUARANTINED",
            "ISOLATED"
        }
    )

    system_state["severity"] = {
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low
    }


# ============================================================
# THREAT / FORENSIC RECORD
# ============================================================

def create_threat_record(
    source,
    threat_type,
    risk_score,
    severity,
    reason,
    filename="",
    drive=""
):
    threat_id = len(threat_events) + 1
    timestamp = current_time()

    sha256 = generate_hash(
        f"{filename}-{drive}-{threat_id}"
    )

    threat = {
        "id": threat_id,
        "timestamp": timestamp,
        "source": source,
        "filename": filename,
        "drive": drive,
        "threat_type": threat_type,
        "risk_score": int(risk_score),
        "severity": severity,
        "reason": reason,
        "action": "BLOCKED",
        "status": "QUARANTINED",
        "sha256": sha256,
        "investigation_status": "AVAILABLE"
    }

    threat_events.insert(0, threat)

    quarantine_record = {
        "id": len(quarantine_files) + 1,
        "timestamp": timestamp,
        "filename": filename,
        "source": source,
        "drive": drive,
        "sha256": sha256,
        "reason": reason,
        "risk_score": int(risk_score),
        "status": "QUARANTINED"
    }

    quarantine_files.insert(0, quarantine_record)

    investigation = {
        "id": len(investigation_records) + 1,
        "timestamp": timestamp,
        "threat_id": threat_id,
        "source": source,
        "filename": filename,
        "threat_type": threat_type,
        "risk_score": int(risk_score),
        "severity": severity,
        "sha256": sha256,
        "status": "AVAILABLE",
        "summary": (
            f"ML anomaly detected from {source}. "
            f"Autonomous response initiated."
        )
    }

    investigation_records.insert(0, investigation)

    update_threat_counters()

    return threat


# ============================================================
# USB HELPERS
# ============================================================

def extract_usb_files(data):
    """
    Supports several USB-agent payload formats.

    Accepted:
        {
            "files": [...]
        }

    or:
        {
            "scan": {
                "files": [...]
            }
        }
    """

    files = data.get("files")

    if not isinstance(files, list):
        scan = data.get("scan") or {}

        if isinstance(scan, dict):
            files = scan.get("files", [])

    if not isinstance(files, list):
        files = []

    return files


def get_usb_device_name(device):
    if isinstance(device, dict):
        return str(
            device.get("name")
            or device.get("device")
            or device.get("label")
            or "USB REMOVABLE DEVICE"
        )

    if device:
        return str(device)

    return "USB REMOVABLE DEVICE"


def get_usb_test_profile(data, files):
    """
    Optional harmless ML test profile.

    The USB agent may send:

        "ml_test_profile": "IRONMIND_ANOMALY_V1"

    This is NOT malware and does not execute anything.

    It only asks the server ML engine to evaluate the
    predefined anomaly-test feature profile.

    Normal USB files are still analyzed from telemetry.
    """

    profile = data.get("ml_test_profile")

    if profile:
        return str(profile)

    for item in files:
        if not isinstance(item, dict):
            continue

        if item.get("ml_test_profile"):
            return str(item.get("ml_test_profile"))

    return None


def analyze_usb_with_ml(files, test_profile=None):
    """
    Uses the CyberMonitor ML engine.

    Supports both:
        analyze_usb(files)
    and, if the monitor implements it:
        analyze_usb(files, test_profile)
    """

    try:
        if test_profile:
            # Preferred explicit test-profile API
            if hasattr(cyber_monitor, "analyze_usb_test"):
                return cyber_monitor.analyze_usb_test(
                    test_profile,
                    files
                )

            if hasattr(cyber_monitor, "analyze_usb_with_profile"):
                return cyber_monitor.analyze_usb_with_profile(
                    files,
                    test_profile
                )

        # Standard ML analysis
        return cyber_monitor.analyze_usb(files)

    except TypeError:
        # Compatibility with an older monitor signature
        return cyber_monitor.analyze_usb(files)


# ============================================================
# LIVE SYSTEM STATUS
# ============================================================

@app.route("/")
def front_page():
    """
    Main IronMind AI front page.

    The front page is intentionally separate from the
    operational security dashboard.
    """

    return render_template(
        "dashboard.html",
        page="landing"
    )


@app.route("/dashboard")
def dashboard():
    """
    Main Security Operations Center dashboard.
    """

    return render_template(
        "dashboard.html",
        page="dashboard"
    )


# ============================================================
# API: COMPLETE STATUS
# ============================================================

@app.route("/api/status")
def api_status():
    with state_lock:

        # Always keep IoT/OT honest.
        system_state["modules"]["iot_ot"] = "NOT CONNECTED"
        system_state["iot"]["status"] = "NOT CONNECTED"
        system_state["industrial_ot"]["status"] = "NOT CONNECTED"

        return jsonify(system_state)


# ============================================================
# API: USB STATUS
# ============================================================

@app.route("/api/usb-status")
def usb_status():
    with state_lock:
        return jsonify(system_state["usb"])


# ============================================================
# API: USB EVENT
# ============================================================

@app.route("/api/usb-event", methods=["POST"])
def usb_event():

    try:
        data = request.get_json(
            silent=True
        ) or {}

        connected = bool(
            data.get("connected", False)
        )

        drive = str(
            data.get("drive", "")
            or ""
        )

        device = data.get("device")

        filesystem = str(
            data.get("filesystem", "")
            or data.get("file_system", "")
            or ""
        )

        files = extract_usb_files(data)

        test_profile = get_usb_test_profile(
            data,
            files
        )

        # ----------------------------------------------------
        # USB REMOVED
        # ----------------------------------------------------

        if not connected:

            with state_lock:

                system_state["usb"] = {
                    "connected": False,
                    "drive": "",
                    "device": "",
                    "filesystem": "",
                    "status": "NOT CONNECTED",
                    "scan": "WAITING",
                    "files_scanned": 0,
                    "suspicious": 0,
                    "storage": 0,
                    "anomaly_score": 0,
                    "threat_class": "NONE",
                    "severity": "LOW",
                    "action": "NONE",
                    "detection": "SERVER-SIDE ML",
                    "threat_analysis": "LLM",
                    "autonomous_response": "SERVER DECISION",
                    "last_update": current_time()
                }

                system_state["workflow"] = {
                    "device_detected": False,
                    "anomaly_detected": False,
                    "threat_classified": False,
                    "device_quarantined": False,
                    "forensic_report": False
                }

                update_timestamp()

            return jsonify({
                "success": True,
                "connected": False,
                "drive": "",
                "files_scanned": 0,
                "anomaly_score": 0,
                "threat_class": "NONE",
                "severity": "LOW",
                "action": "NONE",
                "detection": "SERVER-SIDE ML"
            })


        # ----------------------------------------------------
        # USB CONNECTED
        # ----------------------------------------------------

        device_name = get_usb_device_name(
            device
        )

        # ----------------------------------------------------
        # ML ANALYSIS
        # ----------------------------------------------------

        ml_result = analyze_usb_with_ml(
            files,
            test_profile
        )

        if not isinstance(ml_result, dict):
            ml_result = {}

        anomaly_score = safe_int(
            ml_result.get(
                "anomaly_score",
                0
            )
        )

        anomaly_score = max(
            0,
            min(
                100,
                anomaly_score
            )
        )

        threat_class = str(
            ml_result.get(
                "threat_class",
                "NORMAL USB ACTIVITY"
            )
        )

        severity = str(
            ml_result.get(
                "severity",
                "LOW"
            )
        ).upper()

        ml_detected = bool(
            ml_result.get(
                "ml_detected",
                anomaly_score >= 70
            )
        )

        # ----------------------------------------------------
        # AUTONOMOUS DECISION
        # ----------------------------------------------------

        if anomaly_score >= 70:

            action = "QUARANTINE"
            usb_status_value = "THREAT DETECTED"

        else:

            action = "MONITOR"
            usb_status_value = "SECURE"


        # ----------------------------------------------------
        # STORAGE INFORMATION
        # ----------------------------------------------------

        storage = safe_int(
            data.get(
                "storage",
                data.get(
                    "storage_used",
                    0
                )
            )
        )

        suspicious_count = safe_int(
            data.get(
                "suspicious_count",
                1 if ml_detected else 0
            )
        )

        # ----------------------------------------------------
        # STATE UPDATE
        # ----------------------------------------------------

        with state_lock:

            system_state["usb"] = {
                "connected": True,
                "drive": drive,
                "device": device_name,
                "filesystem": filesystem,

                "status": usb_status_value,

                "scan": "COMPLETE",

                "files_scanned": len(files),

                "suspicious": suspicious_count,

                "storage": storage,

                "anomaly_score": anomaly_score,

                "threat_class": threat_class,

                "severity": severity,

                "action": action,

                "detection": "SERVER-SIDE ML",

                "threat_analysis": "LLM",

                "autonomous_response": "SERVER DECISION",

                "last_update": current_time()
            }


            # ------------------------------------------------
            # WORKFLOW
            # ------------------------------------------------

            system_state["workflow"] = {
                "device_detected": True,

                "anomaly_detected": (
                    anomaly_score >= 40
                ),

                "threat_classified": (
                    anomaly_score >= 40
                ),

                "device_quarantined": (
                    anomaly_score >= 70
                ),

                "forensic_report": (
                    anomaly_score >= 70
                )
            }


            # ------------------------------------------------
            # THREAT CASE
            # ------------------------------------------------

            if anomaly_score >= 70:

                system_state["risk"] = anomaly_score

                system_state["ai_risk"] = anomaly_score

                system_state["status"] = (
                    "THREAT BLOCKED"
                )

                system_state["modules"][
                    "endpoint"
                ] = "THREAT BLOCKED"

                system_state["endpoint"][
                    "status"
                ] = "THREAT BLOCKED"

                system_state["endpoint"][
                    "network_traffic"
                ] = anomaly_score


                # Create forensic record
                filename = ""

                if files:

                    first_suspicious = None

                    for item in files:

                        if not isinstance(
                            item,
                            dict
                        ):
                            continue

                        if item.get(
                            "ml_test"
                        ):

                            first_suspicious = item

                            break

                    if first_suspicious:

                        filename = str(
                            first_suspicious.get(
                                "name",
                                ""
                            )
                        )

                    elif isinstance(
                        files[0],
                        dict
                    ):

                        filename = str(
                            files[0].get(
                                "name",
                                ""
                            )
                        )


                threat = create_threat_record(
                    source="USB DRIVE",
                    threat_type=threat_class,
                    risk_score=anomaly_score,
                    severity=severity,
                    reason=(
                        "Server-side ML detected "
                        "anomalous removable-media "
                "telemetry."
                    ),
                    filename=filename,
                    drive=drive
                )


                add_event(
                    event_type="USB THREAT",
                    message=(
                        f"USB anomaly detected: "
                        f"{threat_class}"
                    ),
                    severity=severity,
                    score=anomaly_score,
                    source="USB ML SENSOR"
                )


                add_event(
                    event_type="AUTONOMOUS RESPONSE",
                    message=(
                        "USB device content "
                        "quarantined and forensic "
                        "record generated."
                    ),
                    severity="CRITICAL",
                    score=anomaly_score,
                    source="IRONMIND RESPONSE ENGINE"
                )


            else:

                system_state["ai_risk"] = anomaly_score

                system_state["endpoint"][
                    "status"
                ] = "SECURE"

                add_event(
                    event_type="USB SCAN",
                    message=(
                        "USB device scanned by "
                        "server-side ML."
                    ),
                    severity="INFO",
                    score=anomaly_score,
                    source="USB ML SENSOR"
                )


            update_timestamp()


        # ----------------------------------------------------
        # API RESPONSE
        # ----------------------------------------------------

        return jsonify({
            "success": True,

            "connected": True,

            "drive": drive,

            "device": device_name,

            "filesystem": filesystem,

            "files_scanned": len(files),

            "anomaly_score": anomaly_score,

            "threat_class": threat_class,

            "severity": severity,

            "action": action,

            "ml_detected": ml_detected,

            "detection": "SERVER-SIDE ML",

            "threat_analysis": "LLM",

            "autonomous_response": (
                "SERVER DECISION"
            ),

            "workflow": system_state[
                "workflow"
            ],

            "ml_result": ml_result
        })


    except Exception as error:

        traceback.print_exc()

        return jsonify({
            "success": False,
            "connected": False,
            "anomaly_score": 0,
            "threat_class": "ANALYSIS ERROR",
            "severity": "UNKNOWN",
            "action": "MONITOR",
            "detection": "SERVER-SIDE ML",
            "error": str(error)
        }), 500


# ============================================================
# API: USB THREAT TEST
# ============================================================

@app.route(
    "/api/usb-threat-test",
    methods=["GET", "POST"]
)
def usb_threat_test():

    try:

        # Explicit harmless ML demonstration.
        #
        # This does NOT execute a file.
        # It only asks the ML engine to evaluate
        # its anomaly-test profile if supported.

        demo_files = [
            {
                "name": "IRONMIND_ML_TEST.txt",
                "extension": ".txt",
                "size": 99999999,
                "is_hidden": True,
                "is_system": True,
                "ml_test": True
            }
        ]

        result = analyze_usb_with_ml(
            demo_files,
            "IRONMIND_ANOMALY_V1"
        )

        score = safe_int(
            result.get(
                "anomaly_score",
                0
            )
        )

        score = max(
            0,
            min(
                100,
                score
            )
        )

        threat_class = str(
            result.get(
                "threat_class",
                "ML ANOMALY TEST"
            )
        )

        severity = str(
            result.get(
                "severity",
                "CRITICAL"
            )
        ).upper()


        with state_lock:

            system_state["usb"][
                "connected"
            ] = True

            system_state["usb"][
                "drive"
            ] = "TEST USB"

            system_state["usb"][
                "device"
            ] = "IRONMIND ML TEST DEVICE"

            system_state["usb"][
                "filesystem"
            ] = "TEST"

            system_state["usb"][
                "status"
            ] = "THREAT DETECTED"

            system_state["usb"][
                "scan"
            ] = "COMPLETE"

            system_state["usb"][
                "files_scanned"
            ] = 1

            system_state["usb"][
                "suspicious"
            ] = 1

            system_state["usb"][
                "anomaly_score"
            ] = score

            system_state["usb"][
                "threat_class"
            ] = threat_class

            system_state["usb"][
                "severity"
            ] = severity

            system_state["usb"][
                "action"
            ] = "QUARANTINE"


            system_state["workflow"] = {
                "device_detected": True,
                "anomaly_detected": True,
                "threat_classified": True,
                "device_quarantined": True,
                "forensic_report": True
            }


            system_state["risk"] = score

            system_state["ai_risk"] = score

            system_state["status"] = (
                "THREAT BLOCKED"
            )

            system_state["modules"][
                "endpoint"
            ] = "THREAT BLOCKED"

            system_state["endpoint"][
                "status"
            ] = "THREAT BLOCKED"


            create_threat_record(
                source="USB ML TEST",
                threat_type=threat_class,
                risk_score=score,
                severity=severity,
                reason=(
                    "Harmless IronMind ML "
                    "anomaly demonstration."
                ),
                filename=(
                    "IRONMIND_ML_TEST.txt"
                ),
                drive="TEST USB"
            )


            add_event(
                event_type="ML TEST",
                message=(
                    "IronMind server-side "
                    "ML anomaly test executed."
                ),
                severity=severity,
                score=score,
                source="IRONMIND ML"
            )

            update_timestamp()


        return jsonify({
            "success": True,
            "test": True,
            "anomaly_score": score,
            "threat_class": threat_class,
            "severity": severity,
            "action": "QUARANTINE",
            "detection": "SERVER-SIDE ML",
            "workflow": system_state[
                "workflow"
            ]
        })


    except Exception as error:

        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# API: THREATS
# ============================================================

@app.route("/api/threats")
def get_threats():

    with state_lock:

        return jsonify({
            "success": True,
            "count": len(threat_events),
            "threats": threat_events
        })


# ============================================================
# API: QUARANTINE
# ============================================================

@app.route("/api/quarantine")
def get_quarantine():

    with state_lock:

        return jsonify({
            "success": True,
            "count": len(quarantine_files),
            "files": quarantine_files
        })


# ============================================================
# API: INVESTIGATIONS
# ============================================================

@app.route("/api/investigations")
def get_investigations():

    with state_lock:

        return jsonify({
            "success": True,
            "count": len(investigation_records),
            "investigations": investigation_records
        })


# ============================================================
# API: ENDPOINT TEST
# ============================================================

@app.route("/api/endpoint-test")
def endpoint_test():

    try:

        # Synthetic telemetry for dashboard testing.
        # Detection architecture remains ML-based.

        test_features = [
            {
                "extension": ".process",
                "size": 50000000,
                "is_hidden": True,
                "is_system": True
            },
            {
                "extension": ".network",
                "size": 30000000,
                "is_hidden": True,
                "is_system": True
            }
        ]

        ml_result = analyze_usb_with_ml(
            test_features
        )

        score = safe_int(
            ml_result.get(
                "anomaly_score",
                82
            )
        )

        score = max(
            70,
            min(
                100,
                score
            )
        )

        with state_lock:

            system_state["risk"] = score

            system_state["ai_risk"] = score

            system_state["status"] = (
                "THREAT BLOCKED"
            )

            system_state["modules"][
                "endpoint"
            ] = "THREAT BLOCKED"

            system_state["endpoint"][
                "status"
            ] = "THREAT BLOCKED"

            system_state["endpoint"][
                "cpu"
            ] = 91

            system_state["endpoint"][
                "memory"
            ] = 84

            system_state["endpoint"][
                "network_traffic"
            ] = score

            event = {
                "id": len(endpoint_events) + 1,
                "timestamp": current_time(),
                "source": "LOCAL ENDPOINT",
                "event": (
                    "SUSPICIOUS PROCESS "
                    "BEHAVIOR"
                ),
                "risk_score": score,
                "action": "BLOCKED",
                "status": "QUARANTINED"
            }

            endpoint_events.insert(
                0,
                event
            )

            add_event(
                event_type="ENDPOINT THREAT",
                message=(
                    "Endpoint anomaly "
                    "detected and blocked."
                ),
                severity="HIGH",
                score=score,
                source="ENDPOINT ML"
            )

            update_timestamp()


        return jsonify({
            "success": True,
            "source": "ENDPOINT",
            "anomaly_score": score,
            "threat_class": (
                "ENDPOINT ANOMALY"
            ),
            "action": "BLOCKED",
            "status": "THREAT BLOCKED"
        })


    except Exception as error:

        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# API: NETWORK TEST
# ============================================================

@app.route("/api/network-test")
def network_test():

    try:

        test_features = [
            {
                "extension": ".network",
                "size": 100000000,
                "is_hidden": True,
                "is_system": True
            },
            {
                "extension": ".traffic",
                "size": 90000000,
                "is_hidden": True,
                "is_system": True
            },
            {
                "extension": ".connection",
                "size": 80000000,
                "is_hidden": True,
                "is_system": True
            }
        ]

        ml_result = analyze_usb_with_ml(
            test_features
        )

        score = safe_int(
            ml_result.get(
                "anomaly_score",
                86
            )
        )

        score = max(
            70,
            min(
                100,
                score
            )
        )

        with state_lock:

            system_state["risk"] = max(
                system_state["risk"],
                score
            )

            system_state["ai_risk"] = max(
                system_state["ai_risk"],
                score
            )

            system_state["status"] = (
                "THREAT BLOCKED"
            )

            system_state["modules"][
                "network"
            ] = "THREAT BLOCKED"

            system_state["network"][
                "status"
            ] = "THREAT BLOCKED"

            system_state["network"][
                "traffic"
            ] = score


            event = {
                "id": len(network_events) + 1,
                "timestamp": current_time(),
                "source": "NETWORK",
                "event": (
                    "NETWORK ANOMALY "
                    "DETECTED"
                ),
                "risk_score": score,
                "action": "ISOLATED",
                "status": "BLOCKED"
            }

            network_events.insert(
                0,
                event
            )


            add_event(
                event_type="NETWORK THREAT",
                message=(
                    "Network anomaly "
                    "detected and connection "
                    "isolated."
                ),
                severity="HIGH",
                score=score,
                source="NETWORK ML"
            )

            update_timestamp()


        return jsonify({
            "success": True,
            "source": "NETWORK",
            "anomaly_score": score,
            "threat_class": (
                "NETWORK ANOMALY"
            ),
            "action": "ISOLATED",
            "status": "THREAT BLOCKED"
        })


    except Exception as error:

        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# API: NETWORK EVENTS
# ============================================================

@app.route("/api/network-events")
def get_network_events():

    with state_lock:

        return jsonify({
            "success": True,
            "count": len(network_events),
            "events": network_events
        })


# ============================================================
# API: ENDPOINT EVENTS
# ============================================================

@app.route("/api/endpoint-events")
def get_endpoint_events():

    with state_lock:

        return jsonify({
            "success": True,
            "count": len(endpoint_events),
            "events": endpoint_events
        })


# ============================================================
# API: CYBER TEST
# ============================================================

@app.route("/api/cyber-test")
def cyber_test():

    return network_test()


# ============================================================
# API: MACHINE / IoT TEST
# ============================================================

@app.route("/api/machine-test")
def machine_test():

    # IMPORTANT:
    # There is currently no connected IoT/OT hardware.
    # Therefore this endpoint does NOT fabricate telemetry.

    with state_lock:

        system_state["modules"][
            "iot_ot"
        ] = "NOT CONNECTED"

        system_state["iot"] = {
            "status": "NOT CONNECTED",
            "sensors": 0,
            "alerts": 0,
            "temperature": None,
            "vibration": None,
            "rpm": None
        }

        system_state["industrial_ot"] = {
            "status": "NOT CONNECTED",
            "controllers": 0,
            "plcs": 0,
            "alerts": 0
        }

        update_timestamp()


    return jsonify({
        "success": True,
        "connected": False,
        "status": "NOT CONNECTED",
        "message": (
            "IoT / Industrial OT hardware "
            "is waiting for integration."
        )
    })


# ============================================================
# API: IoT STATUS
# ============================================================

@app.route("/api/iot-status")
def iot_status():

    return jsonify({
        "connected": False,
        "status": "NOT CONNECTED",
        "sensors": 0,
        "alerts": 0,
        "message": (
            "No IoT sensor hardware connected."
        )
    })


# ============================================================
# API: INDUSTRIAL OT STATUS
# ============================================================

@app.route("/api/ot-status")
def ot_status():

    return jsonify({
        "connected": False,
        "status": "NOT CONNECTED",
        "controllers": 0,
        "plcs": 0,
        "alerts": 0,
        "message": (
            "No Industrial / OT hardware connected."
        )
    })


# ============================================================
# API: AI STATUS
# ============================================================

@app.route("/api/ai-status")
def ai_status():

    with state_lock:

        monitor_status = {}

        try:
            monitor_status = (
                cyber_monitor.get_status()
            )
        except Exception:
            monitor_status = {}

        return jsonify({
            "success": True,
            "engine": (
                monitor_status.get(
                    "engine",
                    "IsolationForest"
                )
            ),
            "detection": (
                monitor_status.get(
                    "detection",
                    "SERVER-SIDE ML"
                )
            ),
            "status": "ACTIVE",
            "classification": "ACTIVE",
            "prediction": "READY",
            "response": "AUTONOMOUS",
            "last_score": (
                monitor_status.get(
                    "last_score",
                    0
                )
            ),
            "last_class": (
                monitor_status.get(
                    "last_class",
                    "NO THREAT"
                )
            )
        })


# ============================================================
# API: RESET
# ============================================================

@app.route("/api/reset", methods=["GET", "POST"])
def reset_system():

    with state_lock:

        threat_events.clear()
        quarantine_files.clear()
        investigation_records.clear()
        network_events.clear()
        endpoint_events.clear()

        system_state["risk"] = 18
        system_state["ai_risk"] = 16

        system_state["status"] = (
            "PROTECTED"
        )

        system_state["incident"] = (
            "No active incident"
        )

        system_state["modules"] = {
            "endpoint": "SECURE",
            "network": "MONITORING",
            "iot_ot": "NOT CONNECTED"
        }

        system_state["threats"] = 0
        system_state["blocked"] = 0

        system_state["severity"] = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }

        system_state["endpoint"] = {
            "cpu": 32,
            "memory": 46,
            "network_traffic": 38,
            "processes": 0,
            "status": "SECURE"
        }

        system_state["network"] = {
            "traffic": 38,
            "connections": 24,
            "status": "MONITORING",
            "devices": 18
        }

        system_state["usb"] = {
            "connected": False,
            "drive": "",
            "device": "",
            "filesystem": "",
            "status": "NOT CONNECTED",
            "scan": "WAITING",
            "files_scanned": 0,
            "suspicious": 0,
            "storage": 0,
            "anomaly_score": 0,
            "threat_class": "NONE",
            "severity": "LOW",
            "action": "NONE",
            "detection": "SERVER-SIDE ML",
            "threat_analysis": "LLM",
            "autonomous_response": "SERVER DECISION",
            "last_update": current_time()
        }

        system_state["iot"] = {
            "status": "NOT CONNECTED",
            "sensors": 0,
            "alerts": 0,
            "temperature": None,
            "vibration": None,
            "rpm": None
        }

        system_state["industrial_ot"] = {
            "status": "NOT CONNECTED",
            "controllers": 0,
            "plcs": 0,
            "alerts": 0
        }

        system_state["workflow"] = {
            "device_detected": False,
            "anomaly_detected": False,
            "threat_classified": False,
            "device_quarantined": False,
            "forensic_report": False
        }

        system_state["events"] = []

        add_event(
            event_type="SYSTEM",
            message="IronMind AI system reset.",
            severity="INFO",
            score=0,
            source="IRONMIND AI"
        )

        update_timestamp()


    return jsonify({
        "success": True,
        "message": "IronMind AI reset successfully.",
        "state": system_state
    })


# ============================================================
# API: HEALTH
# ============================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "healthy",
        "service": "IronMind AI",
        "version": "1.0",
        "ml_engine": "IsolationForest",
        "ml_detection": True,
        "server_side_ml": True,
        "usb_monitoring": True,
        "endpoint_monitoring": True,
        "network_monitoring": True,
        "threat_blocking": True,
        "quarantine_records": True,
        "investigation_records": True,
        "iot_connected": False,
        "industrial_ot_connected": False
    })


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):

    traceback.print_exc()

    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


# ============================================================
# INITIALIZATION
# ============================================================

update_timestamp()


# ============================================================
# LOCAL DEVELOPMENT
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
