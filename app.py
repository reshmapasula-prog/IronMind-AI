import hashlib
import threading
from datetime import datetime

from flask import Flask, jsonify, render_template, request

from cyber.monitor import CyberMonitor
from machine.monitor import MachineMonitor
from response.engine import ResponseEngine


# ============================================================
# IRONMIND AI
# MAIN FLASK APPLICATION
# ============================================================

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)


# ============================================================
# CORE MODULES
# ============================================================

cyber_monitor = CyberMonitor()
machine_monitor = MachineMonitor()
response_engine = ResponseEngine()

state_lock = threading.RLock()


# ============================================================
# SYSTEM STATE
# ============================================================

system_state = {

    "risk": 0,
    "ai_risk": 0,

    "status": "PROTECTED",

    "incident": "No active incident",

    "ai_engine": "ACTIVE",
    "ai_detection": "SERVER-SIDE ML",
    "ai_model": "IsolationForest",

    "modules": {
        "endpoint": "SECURE",
        "network": "MONITORING",
        "iot_ot": "NOT CONNECTED"
    },

    "threats": 0,
    "blocked": 0,

    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,

    "infrastructure": {
        "endpoints": 12,
        "cloud": 8,
        "network_devices": 18
    },

    "ai_processing": 72,

    "endpoint": {
        "cpu": 32,
        "memory": 46,
        "network_traffic": 38,
        "usb_activity": 0
    },

    "network": {
        "risk": 0,
        "status": "MONITORING",
        "events": 0
    },

    "usb": {
        "connected": False,
        "drive": "",
        "device": "USB REMOVABLE DEVICE",
        "status": "NOT CONNECTED",
        "files_scanned": 0,
        "files": [],
        "suspicious": 0,
        "anomaly_score": 0,
        "threat_class": "NONE",
        "severity": "LOW",
        "action": "NONE",
        "last_update": None
    },

    "workflow": {
        "device_detected": False,
        "files_scanned": False,
        "anomaly_score": 0,
        "threat_classified": False,
        "quarantined": False,
        "report_generated": False,
        "current_step": "WAITING"
    },

    "events": [],

    "last_update": None
}


# ============================================================
# IN-MEMORY RECORDS
# ============================================================

threat_events = []
quarantine_files = []
investigation_records = []
network_events = []
endpoint_events = []


# ============================================================
# HELPERS
# ============================================================

def update_timestamp():

    system_state["last_update"] = (
        datetime.now().isoformat()
    )


def generate_hash(filename):

    raw = (
        str(filename)
        + datetime.now().isoformat()
    ).encode("utf-8")

    return hashlib.sha256(raw).hexdigest()


def add_event(message, detail=""):

    event = {
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "detail": detail
    }

    system_state["events"].insert(
        0,
        event
    )

    system_state["events"] = (
        system_state["events"][:30]
    )


def update_threat_counters():

    system_state["critical"] = sum(
        1
        for item in threat_events
        if str(
            item.get("severity", "")
        ).upper() == "CRITICAL"
    )

    system_state["high"] = sum(
        1
        for item in threat_events
        if str(
            item.get("severity", "")
        ).upper() == "HIGH"
    )

    system_state["medium"] = sum(
        1
        for item in threat_events
        if str(
            item.get("severity", "")
        ).upper() == "MEDIUM"
    )

    system_state["low"] = sum(
        1
        for item in threat_events
        if str(
            item.get("severity", "")
        ).upper() == "LOW"
    )


# ============================================================
# SCORE CLASSIFICATION
# ============================================================

def classify_risk(score):

    score = int(score)

    if score >= 85:
        return "CRITICAL"

    elif score >= 70:
        return "HIGH"

    elif score >= 50:
        return "WARNING"

    else:
        return "NORMAL"


def get_action(score):

    score = int(score)

    # Only genuinely high-risk activity is quarantined.
    if score >= 85:
        return "QUARANTINE"

    return "MONITOR"


# ============================================================
# THREAT RECORD
# ============================================================

