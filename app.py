from flask import Flask, render_template, jsonify, request
from datetime import datetime
import random
import threading
import hashlib
import os
import uuid


# ============================================================
# IRONMIND AI
# Autonomous AI Cyber Defense Platform
#
# USB + Endpoint + Network + Investigation
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

    # --------------------------------------------------------
    # General
    # --------------------------------------------------------

    "risk": 18,
    "ai_risk": 16,
    "status": "PROTECTED",
    "incident": "No active security incident",
    "ai_engine": "ACTIVE",

    # --------------------------------------------------------
    # Security modules
    # --------------------------------------------------------

    "endpoint": "SECURE",
    "network": "MONITORING",
    "iot_ot": "MONITORING",

    # --------------------------------------------------------
    # Threat information
    # --------------------------------------------------------

    "threats": 0,
    "blocked": 0,

    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,

    # --------------------------------------------------------
    # Infrastructure
    # --------------------------------------------------------

    "endpoints": 12,
    "cloud": 8,
    "network_devices": 18,

    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    "ai_processing": 72,

    # --------------------------------------------------------
    # Endpoint telemetry
    # --------------------------------------------------------

    "cpu": 32,
    "memory": 46,
    "network_traffic": 38,
    "usb_activity": "NO USB EVENT",

    # --------------------------------------------------------
    # Machine / IoT
    # --------------------------------------------------------

    "machine_temperature": 42.5,
    "machine_vibration": 1.2,
    "machine_rpm": 1498,

    # --------------------------------------------------------
    # USB
    # --------------------------------------------------------

    "usb_connected": False,
    "usb_drive": "",
    "usb_event": "NO USB EVENT",
    "usb_time": "",

    # --------------------------------------------------------
    # Event system
    # --------------------------------------------------------

    "events": 0,

    # --------------------------------------------------------
    # Last update
    # --------------------------------------------------------

    "last_update": datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
}


# ============================================================
# USB STATE
# ============================================================

usb_state = {

    "connected": False,
    "status": "WAITING",
    "device": None,
    "scan": None,
    "last_update": None
}


# ============================================================
# THREAT DATABASE
# ============================================================
#
# In production this would be stored in a database.
# For the current prototype it stays in memory.
#
# IMPORTANT:
# These records remain available for investigation even
# after the threat has been blocked.
# ============================================================

threat_events = []


# ============================================================
# QUARANTINE DATABASE
# ============================================================

quarantine_files = []


# ============================================================
# INVESTIGATION DATABASE
# ============================================================

investigation_records = []


# ============================================================
# NETWORK EVENTS
# ============================================================

network_events = []


# ============================================================
# ENDPOINT EVENTS
# ============================================================

endpoint_events = []


# ============================================================
# DEMO MODE
# ============================================================

demo_mode = "normal"


# ============================================================
# TIMESTAMP
# ============================================================

def update_timestamp():

    system_state["last_update"] = (
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )


# ============================================================
# HASH GENERATOR
# ============================================================

def generate_hash(filename):

    value = (
        filename +
        datetime.now().isoformat()
    ).encode()

    return hashlib.sha256(value).hexdigest()


# ============================================================
# ADD THREAT EVENT
# ============================================================

def add_threat_event(
    filename,
    threat_type,
    risk_score,
    severity,
    source="USB",
    reason="Suspicious behavior detected"
):

    event_id = str(uuid.uuid4())[:8]

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    file_hash = generate_hash(filename)

    threat = {

        "id": event_id,

        "timestamp": timestamp,

        "filename": filename,

        "source": source,

        "threat_type": threat_type,

        "risk_score": risk_score,

        "severity": severity,

        "reason": reason,

        "action": "BLOCKED",

        "status": "QUARANTINED",

        "sha256": file_hash,

        "investigation_status": "AVAILABLE"
    }

    threat_events.insert(
        0,
        threat
    )

    # --------------------------------------------------------
    # QUARANTINE RECORD
    # --------------------------------------------------------

    quarantine_record = {

        "id": event_id,

        "filename": filename,

        "source": source,

        "sha256": file_hash,

        "risk_score": risk_score,

        "severity": severity,

        "status": "QUARANTINED",

        "blocked": True,

        "timestamp": timestamp
    }

    quarantine_files.insert(
        0,
        quarantine_record
    )

    # --------------------------------------------------------
    # INVESTIGATION RECORD
    # --------------------------------------------------------

    investigation_record = {

        "id": event_id,

        "filename": filename,

        "threat_type": threat_type,

        "severity": severity,

        "risk_score": risk_score,

        "source": source,

        "reason": reason,

        "sha256": file_hash,

        "action": "BLOCKED",

        "status": "QUARANTINED",

        "timestamp": timestamp,

        "investigation_status": "READY FOR INVESTIGATION"
    }

    investigation_records.insert(
        0,
        investigation_record
    )

    return threat


