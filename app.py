from flask import Flask, render_template, jsonify, request
from datetime import datetime
import random
import threading
import hashlib
import uuid


# ============================================================
# IRONMIND AI
# AUTONOMOUS AI CYBER DEFENSE PLATFORM
#
# USB + ENDPOINT + NETWORK + IoT/OT + INVESTIGATION
# ============================================================

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

state_lock = threading.RLock()


# ============================================================
# SYSTEM STATE
# ============================================================

system_state = {

    "risk": 18,
    "ai_risk": 16,

    "status": "PROTECTED",

    "incident":
        "No active security incident",

    "ai_engine": "ACTIVE",

    "endpoint": "SECURE",

    "network": "MONITORING",

    "iot_ot": "MONITORING",

    "threats": 0,

    "blocked": 0,

    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,

    "endpoints": 12,

    "cloud": 8,

    "network_devices": 18,

    "ai_processing": 72,

    "cpu": 32,

    "memory": 46,

    "network_traffic": 38,

    "usb_activity":
        "NO USB EVENT",

    "machine_temperature":
        42.5,

    "machine_vibration":
        1.2,

    "machine_rpm":
        1498,

    "usb_connected":
        False,

    "usb_drive":
        "",

    "usb_event":
        "NO USB EVENT",

    "usb_time":
        "",

    "events":
        0,

    "last_update":
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
}


# ============================================================
# USB STATE
# ============================================================

usb_state = {

    "connected":
        False,

    "status":
        "WAITING",

    "device":
        None,

    "scan":
        None,

    "last_update":
        None
}


# ============================================================
# DATABASES
# ============================================================

threat_events = []

quarantine_files = []

investigation_records = []

network_events = []

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
# HASH
# ============================================================

def generate_hash(filename):

    value = (
        filename +
        datetime.now().isoformat()
    ).encode()

    return hashlib.sha256(
        value
    ).hexdigest()


# ============================================================
# ADD THREAT
# ============================================================

def add_threat_event(
    filename,
    threat_type,
    risk_score,
    severity,
    source="USB",
    reason="Suspicious behavior detected"
):

    event_id = str(
        uuid.uuid4()
    )[:8]

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    file_hash = generate_hash(
        filename
    )

    threat = {

        "id":
            event_id,

        "timestamp":
            timestamp,

        "filename":
            filename,

        "source":
            source,

        "threat_type":
            threat_type,

        "risk_score":
            risk_score,

        "severity":
            severity,

        "reason":
            reason,

        "action":
            "BLOCKED",

        "status":
            "QUARANTINED",

        "sha256":
            file_hash,

        "investigation_status":
            "AVAILABLE"
    }

    threat_events.insert(
        0,
        threat
    )

    # --------------------------------------------------------
    # QUARANTINE
    # --------------------------------------------------------

    quarantine_record = {

        "id":
            event_id,

        "filename":
            filename,

        "source":
            source,

        "sha256":
            file_hash,

        "risk_score":
            risk_score,

        "severity":
            severity,

        "status":
            "QUARANTINED",

        "blocked":
            True,

        "timestamp":
            timestamp
    }

    quarantine_files.insert(
        0,
        quarantine_record
    )

    # --------------------------------------------------------
    # INVESTIGATION
    # --------------------------------------------------------

    investigation_record = {

        "id":
            event_id,

        "filename":
            filename,

        "threat_type":
            threat_type,

        "severity":
            severity,

        "risk_score":
            risk_score,

        "source":
            source,

        "reason":
            reason,

        "sha256":
            file_hash,

        "action":
            "BLOCKED",

        "status":
            "QUARANTINED",

        "timestamp":
            timestamp,

        "investigation_status":
            "READY FOR INVESTIGATION"
    }

    investigation_records.insert(
        0,
        investigation_record
    )

    return threat


# ============================================================
# UPDATE COUNTERS
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

    system_state["threats"] = (
        len(threat_events)
    )

    system_state["blocked"] = (
        len(quarantine_files)
    )


# ============================================================
# PROCESS USB THREAT
# ============================================================