def create_threat_record(
    filename,
    source,
    threat_type,
    risk_score,
    severity,
    reason,
    action="QUARANTINE"
):

    now = datetime.now().isoformat()

    threat_id = (
        f"TH-{len(threat_events) + 1:05d}"
    )

    sha256 = generate_hash(
        filename
    )

    threat = {

        "id": threat_id,

        "timestamp": now,

        "filename": filename,

        "source": source,

        "threat_type": threat_type,

        "risk_score": int(risk_score),

        "severity": severity,

        "reason": reason,

        "action": action,

        "status": (
            "QUARANTINED"
            if action == "QUARANTINE"
            else "MONITORED"
        ),

        "sha256": sha256,

        "investigation_status": "AVAILABLE"
    }

    threat_events.insert(
        0,
        threat
    )

    if action == "QUARANTINE":

        quarantine_files.insert(
            0,
            {
                "id": threat_id,
                "filename": filename,
                "sha256": sha256,
                "timestamp": now,
                "status": "QUARANTINED"
            }
        )

        investigation_records.insert(
            0,
            {
                "id":
                    f"INV-{len(investigation_records)+1:05d}",

                "threat_id":
                    threat_id,

                "filename":
                    filename,

                "timestamp":
                    now,

                "status":
                    "AVAILABLE"
            }
        )

    update_threat_counters()

    return threat


# ============================================================
# FRONT PAGE
# ============================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    return render_template(
        "dashboard.html"
    )


# ============================================================
# SYSTEM STATUS
# ============================================================

@app.route("/api/status")
def api_status():

    with state_lock:

        update_timestamp()

        return jsonify(
            system_state
        )


# ============================================================
# USB STATUS
# ============================================================

@app.route("/api/usb-status")
def usb_status():

    with state_lock:

        return jsonify(
            system_state["usb"]
        )


# ============================================================
# USB EVENT
# ============================================================