# ============================================================
# UPDATE THREAT COUNTERS
# ============================================================

def update_threat_counters():

    critical = 0
    high = 0
    medium = 0
    low = 0

    for threat in threat_events:
        severity = threat.get(
            "severity",
            ""
        ).upper()

        if severity == "CRITICAL":
            critical += 1

        elif severity == "HIGH":
            high += 1

        elif severity == "MEDIUM":
            medium += 1

        elif severity == "LOW":
            low += 1

    system_state["critical"] = critical
    system_state["high"] = high
    system_state["medium"] = medium
    system_state["low"] = low

    system_state["threats"] = len(
        threat_events
    )

    system_state["blocked"] = len(
        quarantine_files
    )


# ============================================================
# PROCESS USB THREAT
# ============================================================

def process_usb_threat(
    filename="invoice.exe"
):

    with state_lock:

        threat = add_threat_event(

            filename=filename,

            threat_type="SUSPICIOUS EXECUTABLE",

            risk_score=94,

            severity="CRITICAL",

            source="USB DRIVE",

            reason=(
                "Executable detected from removable media "
                "with high-risk characteristics"
            )
        )

        system_state["risk"] = 96

        system_state["ai_risk"] = 94

        system_state["status"] = (
            "THREAT BLOCKED"
        )

        system_state["incident"] = (

            f"CRITICAL USB THREAT BLOCKED: "
            f"{filename}"
        )

        system_state["endpoint"] = (
            "THREAT BLOCKED"
        )

        system_state["network"] = (
            "MONITORING"
        )

        system_state["usb_event"] = (
            "HIGH-RISK FILE BLOCKED"
        )

        system_state["usb_activity"] = (
            "THREAT BLOCKED"
        )

        system_state["events"] += 1

        update_threat_counters()

        update_timestamp()

        return threat


# ============================================================
# NORMAL LIVE DATA
# ============================================================

def generate_live_data():

    global demo_mode

    with state_lock:

        # ====================================================
        # NORMAL
        # ====================================================

        if demo_mode == "normal":

            system_state["risk"] = random.randint(
                10,
                28
            )

            system_state["ai_risk"] = random.randint(
                8,
                25
            )

            system_state["endpoint"] = (
                "SECURE"
            )

            system_state["network"] = (
                "MONITORING"
            )

            system_state["iot_ot"] = (
                "MONITORING"
            )

            system_state["cpu"] = random.randint(
                20,
                55
            )

            system_state["memory"] = random.randint(
                35,
                65
            )

            system_state["network_traffic"] = random.randint(
                20,
                55
            )

            system_state["machine_temperature"] = round(
                random.uniform(
                    38,
                    48
                ),
                1
            )

            system_state["machine_vibration"] = round(
                random.uniform(
                    0.8,
                    1.8
                ),
                1
            )

            system_state["machine_rpm"] = random.randint(
                1450,
                1550
            )

            system_state["status"] = (
                "PROTECTED"
            )

            system_state["incident"] = (
                "No active security incident"
            )

            system_state["usb_activity"] = (
                "NO USB EVENT"
            )

        # ====================================================
        # CYBER TEST
        # ====================================================

        elif demo_mode == "cyber":

            system_state["risk"] = random.randint(
                75,
                95
            )

            system_state["ai_risk"] = random.randint(
                78,
                97
            )

            system_state["endpoint"] = (
                "THREAT DETECTED"
            )

            system_state["network"] = (
                "ANALYZING"
            )

            system_state["status"] = (
                "UNDER ATTACK"
            )

            system_state["incident"] = (
                "Cybersecurity test event detected"
            )

            system_state["cpu"] = random.randint(
                55,
                90
            )

            system_state["memory"] = random.randint(
                55,
                85
            )

            system_state["network_traffic"] = random.randint(
                60,
                95
            )

        # ====================================================
        # MACHINE TEST
        # ====================================================

        elif demo_mode == "machine":

            system_state["risk"] = random.randint(
                55,
                85
            )

            system_state["ai_risk"] =random.randint(
                60,
                90
            )

            system_state["machine_temperature"] = round(
                random.uniform(
                    65,
                    85
                ),
                1
            )

            system_state["machine_vibration"] = round(
                random.uniform(
                    4.0,
                    7.0
                ),
                1
            )

            system_state["machine_rpm"] = random.randint(
                1050,
                1250
            )

            system_state["endpoint"] = (
                "SECURE"
            )

            system_state["network"] = (
                "MONITORING"
            )

            system_state["iot_ot"] = (
                "ANOMALY DETECTED"
            )

            system_state["status"] = (
                "MACHINE ANOMALY"
            )

            system_state["incident"] = (
                "Machine telemetry anomaly detected"
            )

        update_threat_counters()

        update_timestamp()


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

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
# STATUS
# ============================================================