def process_usb_threat(
    filename="invoice.exe",
    risk_score=95,
    severity="CRITICAL",
    reason=None
):

    global demo_mode

    with state_lock:

        # IMPORTANT:
        # Keep dashboard in threat mode.
        demo_mode = "cyber"

        if risk_score >= 90:

            severity = "CRITICAL"

        elif risk_score >= 70:

            severity = "HIGH"

        else:

            severity = "MEDIUM"

        if not reason:

            reason = (
                "High-risk executable or script "
                "detected on removable media"
            )

        threat = add_threat_event(

            filename=filename,

            threat_type=
                "HIGH-RISK USB FILE",

            risk_score=
                risk_score,

            severity=
                severity,

            source=
                "USB DRIVE",

            reason=
                reason
        )

        # ----------------------------------------------------
        # SECURITY STATE
        # ----------------------------------------------------

        system_state["risk"] = max(
            90,
            risk_score
        )

        system_state["ai_risk"] = max(
            90,
            risk_score
        )

        system_state["status"] = (
            "THREAT BLOCKED"
        )

        system_state["incident"] = (
            f"{severity} USB THREAT BLOCKED: "
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
# LIVE DATA
# ============================================================

def generate_live_data():

    global demo_mode

    with state_lock:

        # ----------------------------------------------------
        # DO NOT RESET AN ACTIVE THREAT
        # ----------------------------------------------------

        if len(threat_events) > 0:

            latest = threat_events[0]

            system_state["risk"] = max(
                system_state["risk"],
                latest["risk_score"]
            )

            system_state["ai_risk"] = max(
                system_state["ai_risk"],
                latest["risk_score"]
            )

            system_state["status"] = (
                "THREAT BLOCKED"
            )

            system_state["incident"] = (
                f'{latest["severity"]} USB THREAT BLOCKED: '
                f'{latest["filename"]}'
            )

            system_state["endpoint"] = (
                "THREAT BLOCKED"
            )

            system_state["usb_activity"] = (
                "THREAT BLOCKED"
            )

            update_threat_counters()

            update_timestamp()

            return

        # ----------------------------------------------------
        # NORMAL
        # ----------------------------------------------------

        if demo_mode == "normal":

            system_state["risk"] = random.randint(
                10,
                28
            )

            system_state["ai_risk"] = random.randint(
                8,
                25
            )

            system_state["status"] = (
                "PROTECTED"
            )

            system_state["incident"] = (
                "No active security incident"
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

            system_state["usb_activity"] = (
                "NO USB EVENT"
            )

        # ----------------------------------------------------
        # CYBER
        # ----------------------------------------------------

        elif demo_mode == "cyber":

            system_state["risk"] = random.randint(
                80,
                96
            )

            system_state["ai_risk"] = random.randint(
                82,
                98
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

        # ----------------------------------------------------
        # MACHINE
        # ----------------------------------------------------

        elif demo_mode == "machine":

            system_state["risk"] = random.randint(
                55,
                85
            )

            system_state["ai_risk"] = random.randint(
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
                    4,
                    7
                ),
                1
            )

            system_state["machine_rpm"] = random.randint(
                1050,
                1250
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

        return jsonify(
            dict(system_state)
        )


# ============================================================
# USB STATUS
# ============================================================

@app.route("/api/usb-status")
def usb_status():

    with state_lock:

        return jsonify(
            dict(usb_state)
        )


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

        system_state["usb_connected"] = (
            connected
        )

        system_state["usb_time"] = (
            timestamp
        )

        if device:

            system_state["usb_drive"] = (
                device.get(
                    "drive",
                    ""
                )
            )

        # ====================================================
        # USB CONNECTED
        # ====================================================

        if connected:

            system_state["usb_event"] = (
                "USB DEVICE DETECTED"
            )

            system_state["usb_activity"] = (
                "USB DEVICE CONNECTED"
            )

            suspicious_count = 0

            if scan:

                try:

                    suspicious_count = int(
                        scan.get(
                            "suspicious_count",
                            0
                        )
                    )

                except Exception:

                    suspicious_count = 0

            # =================================================
            # THREAT FOUND
            # =================================================

            if suspicious_count > 0:

                filename = (
                    scan.get(
                        "filename",
                        "HIGH_RISK_FILE"
                    )
                )

                risk_score = int(
                    scan.get(
                        "risk_score",
                        95
                    )
                )

                severity = (
                    scan.get(
                        "severity",
                        "CRITICAL"
                    )
                )

                reason = (
                    scan.get(
                        "reason",
                        "High-risk file detected on USB"
                    )
                )

                # ------------------------------------------------
                # PROCESS REAL USB THREAT
                # ------------------------------------------------

                process_usb_threat(

                    filename=
                        filename,

                    risk_score=
                        risk_score,

                    severity=
                        severity,

                    reason=
                        reason
                )

            else:

                # Safe USB
                system_state["risk"] = max(
                    system_state["risk"],
                    25
                )

                system_state["incident"] = (
                    "USB device scanned - no high-risk file detected"
                )

        # ====================================================
        # USB REMOVED
        # ====================================================

        else:

            system_state["usb_connected"] = (
                False
            )

            system_state["usb_drive"] = (
                ""
            )

            system_state["usb_event"] = (
                "USB DEVICE REMOVED"
            )

            system_state["usb_activity"] = (
                "USB DEVICE REMOVED"
            )

            # Do NOT delete investigation records.
            # Evidence remains available.

            if not threat_events:

                system_state["incident"] = (
                    "USB device removed"
                )

        system_state["events"] += 1

        update_threat_counters()

        update_timestamp()

        return jsonify({

            "success":
                True,

            "message":
                "USB event received by IronMind AI",

            "data":
                dict(system_state),

            "usb":
                dict(usb_state)
        })


# ============================================================
# DEMO USB THREAT
# ============================================================

@app.route(
    "/api/usb-threat-test",
    methods=["GET", "POST"]
)
def usb_threat_test():

    threat = process_usb_threat(

        filename=
            "invoice.exe",

        risk_score=
            95,

        severity=
            "CRITICAL",

        reason=
            "Executable test file detected on removable media"
    )

    with state_lock:
        data = dict(
            system_state
        )

    return jsonify({

        "success":
            True,

        "message":
            "CRITICAL USB FILE BLOCKED AND QUARANTINED",

        "threat":
            threat,

        "data":
            data
    })


# ============================================================
# THREATS
# ============================================================

@app.route("/api/threats")
def get_threats():

    with state_lock:

        return jsonify({

            "success":
                True,

            "count":
                len(threat_events),

            "threats":
                list(threat_events)
        })


# ============================================================
# QUARANTINE
# ============================================================

@app.route("/api/quarantine")
def get_quarantine():

    with state_lock:

        return jsonify({

            "success":
                True,

            "count":
                len(quarantine_files),

            "files":
                list(quarantine_files)
        })


# ============================================================
# INVESTIGATIONS
# ============================================================

@app.route("/api/investigations")
def get_investigations():

    with state_lock:

        return jsonify({

            "success":
                True,

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

        system_state["events"] += 1

        data = dict(
            system_state
        )

    return jsonify({

        "success":
            True,

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

        system_state["events"] += 1

        data = dict(
            system_state
        )

    return jsonify({

        "success":
            True,

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

        system_state["network"] = (
            "THREAT BLOCKED"
            if risk >= 70
            else "ANALYZING"
        )

        system_state["network_traffic"] = (
            risk
        )

        system_state["events"] += 1

        if risk >= 70:

            system_state["risk"] = max(
                system_state["risk"],
                risk
            )

            system_state["ai_risk"] = max(
                system_state["ai_risk"],
                risk
            )

            system_state["incident"] = (
                "Suspicious network traffic blocked"
            )

        update_timestamp()

        data = dict(
            system_state
        )

    return jsonify({

        "success":
            True,

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

        system_state["endpoint"] = (
            "THREAT BLOCKED"
            if risk >= 70
            else "THREAT DETECTED"
        )

        system_state["cpu"] = random.randint(
            55,
            90
        )

        system_state["memory"] = random.randint(
            55,
            90
        )

        system_state["events"] += 1

        if risk >= 70:

            system_state["risk"] = max(
                system_state["risk"],
                risk
            )

            system_state["ai_risk"] = max(
                system_state["ai_risk"],
                risk
            )

            system_state["incident"] = (
                "Suspicious endpoint behavior blocked"
            )

        update_timestamp()

        data = dict(
            system_state
        )

    return jsonify({

        "success":
            True,

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

        system_state["risk"] = 18

        system_state["ai_risk"] = 16

        system_state["status"] = (
            "PROTECTED"
        )

        system_state["incident"] = (
            "No active security incident"
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

        system_state["cpu"] = 32

        system_state["memory"] = 46

        system_state["network_traffic"] = 38

        system_state["machine_temperature"] = 42.5

        system_state["machine_vibration"] = 1.2

        system_state["machine_rpm"] = 1498

        system_state["usb_activity"] = (
            "NO USB EVENT"
        )

        system_state["usb_event"] = (
            "NO USB EVENT"
        )

        system_state["usb_connected"] = (
            False
        )

        system_state["usb_drive"] = ""

        system_state["usb_time"] = ""

        # ----------------------------------------------------
        # Clear demo data
        # ----------------------------------------------------

        threat_events.clear()

        quarantine_files.clear()

        investigation_records.clear()

        network_events.clear()

        endpoint_events.clear()

        usb_state["connected"] = False

        usb_state["status"] = (
            "WAITING"
        )

        usb_state["device"] = None

        usb_state["scan"] = None

        usb_state["last_update"] = None

        system_state["events"] = 0

        update_threat_counters()

        update_timestamp()

        data = dict(
            system_state
        )

    return jsonify({

        "success":
            True,

        "message":
            "IronMind AI system reset",

        "data":
            data,

        "state":
            data
    })


# ============================================================
# HEALTH
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