@app.route(
    "/api/usb-event",
    methods=["POST"]
)
def usb_event():

    try:

        data = (
            request.get_json(
                silent=True
            )
            or {}
        )

        # ----------------------------------------------------
        # BASIC USB INFORMATION
        # ----------------------------------------------------

        connected = bool(
            data.get(
                "connected",
                False
            )
        )

        drive = str(
            data.get(
                "drive",
                ""
            )
        )

        device = data.get(
            "device"
        )

        scan = (
            data.get("scan")
            or {}
        )

        files = data.get(
            "files"
        )

        if not isinstance(
            files,
            list
        ):

            files = scan.get(
                "files",
                []
            )

        if not isinstance(
            files,
            list
        ):

            files = []


        # ====================================================
        # USB REMOVED
        # ====================================================

        if not connected:

            with state_lock:

                system_state["usb"] = {

                    "connected": False,

                    "drive": "",

                    "device":
                        "USB REMOVABLE DEVICE",

                    "status":
                        "NOT CONNECTED",

                    "files_scanned":
                        0,

                    "files":
                        [],

                    "suspicious":
                        0,

                    "anomaly_score":
                        0,

                    "threat_class":
                        "NONE",

                    "severity":
                        "LOW",

                    "action":
                        "NONE",

                    "last_update":
                        datetime.now().isoformat()
                }

                system_state["endpoint"][
                    "usb_activity"
                ] = 0

                system_state["workflow"] = {

                    "device_detected":
                        False,

                    "files_scanned":
                        False,

                    "anomaly_score":
                        0,

                    "threat_classified":
                        False,

                    "quarantined":
                        False,

                    "report_generated":
                        False,

                    "current_step":
                        "WAITING"
                }

                add_event(
                    "USB device removed",
                    "Removable media disconnected"
                )

                update_timestamp()

            return jsonify({

                "success":
                    True,

                "connected":
                    False,

                "anomaly_score":
                    0,

                "threat_class":
                    "NONE",

                "severity":
                    "NORMAL",

                "action":
                    "NONE",

                "detection":
                    "SERVER-SIDE ML"
            })


        # ====================================================
        # USB CONNECTED
        # ====================================================

        ml_test_profile = data.get(
            "ml_test_profile"
        )


        # ====================================================
        # EXISTING ML ANALYSIS
        # ====================================================

        if ml_test_profile == "IRONMIND_ANOMALY_V1":

            ml_result = (
                cyber_monitor.analyze_usb_test(
                    "IRONMIND_ANOMALY_V1"
                )
            )

        else:

            # IMPORTANT:
            # This is your existing real USB ML path.
            ml_result = (
                cyber_monitor.analyze_usb(
                    files
                )
            )


        # ====================================================
        # GET ML SCORE
        # ====================================================

        anomaly_score = int(
            ml_result.get(
                "anomaly_score",
                0
            )
            or 0
        )

        anomaly_score = max(
            0,
            min(
                100,
                anomaly_score
            )
        )


        # ====================================================
        # CLASSIFICATION BASED ON ACTUAL SCORE
        # ====================================================

        score_severity = classify_risk(
            anomaly_score
        )

        action = get_action(
            anomaly_score
        )


        # ====================================================
        # THREAT CLASS
        # ====================================================

        threat_class = str(
            ml_result.get(
                "threat_class",
                "NORMAL USB ACTIVITY"
            )
        )


        # ====================================================
        # DEVICE NAME
        # ====================================================

        if isinstance(
            device,
            dict
        ):

            device_name = str(
                device.get(
                    "name",
                    "USB REMOVABLE DEVICE"
                )
            )

        else:

            device_name = str(
                device
                or
                "USB REMOVABLE DEVICE"
            )


        # ====================================================
        # ML DETECTION FLAG
        # ====================================================

        ml_detected = bool(
            ml_result.get(
                "ml_detected",
                False
            )
        )


        # ====================================================
        # STATUS
        # ====================================================

        if action == "QUARANTINE":

            usb_status = (
                "THREAT DETECTED"
            )

        elif score_severity == "HIGH":

            usb_status = (
                "HIGH RISK - MONITORING"
            )

        elif score_severity == "WARNING":

            usb_status = (
                "WARNING - MONITORING"
            )

        else:

            usb_status = "SECURE"


        # ====================================================
        # UPDATE SYSTEM STATE
        # ====================================================

        with state_lock:

            system_state["usb"] = {

                "connected":
                    True,

                "drive":
                    drive,

                "device":
                    device_name,

                "status":
                    usb_status,

                "files_scanned":
                    len(files),

                # Store actual files so they can be displayed
                "files":
                    files,

                "suspicious":
                    (
                        1
                        if ml_detected
                        else 0
                    ),

                "anomaly_score":
                    anomaly_score,

                "threat_class":
                    threat_class,

                "severity":
                    score_severity,

                "action":
                    action,

                "last_update":
                    datetime.now().isoformat()
            }


            # ------------------------------------------------
            # ENDPOINT USB ACTIVITY
            # ------------------------------------------------

            system_state["endpoint"][
                "usb_activity"
            ] = 1


            # ------------------------------------------------
            # WORKFLOW
            # ------------------------------------------------

            system_state["workflow"] = {

                "device_detected":
                    True,

                "files_scanned":
                    True,

                "anomaly_score":
                    anomaly_score,

                "threat_classified":
                    True,

                "quarantined":
                    action == "QUARANTINE",

                "report_generated":
                    action == "QUARANTINE",

                "current_step":
                    (
                        "FORENSIC REPORT GENERATED"
                        if action == "QUARANTINE"

                        else
                        "MONITORING"
                    )
            }


            # =================================================
            # HIGH / CRITICAL THREAT
            # =================================================

            if action == "QUARANTINE":

                filename = (
                    "USB anomaly event"
                )

                if ml_test_profile:

                    filename = (
                        "IRONMIND_TEST_10.txt"
                    )

                elif files:

                    first_file = files[0]

                    if isinstance(
                        first_file,
                        dict
                    ):

                        filename = str(
                            first_file.get(
                                "name",
                                filename
                            )
                        )


                threat = create_threat_record(

                    filename=
                        filename,

                    source=
                        "USB DRIVE",

                    threat_type=
                        threat_class,

                    risk_score=
                        anomaly_score,

                    severity=
                        score_severity,

                    reason=(
                        "Existing IronMind ML "
                        "analysis classified "
                        "removable-media activity "
                        "as critical risk."
                    ),

                    action=
                        "QUARANTINE"
                )


                system_state["risk"] = (
                    anomaly_score
                )

                system_state["ai_risk"] = (
                    anomaly_score
                )

                system_state["status"] = (
                    "THREAT BLOCKED"
                )

                system_state["modules"][
                    "endpoint"
                ] = (
                    "THREAT BLOCKED"
                )

                system_state["threats"] = (
                    len(threat_events)
                )

                system_state["blocked"] = sum(

                    1

                    for item in threat_events

                    if item.get("action")
                    == "QUARANTINE"
                )

                system_state["incident"] = (

                    f"{threat_class} detected "
                    f"on removable media"
                )

                add_event(

                    "USB critical threat detected",

                    (
                        f"ML anomaly score "
                        f"{anomaly_score}% • "
                        f"{score_severity} • "
                        f"{threat_class} • "
                        f"QUARANTINE"
                    )
                )


            # =================================================
            # HIGH RISK — MONITOR
            # =================================================

            elif score_severity == "HIGH":

                system_state["risk"] = (
                    anomaly_score
                )

                system_state["ai_risk"] = (
                    anomaly_score
                )

                system_state["status"] = (
                    "HIGH RISK - MONITORING"
                )

                system_state["modules"][
                    "endpoint"
                ] = (
                    "MONITORING"
                )

                system_state["incident"] = (
                f"High-risk USB activity "
                    f"detected"
                )

                add_event(

                    "USB high-risk activity",

                    (
                        f"ML anomaly score "
                        f"{anomaly_score}% • "
                        f"HIGH • "
                        f"{threat_class} • "
                        f"MONITORING"
                    )
                )


            # =================================================
            # WARNING
            # =================================================

            elif score_severity == "WARNING":

                system_state["risk"] = (
                    anomaly_score
                )

                system_state["ai_risk"] = (
                    anomaly_score
                )

                system_state["status"] = (
                    "WARNING"
                )

                system_state["modules"][
                    "endpoint"
                ] = (
                    "MONITORING"
                )

                system_state["incident"] = (
                    "USB activity requires monitoring"
                )

                add_event(

                    "USB warning",

                    (
                        f"ML anomaly score "
                        f"{anomaly_score}% • "
                        f"WARNING • "
                        f"{threat_class}"
                    )
                )


            # =================================================
            # NORMAL
            # =================================================

            else:

                system_state["risk"] = (
                    anomaly_score
                )

                system_state["ai_risk"] = (
                    anomaly_score
                )

                system_state["status"] = (
                    "PROTECTED"
                )

                system_state["modules"][
                    "endpoint"
                ] = (
                    "SECURE"
                )

                system_state["incident"] = (
                    "No active endpoint incident"
                )

                add_event(

                    "USB analyzed",

                    (
                        f"ML anomaly score "
                        f"{anomaly_score}% • "
                        f"NORMAL • "
                        f"{threat_class}"
                    )
                )


            update_timestamp()


        # ====================================================
        # RESPONSE TO USB AGENT
        # ====================================================

        response = {

            "success":
                True,

            "connected":
                True,

            "drive":
                drive,

            "device":
                device_name,

            "files_scanned":
                len(files),

            "files":
                files,

            "anomaly_score":
                anomaly_score,

            "threat_class":
                threat_class,

            "severity":
                score_severity,

            "action":
                action,

            "ml_detected":
                ml_detected,

            "detection":
                "SERVER-SIDE ML",

            "threat_analysis":
                "SERVER-SIDE",

            "workflow":
                system_state["workflow"]
        }


        print(
            "[IRONMIND] USB ML event: "
            f"{anomaly_score}% | "
            f"{score_severity} | "
            f"{threat_class} | "
            f"{action}"
        )


        return jsonify(
            response
        )


    except Exception as error:

        print(
            "[IRONMIND] USB event error:",
            error
        )

        return jsonify({

            "success":
                False,

            "anomaly_score":
                0,

            "threat_class":
                "ANALYSIS ERROR",

            "severity":
                "UNKNOWN",

            "action":
                "MONITOR",

            "detection":
                "SERVER-SIDE ML",

            "error":
                str(error)

        }), 500