@app.route("/api/status")
def api_status():

    generate_live_data()

    with state_lock:

        data = dict(
            system_state
        )

    return jsonify(data)


# ============================================================
# USB STATUS
# ============================================================

@app.route("/api/usb-status")
def usb_status():

    with state_lock:

        data = dict(
            usb_state
        )

    return jsonify(data)


# ============================================================
# USB EVENT
# ============================================================

@app.route(
    "/api/usb-event",
    methods=["POST"]
)
def usb_event():

    data = request.get_json(
        silent=True
    ) or {}

    # ========================================================
    # NEW FORMAT
    # ========================================================

    if "connected" in data:

        connected = bool(
            data.get(
                "connected",
                False
            )
        )
        status = data.get(
            "status",
            "UNKNOWN"
        )

        device = data.get(
            "device"
        )

        scan = data.get(
            "scan"
        )

        timestamp = data.get(
            "timestamp",
            datetime.now().isoformat()
        )

        with state_lock:

            usb_state["connected"] = (
                connected
            )

            usb_state["status"] = (
                status
            )

            usb_state["device"] = (
                device
            )

            usb_state["scan"] = (
                scan
            )

            usb_state["last_update"] = (
                timestamp
            )

            system_state[
                "usb_connected"
            ] = connected

            if device:

                system_state[
                    "usb_drive"
                ] = device.get(
                    "drive",
                    ""
                )

            system_state[
                "usb_time"
            ] = timestamp

            if connected:

                system_state[
                    "usb_event"
                ] = (
                    "USB DEVICE DETECTED"
                )

                system_state[
                    "usb_activity"
                ] = (
                    "USB DEVICE CONNECTED"
                )

                # --------------------------------------------
                # SUSPICIOUS FILE DETECTION
                # --------------------------------------------

                suspicious_count = 0

                if scan:

                    suspicious_count = int(
                        scan.get(
                            "suspicious_count",
                            0
                        )
                    )

                if suspicious_count > 0:

                    filename = (
                        scan.get(
                            "filename",
                            "invoice.exe"
                        )
                        if scan
                        else
                        "invoice.exe"
                    )

                    threat = process_usb_threat(
                        filename
                    )

                else:

                    system_state[
                        "risk"
                    ] = max(
                        system_state["risk"],
                        25
                    )

                    system_state[
                        "incident"
                    ] = (
                        "USB device detected"
                    )

            else:

                system_state[
                    "usb_drive"
                ] = ""

                system_state[
                    "usb_event"
                ] = (
                    "USB DEVICE REMOVED"
                )

                system_state[
                    "usb_activity"
                ] = (
                    "USB DEVICE REMOVED"
                )

                system_state[
                    "incident"
                ] = (
                    "USB device removed"
                )

            system_state[
                "events"
            ] += 1

            update_timestamp()

            response_data = dict(
                system_state
            )

        return jsonify({

            "success": True,

            "message":
                "USB scan event received",

            "data":
                response_data,

            "usb":
                usb_state
        })


    # ========================================================
    # OLD USB FORMAT
    # ========================================================

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

        if event == "connected":

            usb_state[
                "connected"
            ] = True

            usb_state[
                "status"
            ] = "CONNECTED"

            usb_state[
                "device"
            ] = {

                "drive":
                    drive,

                "label":
                    "USB DEVICE"
            }

            usb_state[
                "scan"
            ] = None

            usb_state[
                "last_update"
            ] = timestamp

            system_state[
                "usb_connected"
            ] = True

            system_state[
                "usb_drive"
            ] = drive

            system_state[
                "usb_event"
            ] = (
                "USB DEVICE DETECTED"
            )

            system_state[
                "usb_activity"
            ] = (
                "USB DEVICE CONNECTED"
            )

            system_state[
                "incident"
            ] = (
                f"USB device detected on {drive}"
            )

            system_state[
                "risk"
            ] = max(
                system_state["risk"],
                32
            )

            system_state[
                "ai_risk"
            ] = max(
                system_state["ai_risk"],
                28
            )


        elif event == "removed":

            usb_state[
                "connected"
            ] = False

            usb_state[
                "status"
            ] = "REMOVED"

            usb_state[
                "device"
            ] = None

            usb_state[
                "scan"
            ] = None

            usb_state[
                "last_update"
            ] = timestamp

            system_state[
                "usb_connected"
            ] = False

            system_state[
                "usb_drive"
            ] = ""

            system_state[
                "usb_event"
            ] = (
                "USB DEVICE REMOVED"
            )

            system_state[
                "usb_activity"
            ] = (
                "USB DEVICE REMOVED"
            )

            system_state[
                "incident"
            ] = (
                "USB device removed"
            )


        else:

            system_state[
                "usb_event"
            ] = (
                "UNKNOWN USB EVENT"
            )

            system_state[
                "usb_activity"
            ] = (
                "UNKNOWN USB EVENT"
            )

            usb_state[
                "status"
            ] = (
                "UNKNOWN EVENT"
            )

        system_state[
            "usb_time"
        ] = timestamp

        system_state[
            "events"
        ] += 1

        update_timestamp()

        response_data = dict(
            system_state
        )

    return jsonify({

        "success": True,

        "message":
            "USB event received by IronMind AI",

        "data":
            response_data,

        "usb":
            usb_state
    })


