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

        "suspicious": 0,

        "anomaly_score": 0,

        "threat_class": "NONE",

        "severity": "LOW",

        "action": "NONE",

        "files": [],

        "suspicious_files": [],

        "last_update": None
    },

    "workflow": {

        "device_detected": False,

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
# DATABASE-LIKE IN-MEMORY RECORDS
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

        "timestamp":
            datetime.now().isoformat(),

        "message":
            message,

        "detail":
            detail
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
# FILE NORMALIZATION
# ============================================================

def normalize_usb_file(file_item):

    """
    Keeps the REAL file information received
    from the local USB agent.

    No fake filenames are generated here.
    """

    if isinstance(file_item, str):

        name = file_item

        return {
            "name": name,
            "extension": "",
            "size": 0,
            "is_hidden": False,
            "is_system": False,
            "is_executable": False,
            "suspicious": False,
            "status": "ANALYZED"
        }

    if not isinstance(file_item, dict):

        return {
            "name": str(file_item),
            "extension": "",
            "size": 0,
            "is_hidden": False,
            "is_system": False,
            "is_executable": False,
            "suspicious": False,
            "status": "ANALYZED"
        }

    name = str(
        file_item.get(
            "name",
            file_item.get(
                "filename",
                "UNKNOWN FILE"
            )
        )
    )

    extension = str(
        file_item.get(
            "extension",
            ""
        )
    ).lower()

    suspicious = bool(
        file_item.get(
            "suspicious",
            False
        )
    )

    status = str(
        file_item.get(
            "status",
            "SUSPICIOUS"
            if suspicious
            else "ANALYZED"
        )
    ).upper()

    return {

        "name": name,

        "extension": extension,

        "size": file_item.get(
            "size",
            0
        ),

        "is_hidden": bool(
            file_item.get(
                "is_hidden",
                False
            )
        ),

        "is_system": bool(
            file_item.get(
                "is_system",
                False
            )
        ),

        "is_executable": bool(
            file_item.get(
                "is_executable",
                False
            )
        ),

        "suspicious": suspicious,

        "status": status
    }


def get_suspicious_files(files):

    """
    Uses information supplied by the USB agent.

    A file is treated as suspicious only when the
    agent explicitly marks it suspicious.

    We do NOT label every executable file as malware.
    """

    suspicious_files = []

    for file_item in files:

        if not isinstance(
            file_item,
            dict
        ):
            continue

        if bool(
            file_item.get(
                "suspicious",
                False
            )
        ):

            suspicious_files.append(
                file_item
            )

    return suspicious_files


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

        "id":
            threat_id,

        "timestamp":
            now,

        "filename":
            filename,

        "source":
            source,

        "threat_type":
            threat_type,

        "risk_score":
            int(risk_score),

        "severity":
            severity,

        "reason":
            reason,

        "action":
            action,

        "status":
            (
                "QUARANTINED"
                if action == "QUARANTINE"
                else "MONITORED"
            ),

        "sha256":
            sha256,

        "investigation_status":
            "AVAILABLE"
    }

    threat_events.insert(
        0,
        threat
    )

    if action == "QUARANTINE":

        quarantine_files.insert(
            0,
            {

                "id":
                    threat_id,

                "filename":
                    filename,

                "sha256":
                    sha256,

                "timestamp":
                    now,

                "status":
                    "QUARANTINED"
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
# SOC DASHBOARD
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

                    "files":
                        [],

                    "suspicious_files":
                        [],

                    "last_update":
                        datetime.now().isoformat()
                }

                system_state["endpoint"][
                    "usb_activity"
                ] = 0

                system_state["workflow"] = {

                    "device_detected":
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
                    "LOW",

                "action":
                    "NONE",

                "files":
                    [],

                "detection":
                    "SERVER-SIDE ML"
            })


        # ====================================================
        # NORMALIZE REAL FILE DATA
        # ====================================================

        normalized_files = []

        for item in files:

            normalized_files.append(
                normalize_usb_file(item)
            )

        suspicious_files = (
            get_suspicious_files(
                normalized_files
            )
        )


        # ====================================================
        # ML ANALYSIS
        # ====================================================

        ml_test_profile = data.get(
            "ml_test_profile"
        )

        if ml_test_profile == (
            "IRONMIND_ANOMALY_V1"
        ):

            ml_result = (
                cyber_monitor.analyze_usb_test(
                    "IRONMIND_ANOMALY_V1"
                )
            )

        else:

            ml_result = (
                cyber_monitor.analyze_usb(
                    normalized_files
                )
            )


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
        )

        ml_detected = bool(
            ml_result.get(
                "ml_detected",
                False
            )
        )


        # ====================================================
        # SERVER RESPONSE
        # ====================================================

        if anomaly_score >= 70:

            action = "QUARANTINE"

            usb_status = (
                "THREAT DETECTED"
            )

        else:

            action = "MONITOR"

            usb_status = "SECURE"


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
        # UPDATE USB STATE
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
                    len(normalized_files),

                "suspicious":
                    len(suspicious_files),

                "anomaly_score":
                    anomaly_score,

                "threat_class":
                    threat_class,

                "severity":
                    severity,

                "action":
                    action,

                "files":
                    normalized_files,

                "suspicious_files":
                    suspicious_files,

                "last_update":
                    datetime.now().isoformat()
            }


            system_state["endpoint"][
                "usb_activity"
            ] = 1


            system_state["workflow"] = {

                "device_detected":
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
                        else "MONITORING"
                    )
            }


            # =================================================
            # HIGH-RISK USB
            # =================================================

            if anomaly_score >= 70:

                created_records = []

                # ---------------------------------------------
                # REAL SUSPICIOUS FILES
                # ---------------------------------------------

                for suspicious_file in suspicious_files:

                    filename = str(
                        suspicious_file.get(
                            "name",
                            "UNKNOWN FILE"
                        )
                    )

                    threat = (
                        create_threat_record(

                            filename=
                                filename,

                            source=
                                "USB DRIVE",

                            threat_type=
                                threat_class,

                            risk_score=
                                anomaly_score,

                            severity=
                                severity,

                            reason=(
                                "File was identified "
                                "as suspicious by the "
                                "USB security agent "
                                "and the USB activity "
                                "received a high ML "
                                "anomaly score."
                            ),

                            action=
                                "QUARANTINE"
                        )
                    )

                    created_records.append(
                        threat
                    )


                # ---------------------------------------------
                # IF NO INDIVIDUAL FILE WAS FLAGGED
                # ---------------------------------------------
                #
                # We create ONE device-level record.
                #
                # We do NOT falsely mark every file as malware.
                # ---------------------------------------------

                if not created_records:

                    threat = (
                        create_threat_record(

                            filename=
                                f"{drive or 'USB'} "
                                "device-level anomaly",

                            source=
                                "USB DRIVE",

                            threat_type=
                                threat_class,

                            risk_score=
                                anomaly_score,

                            severity=
                                severity,

                            reason=(
                                "Server-side ML anomaly "
                                "detection identified "
                                "abnormal removable-media "
                                "telemetry. Individual "
                                "files were not separately "
                                "flagged."
                            ),

                            action=
                                "QUARANTINE"
                        )
                    )

                    created_records.append(
                        threat
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
                ] = "THREAT BLOCKED"

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

                    "USB threat detected",

                    (
                        f"ML anomaly score "
                        f"{anomaly_score}% • "
                        f"{threat_class} • "
                        f"{len(normalized_files)} "
                        f"files scanned • "
                        f"{len(suspicious_files)} "
                        f"suspicious files"
                    )
                )


            # =================================================
            # NORMAL USB
            # =================================================

            else:

                system_state["ai_risk"] = (
                    anomaly_score
                )

                system_state["status"] = (
                    "PROTECTED"
                )

                system_state["modules"][
                    "endpoint"
                ] = "SECURE"

                system_state["incident"] = (
                    "No active endpoint incident"
                )

                add_event(

                    "USB analyzed",

                    (
                        f"ML anomaly score "
                        f"{anomaly_score}% • "
                        f"{len(normalized_files)} "
                        f"files scanned • "
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
                len(normalized_files),

            "suspicious_files":
                len(suspicious_files),

            "files":
                normalized_files,

            "suspicious_file_details":
                suspicious_files,

            "anomaly_score":
                anomaly_score,

            "threat_class":
                threat_class,

            "severity":
                severity,

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
            f"{threat_class} | "
            f"{action} | "
            f"Files: {len(normalized_files)} | "
            f"Suspicious: {len(suspicious_files)}"
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

        threat_class = ml_result.get(
            "threat_class",
            "SUSPICIOUS USB CONTENT"
        )

        severity = ml_result.get(
            "severity",
            "CRITICAL"
        )

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

            reason=(
                "Harmless IronMind ML "
                "demonstration profile."
            ),

            action=
                "QUARANTINE"
        )

        system_state["risk"] = score

        system_state["ai_risk"] = score

        system_state["status"] = (
            "THREAT BLOCKED"
        )

        system_state["modules"][
            "endpoint"
        ] = "THREAT BLOCKED"

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
                "THREAT DETECTED",

            "files_scanned":
                1,

            "suspicious":
                1,

            "anomaly_score":
                score,

            "threat_class":
                threat_class,

            "severity":
                severity,

            "action":
                "QUARANTINE",

            "files": [

                {
                    "name":
                        "IRONMIND_TEST_10.txt",

                    "extension":
                        ".txt",

                    "size":
                        0,

                    "suspicious":
                        True,

                    "status":
                        "SUSPICIOUS"
                }

            ],

            "suspicious_files": [

                {
                    "name":
                        "IRONMIND_TEST_10.txt",

                    "extension":
                        ".txt",

                    "suspicious":
                        True,

                    "status":
                        "SUSPICIOUS"
                }

            ],

            "last_update":
                datetime.now().isoformat()
        }

        system_state["workflow"] = {

            "device_detected":
                True,

            "anomaly_score":
                score,

            "threat_classified":
                True,

            "quarantined":
                True,

            "report_generated":
                True,

            "current_step":
                "FORENSIC REPORT GENERATED"
        }

        system_state["incident"] = (
            "IronMind ML demonstration "
            "incident"
        )

        add_event(
            "USB ML demonstration",
            f"Anomaly score {score}%"
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
                "QUARANTINE",

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
                    (
                        "BLOCKED"
                        if score >= 70
                        else "MONITORED"
                    )
            }
        )

        system_state["risk"] = score

        system_state["ai_risk"] = score

        system_state["status"] = (
            "THREAT BLOCKED"
        )

        system_state["modules"][
            "endpoint"
        ] = "THREAT BLOCKED"

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
                    (
                        "BLOCKED"
                        if score >= 70
                        else "MONITORED"
                    )
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
                (
                    "IoT / Industrial OT "
                    "hardware is not connected."
                ),

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
            "files":
                [],

            "suspicious_files":
                [],

            "last_update":
                datetime.now().isoformat()
        }


        system_state["workflow"] = {

            "device_detected":
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
             