# ============================================================
# THREATS
# ============================================================

@app.route("/api/threats")
def get_threats():

    with state_lock:

        return jsonify(
            threat_events
        )


# ============================================================
# QUARANTINE
# ============================================================

@app.route("/api/quarantine")
def get_quarantine():

    with state_lock:

        return jsonify(
            quarantine_files
        )


# ============================================================
# INVESTIGATIONS
# ============================================================

@app.route("/api/investigations")
def get_investigations():

    with state_lock:

        return jsonify(
            investigation_records
        )


# ============================================================
# NETWORK EVENTS
# ============================================================

@app.route("/api/network-events")
def get_network_events():

    with state_lock:

        return jsonify(
            network_events
        )


# ============================================================
# ENDPOINT EVENTS
# ============================================================

@app.route("/api/endpoint-events")
def get_endpoint_events():

    with state_lock:

        return jsonify(
            endpoint_events
        )


# ============================================================
# USB ML TEST
# ============================================================

@app.route(
    "/api/usb-threat-test",
    methods=["GET", "POST"]
)
def usb_threat_test():

    with state_lock:

        ml_result = (
            cyber_monitor.analyze_usb_test(
                "IRONMIND_ANOMALY_V1"
            )
        )

        score = int(
            ml_result.get(
                "anomaly_score",
                94
            )
        )

        score = max(
            0,
            min(
                100,
                score
            )
        )

        threat_class = ml_result.get(
            "threat_class",
            "SUSPICIOUS USB CONTENT"
        )

        severity = classify_risk(
            score
        )

        action = get_action(
            score
        )

        threat = None

        if action == "QUARANTINE":

            threat = create_threat_record(

                filename=
                    "IRONMIND_TEST_10.txt",

                source=
                    "USB DRIVE",

                threat_type=
                    threat_class,

                risk_score=
                    score,

                severity=
                    severity,

                reason=
                    "Harmless IronMind "
                    "ML demonstration profile.",

                action=
                    "QUARANTINE"
            )


        system_state["risk"] = score

        system_state["ai_risk"] = score

        system_state["status"] = (

            "THREAT BLOCKED"

            if action == "QUARANTINE"

            else
            "MONITORING"
        )

        system_state["modules"][
            "endpoint"
        ] = (

            "THREAT BLOCKED"

            if action == "QUARANTINE"

            else
            "MONITORING"
        )

        system_state["threats"] = (
            len(threat_events)
        )

        system_state["blocked"] = sum(

            1

            for item in threat_events

            if item.get("action")
            == "QUARANTINE"
        )

        system_state["usb"] = {

            "connected":
                True,

            "drive":
                "TEST USB",

            "device":
                "IRONMIND TEST USB",

            "status":
                (
                    "THREAT DETECTED"
                    if action == "QUARANTINE"
                    else "HIGH RISK - MONITORING"
                ),

            "files_scanned":
                1,

            "files":
                [
                    {
                        "name":
                            "IRONMIND_TEST_10.txt"
                    }
                ],

            "suspicious":
                1,

            "anomaly_score":
                score,

            "threat_class":
                threat_class,

            "severity":
                severity,

            "action":
                action,

            "last_update":
                datetime.now().isoformat()
        }

        system_state["workflow"] = {

            "device_detected":
                True,

            "files_scanned":
                True,

            "anomaly_score":
                score,

            "threat_classified":
                True,

            "quarantined":
                action == "QUARANTINE",

            "report_generated":
                action == "QUARANTINE",

            "current_step":
                (
                    "FORENSIC REPORT GENERATED"
                    if action == "QUARANTINE"
                    else "MONITORING"
                )
        }

        system_state["incident"] = (

            "IronMind ML demonstration incident"

            if action == "QUARANTINE"

            else
            "IronMind ML demonstration monitoring"
        )

        add_event(

            "USB ML demonstration",

            (
                f"Anomaly score "
                f"{score}% • "
                f"{severity} • "
                f"{action}"
            )
        )

        update_timestamp()

        return jsonify({

            "success":
                True,

            "anomaly_score":
                score,

            "threat_class":
                threat_class,

            "severity":
                severity,

            "action":
                action,

            "threat":
                threat,

            "state":
                system_state
        })