# ============================================================
# DEMO USB THREAT
#
# This is the button you can use during the hackathon.
# ============================================================

@app.route(
    "/api/usb-threat-test",
    methods=["GET", "POST"]
)
def usb_threat_test():

    global demo_mode

    demo_mode = "cyber"

    threat = process_usb_threat(
        "invoice.exe"
    )

    with state_lock:

        data = dict(
            system_state
        )

    return jsonify({

        "success": True,

        "message":
            "CRITICAL USB FILE BLOCKED AND QUARANTINED",

        "threat":
            threat,

        "data":
            data
    })


# ============================================================
# GET THREAT EVENTS
# ============================================================

@app.route("/api/threats")
def get_threats():

    with state_lock:

        return jsonify({

            "success": True,

            "count":
                len(threat_events),

            "threats":
                list(threat_events)
        })


# ============================================================
# GET QUARANTINE
# ============================================================

@app.route("/api/quarantine")
def get_quarantine():

    with state_lock:

        return jsonify({

            "success": True,

            "count":
                len(quarantine_files),

            "files":
                list(quarantine_files)
        })


# ============================================================
# GET INVESTIGATION RECORDS
# ============================================================

@app.route("/api/investigations")
def get_investigations():

    with state_lock:

        return jsonify({

            "success": True,

            "count":
                len(investigation_records),

            "records":
                list(investigation_records)
        })


# ============================================================
# CYBER TEST
# ============================================================

@app.route(
    "/api/cyber-test",
    methods=["GET", "POST"]
)
def cyber_test():

    global demo_mode

    demo_mode = "cyber"

    generate_live_data()

    with state_lock:

        system_state[
            "blocked"
        ] += 1

        system_state[
            "events"
        ] += 1

        data = dict(
            system_state
        )

    return jsonify({

        "success": True,

        "message":
            "Cybersecurity test executed",

        "data":
            data,

        "state":
            data
    })


# ============================================================
# MACHINE TEST
# ============================================================