# ============================================================
# ENDPOINT TEST
# ============================================================

@app.route(
    "/api/endpoint-test",
    methods=["GET", "POST"]
)
def endpoint_test():

    with state_lock:

        result = (
            cyber_monitor.analyze_usb(
                [
                    {
                        "name":
                            "endpoint-test",

                        "extension":
                            ".telemetry",

                        "size":
                            1000000,

                        "is_hidden":
                            False,

                        "is_system":
                            False,

                        "is_executable":
                            False
                    },

                    {
                        "name":
                            "process-profile",

                        "extension":
                            ".telemetry",

                        "size":
                            1000000,

                        "is_hidden":
                            True,

                        "is_system":
                            False,

                        "is_executable":
                            True
                    }
                ]
            )
        )

        score = max(
            70,
            int(
                result.get(
                    "anomaly_score",
                    70
                )
            )
        )

        endpoint_events.insert(
            0,
            {
                "id":
                    f"EP-{len(endpoint_events)+1:05d}",

                "timestamp":
                    datetime.now().isoformat(),

                "source":
                    "LOCAL ENDPOINT",

                "event":
                    "Synthetic endpoint anomaly test",

                "risk_score":
                    score,

                "action":
                    "BLOCKED"
                    if score >= 70
                    else "MONITORED"
            }
        )

        system_state["risk"] = score

        system_state["ai_risk"] = score

        system_state["status"] = (
            "THREAT BLOCKED"
        )

        system_state["modules"][
            "endpoint"
        ] = (
            "THREAT BLOCKED"
        )

        system_state["endpoint"]["cpu"] = 91

        system_state["endpoint"]["memory"] = 78

        system_state["incident"] = (
            "Endpoint anomaly detected"
        )

        add_event(
            "Endpoint anomaly",
            f"ML test score {score}%"
        )

        update_timestamp()

        return jsonify({

            "success":
                True,

            "anomaly_score":
                score,

            "state":
                system_state
        })


# ============================================================
# NETWORK TEST
# ============================================================

@app.route(
    "/api/network-test",
    methods=["GET", "POST"]
)
def network_test():

    with state_lock:

        result = (
            cyber_monitor.analyze_usb(
                [
                    {
                        "name":
                            "network-traffic",

                        "extension":
                            ".net",

                        "size":
                            5000000,

                        "is_hidden":
                            True,

                        "is_system":
                            False,

                        "is_executable":
                            True
                    },

                    {
                        "name":
                            "connection-profile",

                        "extension":
                            ".net",

                        "size":
                            9000000,

                        "is_hidden":
                            True,

                        "is_system":
                            True,

                        "is_executable":
                            True
                    }
                ]
            )
        )

        score = max(
            70,
            int(
                result.get(
                    "anomaly_score",
                    70
                )
            )
        )

        network_events.insert(
            0,
            {
                "id":
                    f"NET-{len(network_events)+1:05d}",

                "timestamp":
                    datetime.now().isoformat(),

                "source":
                    "NETWORK",

                "event":
                    "Synthetic network anomaly test",

                "risk_score":
                    score,

                "action":
                    "BLOCKED"
                    if score >= 70
                    else "MONITORED"
            }
        )

        system_state["network"] = {

            "risk":
                score,

            "status":
                "THREAT BLOCKED",

            "events":
                len(network_events)
        }

        system_state["modules"][
            "network"
        ] = "THREAT BLOCKED"

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

        system_state["incident"] = (
            "Network anomaly detected"
        )

        add_event(
            "Network anomaly",
            f"ML test score {score}%"
        )

        update_timestamp()

        return jsonify({

            "success":
                True,

            "anomaly_score":
                score,

            "state":
                system_state
        })