@app.route(
    "/api/machine-test",
    methods=["GET", "POST"]
)
def machine_test():

    global demo_mode

    demo_mode = "machine"

    generate_live_data()

    with state_lock:

        system_state[
            "events"
        ] += 1

        data = dict(
            system_state
        )

    return jsonify({

        "success": True,

        "message":
            "Machine anomaly test executed",

        "data":
            data,

        "state":
            data
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

        risk = random.randint(
            65,
            92
        )

        network_event = {

            "id":
                str(uuid.uuid4())[:8],

            "timestamp":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "source":
                "NETWORK",

            "event":
                "Suspicious network traffic",

            "risk_score":
                risk,

            "action":
                "BLOCKED"
                if risk >= 70
                else "MONITORED"
        }

        network_events.insert(
            0,
            network_event
        )

        system_state[
            "network"
        ] = (
            "THREAT BLOCKED"
            if risk >= 70
            else "ANALYZING"
        )

        system_state[
            "network_traffic"
        ] = risk

        system_state[
            "events"
        ] += 1

        if risk >= 70:

            system_state[
                "risk"
            ] = max(
                system_state["risk"],
                risk
            )

            system_state[
                "ai_risk"
            ] = max(
                system_state["ai_risk"],
                risk
            )

            system_state[
                "incident"
            ] = (
                "Suspicious network traffic blocked"
            )

        update_timestamp()

        data = dict(
            system_state
        )

    return jsonify({

        "success": True,

        "message":
            "Network security analysis executed",

        "event":
            network_event,

        "data":
            data,

        "state":
            data
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

        risk = random.randint(
            65,
            94
        )

        endpoint_event = {

            "id":
                str(uuid.uuid4())[:8],

            "timestamp":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "device":
                "LOCAL-ENDPOINT",

            "event":
                "Suspicious process behavior",

            "risk_score":
                risk,

            "action":
                "BLOCKED"
                if risk >= 70
                else "MONITORED"
        }

        endpoint_events.insert(
            0,
            endpoint_event
        )

        system_state[
            "endpoint"
        ] = (
            "THREAT BLOCKED"
            if risk >= 70
            else "THREAT DETECTED"
        )

        system_state[
            "cpu"
        ] = random.randint(
            55,
            90
        )

        system_state[
            "memory"
        ] = random.randint(
            55,
            90
        )

        system_state[
            "events"
        ] += 1

        if risk >= 70:

            system_state[
                "risk"
            ] = max(
                system_state["risk"],
                risk
            )

            system_state[
                "ai_risk"
            ] = max(
                system_state["ai_risk"],
                risk
            )

            system_state[
                "incident"
            ] = (
                "Suspicious endpoint behavior blocked"
            )

        update_timestamp()

        data = dict(
            system_state
        )

    return jsonify({

        "success": True,

        "message":
            "Endpoint security analysis executed",

        "event":
            endpoint_event,

        "data":
            data,

        "state":
            data
    })


# ============================================================
# RESET
# ============================================================

@app.route(
    "/api/reset",
    methods=["GET", "POST"]
)
def reset_system():

    global demo_mode

    demo_mode = "normal"
with state_lock:

        system_state[
            "risk"
        ] = 18

        system_state[
            "ai_risk"
        ] = 16

        system_state[
            "status"
        ] = "PROTECTED"

        system_state[
            "incident"
        ] = (
            "No active security incident"
        )

        system_state[
            "endpoint"
        ] = "SECURE"

        system_state[
            "network"
        ] = "MONITORING"

        system_state[
            "iot_ot"
        ] = "MONITORING"

        system_state[
            "cpu"
        ] = 32

        system_state[
            "memory"
        ] = 46

        system_state[
            "network_traffic"
        ] = 38

        system_state[
            "machine_temperature"
        ] = 42.5

        system_state[
            "machine_vibration"
        ] = 1.2

        system_state[
            "machine_rpm"
        ] = 1498

        system_state[
            "usb_activity"
        ] = "NO USB EVENT"

        system_state[
            "usb_event"
        ] = "NO USB EVENT"

        # ----------------------------------------------------
        # Clear active demo records
        # ----------------------------------------------------

        threat_events.clear()

        quarantine_files.clear()

        investigation_records.clear()

        network_events.clear()
        endpoint_events.clear()

        usb_state[
            "connected"
        ] = False

        usb_state[
            "status"
        ] = "WAITING"

        usb_state[
            "device"
        ] = None

        usb_state[
            "scan"
        ] = None

        update_threat_counters()

        system_state[
            "events"
        ] = 0

        update_timestamp()

        data = dict(
            system_state
        )

    return jsonify({

        "success": True,

        "message":
            "IronMind AI system reset",

        "data":
            data,

        "state":
            data
    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({

        "status":
            "online",

        "service":
            "IronMind AI",

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

        "timestamp":
            datetime.now().isoformat()
    })


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