# ============================================================
# CYBER TEST
# ============================================================

@app.route(
    "/api/cyber-test",
    methods=["GET", "POST"]
)
def cyber_test():

    return network_test()


# ============================================================
# MACHINE / IoT TEST
# ============================================================

@app.route(
    "/api/machine-test",
    methods=["GET", "POST"]
)
def machine_test():

    with state_lock:

        result = (
            machine_monitor.detect_anomaly()
        )

        return jsonify({

            "success":
                True,

            "connected":
                False,

            "status":
                "NOT CONNECTED",

            "message":
                "IoT / Industrial OT "
                "hardware is not connected.",

            "machine":
                result
        })


# ============================================================
# RESET
# ============================================================

@app.route(
    "/api/reset",
    methods=["GET", "POST"]
)
def reset_system():

    with state_lock:

        threat_events.clear()

        quarantine_files.clear()

        investigation_records.clear()

        network_events.clear()

        endpoint_events.clear()


        system_state["risk"] = 0

        system_state["ai_risk"] = 0

        system_state["status"] = (
            "PROTECTED"
        )

        system_state["incident"] = (
            "No active incident"
        )

        system_state["threats"] = 0

        system_state["blocked"] = 0

        system_state["critical"] = 0

        system_state["high"] = 0

        system_state["medium"] = 0

        system_state["low"] = 0


        system_state["modules"] = {

            "endpoint":
                "SECURE",

            "network":
                "MONITORING",

            "iot_ot":
                "NOT CONNECTED"
        }


        system_state["network"] = {

            "risk":
                0,

            "status":
                "MONITORING",

            "events":
                0
        }


        system_state["endpoint"] = {

            "cpu":
                32,

            "memory":
                46,

            "network_traffic":
                38,

            "usb_activity":
                0
        }


        system_state["usb"] = {

            "connected":
                False,

            "drive":
                "",

            "device":
                "USB REMOVABLE DEVICE",

            "status":
                "NOT CONNECTED",

            "files_scanned":
                0,

            "files":
                [],

            "suspicious":
                0,

            "anomaly_score":
                0,

            "threat_class":
                "NONE",

            "severity":
                "LOW",

            "action":
                "NONE",

            "last_update":
                datetime.now().isoformat()
        }


        system_state["workflow"] = {

            "device_detected":
                False,

            "files_scanned":
                False,

            "anomaly_score":
                0,

            "threat_classified":
                False,

            "quarantined":
                False,

            "report_generated":
                False,

            "current_step":
                "WAITING"
        }


        system_state["events"] = []


        cyber_monitor.reset()

        machine_monitor.reset()

        response_engine.reset()


        add_event(
            "System reset",
            "IronMind defense state restored"
        )

        update_timestamp()


        return jsonify({

            "success":
               True,

            "state":
                system_state
        })


# ============================================================
# HEALTH
# ============================================================

@app.route("/health")
def health():

    return jsonify({

        "status":
            "healthy",

        "service":
            "IronMind AI",

        "ml_engine":
            "IsolationForest",

        "usb_monitoring":
            True,

        "endpoint_monitoring":
            True,

        "network_monitoring":
            True,

        "threat_blocking":
            True,

        "investigation":
            True,

        "iot_connected":
            False,

        "industrial_ot_connected":
            False
    })


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
