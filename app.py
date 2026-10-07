from __future__ import annotations

import hashlib
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template, request

from cyber.monitor import CyberMonitor
from machine.monitor import MachineMonitor
from response.engine import ResponseEngine


app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates",
)


# ============================================================
# GLOBAL SERVICES
# ============================================================

cyber_monitor = CyberMonitor()
machine_monitor = MachineMonitor()
response_engine = ResponseEngine()

state_lock = threading.RLock()


# ============================================================
# HELPERS
# ============================================================

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_hash(value: str) -> str:
    return hashlib.sha256(
        f"{value}:{now_iso()}".encode("utf-8")
    ).hexdigest()


def clamp_score(value: Any) -> int:
    try:
        value = int(float(value))
    except (TypeError, ValueError):
        value = 0

    return max(0, min(100, value))


def severity_from_score(score: int) -> str:
    if score >= 85:
        return "CRITICAL"

    if score >= 70:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    return "LOW"


def update_timestamp():
    system_state["last_update"] = now_iso()


# ============================================================
# SYSTEM STATE
# ============================================================

system_state: Dict[str, Any] = {
    "risk": 18,
    "ai_risk": 16,
    "status": "PROTECTED",
    "incident": "No active incident",
    "ai_engine": "ACTIVE",

    "modules": {
        "endpoint": "SECURE",
        "network": "MONITORING",
        "iot_ot": "NOT CONNECTED",
        "industrial_ot": "NOT CONNECTED",
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
        "network_devices": 18,
    },

    "ai": {
        "processing": 72,
        "engine": "IsolationForest",
        "detection": "SERVER-SIDE ML",
        "threat_analysis": "AI THREAT ANALYSIS",
        "prediction": "READY",
    },

    "endpoint": {
        "cpu": 32,
        "memory": 46,
        "network_traffic": 38,
    },

    "network": {
        "traffic": 30,
        "connections": 14,
        "failed_connections": 2,
        "unusual_ports": 1,
        "packet_burst": 3,
        "anomaly_score": 0,
        "threat_class": "NORMAL NETWORK TRAFFIC",
        "severity": "LOW",
        "status": "MONITORING",
    },

    "usb": {
        "connected": False,
        "device": "WAITING",
        "drive": "-",
        "filesystem": "-",
        "status": "NOT CONNECTED",
        "files_scanned": 0,
        "anomaly_score": 0,
        "threat_class": "NONE",
        "severity": "LOW",
        "action": "MONITOR",
        "ml_prediction": "NONE",
        "last_update": None,
    },

    "workflow": {
        "device_detected": False,
        "anomaly_detected": False,
        "threat_classified": False,
        "device_quarantined": False,
        "forensic_report_generated": False,
    },

    "events": [],

    "last_update": now_iso(),
}


# ============================================================
# DATABASE-LIKE IN-MEMORY RECORDS
# ============================================================

threat_events: List[Dict[str, Any]] = []
quarantine_files: List[Dict[str, Any]] = []
investigation_records: List[Dict[str, Any]] = []
network_events: List[Dict[str, Any]] = []
endpoint_events: List[Dict[str, Any]] = []


# ============================================================
# EVENT HELPERS
# ============================================================

def add_event(
    event_type: str,
    source: str,
    message: str,
    score: int = 0,
):
    event = {
        "id": len(system_state["events"]) + 1,
        "timestamp": now_iso(),
        "type": event_type,
        "source": source,
        "message": message,
        "anomaly_score": clamp_score(score),
    }

    system_state["events"].insert(0, event)

    system_state["events"] = system_state["events"][:100]


def update_threat_counters():
    system_state["threats"] = len(threat_events)

    system_state["blocked"] = sum(
        1
        for event in threat_events
        if event.get("status") in {
            "QUARANTINED",
            "BLOCKED",
            "ISOLATED",
        }
    )

    system_state["critical"] = sum(
        1
        for event in threat_events
        if event.get("severity") == "CRITICAL"
    )

    system_state["high"] = sum(
        1
        for event in threat_events
        if event.get("severity") == "HIGH"
    )

    system_state["medium"] = sum(
        1
        for event in threat_events
        if event.get("severity") == "MEDIUM"
    )

    system_state["low"] = sum(
        1
        for event in threat_events
        if event.get("severity") == "LOW"
    )


def add_threat_event(
    source: str,
    threat_type: str,
    score: int,
    severity: str,
    reason: str,
    filename: str = "",
):
    score = clamp_score(score)

    threat_id = len(threat_events) + 1

    sha256 = generate_hash(
        filename or threat_type
    )

    event = {
        "id": threat_id,
        "timestamp": now_iso(),
        "filename": filename or "-",
        "source": source,
        "threat_type": threat_type,
        "risk_score": score,
        "anomaly_score": score,
        "severity": severity,
        "reason": reason,
        "action": "QUARANTINED",
        "status": "QUARANTINED",
        "sha256": sha256,
        "investigation_status": "AVAILABLE",
    }

    threat_events.insert(0, event)

    quarantine_files.insert(
        0,
        {
            "id": threat_id,
            "filename": filename or "-",
            "source": source,
            "timestamp": now_iso(),
            "status": "QUARANTINED",
            "sha256": sha256,
        },
    )

    investigation_records.insert(
        0,
        {
            "id": threat_id,
            "threat_id": threat_id,
            "timestamp": now_iso(),
            "source": source,
            "status": "REPORT GENERATED",
            "anomaly_score": score,
            "threat_class": threat_type,
            "severity": severity,
            "sha256": sha256,
        },
    )

    update_threat_counters()

    return event


# ============================================================
# USB PROCESSING
# ============================================================

def process_usb_ml(
    files: List[Dict[str, Any]],
    device: str,
    drive: str,
    filesystem: str,
):
    result = cyber_monitor.analyze_usb(files)

    score = clamp_score(
        result.get("anomaly_score", 0)
    )

    threat_class = result.get(
        "threat_class",
        "UNKNOWN",
    )

    severity = result.get(
        "severity",
        severity_from_score(score),
    )

    if score >= 70:
        action = "QUARANTINE"
        usb_status = "THREAT BLOCKED"

        system_state["modules"]["endpoint"] = (
            "THREAT BLOCKED"
        )

        system_state["status"] = "THREAT BLOCKED"
        system_state["risk"] = max(
            system_state["risk"],
            score,
        )

        system_state["ai_risk"] = max(
            system_state["ai_risk"],
            score,
        )

        system_state["workflow"] = {
            "device_detected": True,
            "anomaly_detected": True,
            "threat_classified": True,
            "device_quarantined": True,
            "forensic_report_generated": True,
        }

        filename = "-"

        if files:
            filename = str(
                files[0].get(
                    "name",
                    files[0].get("path", "-"),
                )
            )

        threat = add_threat_event(
            source="USB DRIVE",
            threat_type=threat_class,
            score=score,
            severity=severity,
            reason=(
                "Server-side Isolation Forest detected "
                "anomalous removable-media behavior."
            ),
            filename=filename,
        )

        response = response_engine.respond_to_threat(
            source="USB DRIVE",
            anomaly_score=score,
            threat_class=threat_class,
            severity=severity,
        )

        add_event(
            "THREAT",
            "USB",
            (
                f"USB anomaly detected: "
                f"{threat_class} "
                f"({score}%)"
            ),
            score,
        )

    else:
        action = "MONITOR"
        usb_status = "MONITORING"

        threat = None

        system_state["workflow"] = {
            "device_detected": True,
            "anomaly_detected": score >= 40,
            "threat_classified": score >= 40,
            "device_quarantined": False,
            "forensic_report_generated": False,
        }

        response = response_engine.respond_to_threat(
            source="USB DRIVE",
            anomaly_score=score,
            threat_class=threat_class,
            severity=severity,
        )

        add_event(
            "TELEMETRY",
            "USB",
            (
                f"USB telemetry analyzed by ML: "
                f"{score}% anomaly score"
            ),
            score,
        )

        if score < 40:
            system_state["status"] = "PROTECTED"
            system_state["risk"] = min(
                system_state["risk"],
                25,
            )

    system_state["usb"] = {
        "connected": True,
        "device": device or "USB DEVICE",
        "drive": drive or "-",
        "filesystem": filesystem or "-",
        "status": usb_status,
        "files_scanned": len(files),
        "anomaly_score": score,
        "threat_class": threat_class,
        "severity": severity,
        "action": action,
        "ml_prediction": result.get(
            "ml_prediction",
            "UNKNOWN",
        ),
        "engine": result.get(
            "engine",
            "IsolationForest",
        ),
        "detection_method": result.get(
            "detection_method",
            "SERVER-SIDE ML",
        ),
        "last_update": now_iso(),
    }

    update_timestamp()

    return {
        "success": True,
        "anomaly_score": score,
        "threat_class": threat_class,
        "severity": severity,
        "action": action,
        "detection": "SERVER-SIDE ML",
        "engine": "IsolationForest",
        "ml_detected": True,
        "workflow": system_state["workflow"],
        "response": response,
        "threat": threat,
    }


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/status")
def api_status():
    with state_lock:
        update_timestamp()

        return jsonify(system_state)


@app.route("/api/usb-status")
def usb_status():
    with state_lock:
        return jsonify(system_state["usb"])


# ============================================================
# USB EVENT FROM WINDOWS AGENT
# ============================================================

@app.route(
    "/api/usb-event",
    methods=["POST"],
)
def usb_event():
    try:
        payload = request.get_json(
            silent=True
        ) or {}

        connected = bool(
            payload.get(
                "connected",
                False,
            )
        )

        device = str(
            payload.get(
                "device",
                "USB DEVICE",
            )
        )

        drive = str(
            payload.get(
                "drive",
                "-",
            )
        )

        filesystem = str(
            payload.get(
                "filesystem",
                "-",
            )
        )

        files = payload.get(
            "files",
            [],
        )

        if not isinstance(files, list):
            files = []

        with state_lock:

            # ------------------------------------------------
            # USB REMOVED
            # ------------------------------------------------

            if not connected:

                system_state["usb"] = {
                    "connected": False,
                    "device": "WAITING",
                    "drive": "-",
                    "filesystem": "-",
                    "status": "NOT CONNECTED",
                    "files_scanned": 0,
                    "anomaly_score": 0,
                    "threat_class": "NONE",
                    "severity": "LOW",
                    "action": "MONITOR",
                    "ml_prediction": "NONE",
                    "last_update": now_iso(),
                }

                system_state["workflow"] = {
                    "device_detected": False,
                    "anomaly_detected": False,
                    "threat_classified": False,
                    "device_quarantined": False,
                    "forensic_report_generated": False,
                }

                system_state["modules"][
                    "endpoint"
                ] = "SECURE"

                system_state["status"] = "PROTECTED"

                system_state["risk"] = 18
                system_state["ai_risk"] = 16

                add_event(
                    "DEVICE",
                    "USB",
                    "USB device removed.",
                    0,
                )

                update_timestamp()

                return jsonify(
                    {
                        "success": True,
                        "connected": False,
                        "anomaly_score": 0,
                        "threat_class": "NONE",
                        "severity": "LOW",
                        "action": "MONITOR",
                    }
                )

            # ------------------------------------------------
            # USB CONNECTED
            # ------------------------------------------------

            result = process_usb_ml(
                files=files,
                device=device,
                drive=drive,
                filesystem=filesystem,
            )

            return jsonify(result)

    except Exception as exc:
        app.logger.exception(
            "USB event processing failed"
        )

        return jsonify(
            {
                "success": False,
                "error": str(exc),
                "anomaly_score": 0,
                "threat_class": "PROCESSING ERROR",
                "severity": "LOW",
                "action": "MONITOR",
            }
        ), 500


# ============================================================
# USB ML TEST
# ============================================================

@app.route(
    "/api/usb-threat-test",
    methods=["GET", "POST"],
)
def usb_threat_test():

    # Synthetic telemetry is used only to test
    # the ML pipeline end-to-end.
    demo_files = []

    for i in range(60):
        demo_files.append(
            {
                "path": f"E:\\payload_{i}.exe",
                "name": f"payload_{i}.exe",
                "extension": ".exe",
                "size": 18 * 1024 * 1024,
                "sha256": generate_hash(
                    f"payload_{i}"
                ),
                "is_hidden": True,
                "is_system": True,
            }
        )

    with state_lock:

        result = process_usb_ml(
            files=demo_files,
            device="IRONMIND DEMO USB",
            drive="E:\\",
            filesystem="NTFS",
        )

        return jsonify(result)


# ============================================================
# NETWORK ML TEST
# ============================================================

@app.route(
    "/api/network-test",
    methods=["GET", "POST"],
)
def network_test():

    # Extreme telemetry is supplied to the trained
    # IsolationForest as an anomaly-test scenario.
    result = cyber_monitor.analyze_network(
        traffic=95,
        connections=120,
        failed_connections=60,
        unusual_ports=35,
        packet_burst=70,
    )

    score = clamp_score(
        result["anomaly_score"]
    )

    severity = result["severity"]

    with state_lock:

        system_state["network"] = {
            "traffic": 95,
            "connections": 120,
            "failed_connections": 60,
            "unusual_ports": 35,
            "packet_burst": 70,
            "anomaly_score": score,
            "threat_class": result["threat_class"],
            "severity": severity,
            "status": (
                "THREAT BLOCKED"
                if score >= 70
                else "ANALYZING"
            ),
        }

        network_event = {
            "id": len(network_events) + 1,
            "timestamp": now_iso(),
            "source": "NETWORK",
            "event": "ML NETWORK ANOMALY",
            "risk_score": score,
            "anomaly_score": score,
            "severity": severity,
            "action": (
                "ISOLATE"
                if score >= 70
                else "MONITOR"
            ),
            "status": (
                "ISOLATED"
                if score >= 70
                else "MONITORED"
            ),
        }

        network_events.insert(
            0,
            network_event,
        )

        if score >= 70:

            system_state["modules"][
                "network"
            ] = "THREAT BLOCKED"

            system_state["status"] = "THREAT BLOCKED"

            system_state["risk"] = max(
                system_state["risk"],
                score,
            )

            system_state["ai_risk"] = max(
                system_state["ai_risk"],
                score,
            )

            response = response_engine.respond_to_threat(
                source="NETWORK",
                anomaly_score=score,
                threat_class=result["threat_class"],
                severity=severity,
            )

            add_event(
                "THREAT",
                "NETWORK",
                (
                    f"Network anomaly detected "
                    f"({score}%)"
                ),
                score,
            )

        else:
            response = response_engine.respond_to_threat(
                source="NETWORK",
                anomaly_score=score,
                threat_class=result["threat_class"],
                severity=severity,
            )

        update_timestamp()

        return jsonify(
            {
                "success": True,
                "anomaly_score": score,
                "threat_class": result[
                    "threat_class"
                ],
                "severity": severity,
                "action": (
                    "ISOLATE"
                    if score >= 70
                    else "MONITOR"
                ),
                "detection": "SERVER-SIDE ML",
                "engine": "IsolationForest",
                "event": network_event,
                "response": response,
            }
        )


# ============================================================
# ENDPOINT ML TEST
# ============================================================

@app.route(
    "/api/endpoint-test",
    methods=["GET", "POST"],
)
def endpoint_test():

    result = cyber_monitor.analyze_endpoint(
        cpu=97,
        memory=94,
        network_traffic=96,
        process_activity=55,
        privilege_activity=40,
    )

    score = clamp_score(
        result["anomaly_score"]
    )

    with state_lock:

        system_state["endpoint"] = {
            "cpu": 97,
            "memory": 94,
            "network_traffic": 96,
        }

        system_state["modules"][
            "endpoint"
        ] = (
            "THREAT BLOCKED"
            if score >= 70
            else "THREAT DETECTED"
        )

        if score >= 70:
            system_state["status"] = "THREAT BLOCKED"
            system_state["risk"] = max(
                system_state["risk"],
                score,
            )
            system_state["ai_risk"] = max(
                system_state["ai_risk"],
                score,
            )

        event = {
            "id": len(endpoint_events) + 1,
            "timestamp": now_iso(),
            "source": "ENDPOINT",
            "event": "ML ENDPOINT ANOMALY",
            "anomaly_score": score,
            "risk_score": score,
            "severity": result["severity"],
            "action": (
                "BLOCK"
                if score >= 70
                else "MONITOR"
            ),
            "status": (
                "BLOCKED"
                if score >= 70
                else "MONITORED"
            ),
        }

        endpoint_events.insert(
            0,
            event,
        )

        response = response_engine.respond_to_threat(
            source="ENDPOINT",
            anomaly_score=score,
            threat_class=result["threat_class"],
            severity=result["severity"],
        )

        add_event(
            "THREAT" if score >= 70 else "TELEMETRY",
            "ENDPOINT",
            (
                f"Endpoint ML anomaly: "
                f"{score}%"
            ),
            score,
        )

        update_timestamp()

        return jsonify(
            {
                "success": True,
                "anomaly_score": score,
                "threat_class": result[
                    "threat_class"
                ],
                "severity": result["severity"],
                "action": (
                    "BLOCK"
                    if score >= 70
                    else "MONITOR"
                ),
                "detection": "SERVER-SIDE ML",
                "engine": "IsolationForest",
                "event": event,
                "response": response,
            }
        )


# ============================================================
# CYBER TEST
# ============================================================

@app.route(
    "/api/cyber-test",
    methods=["GET", "POST"],
)
def cyber_test():

    return network_test()


# ============================================================
# IOT / OT
# ============================================================

@app.route(
    "/api/machine-test",
    methods=["GET", "POST"],
)
def machine_test():

    with state_lock:

        result = machine_monitor.simulate_anomaly()

        system_state["modules"][
            "iot_ot"
        ] = "NOT CONNECTED"

        system_state["modules"][
            "industrial_ot"
        ] = "NOT CONNECTED"

        update_timestamp()

        return jsonify(result), 409


# ============================================================
# THREATS
# ============================================================

@app.route("/api/threats")
def api_threats():

    with state_lock:
        return jsonify(
            {
                "threats": threat_events,
                "count": len(threat_events),
            }
        )


@app.route("/api/quarantine")
def api_quarantine():

    with state_lock:
        return jsonify(
            {
                "files": quarantine_files,
                "count": len(quarantine_files),
            }
        )


@app.route("/api/investigations")
def api_investigations():

    with state_lock:
        return jsonify(
            {
                "investigations": investigation_records,
                "count": len(
                    investigation_records
                ),
            }
        )


@app.route("/api/network-events")
def api_network_events():

    with state_lock:
        return jsonify(
            {
                "events": network_events,
                "count": len(network_events),
            }
        )


@app.route("/api/endpoint-events")
def api_endpoint_events():

    with state_lock:
        return jsonify(
            {
                "events": endpoint_events,
                "count": len(endpoint_events),
            }
        )


# ============================================================
# RESET
# ============================================================

@app.route(
    "/api/reset",
    methods=["GET", "POST"],
)
def reset():

    with state_lock:

        threat_events.clear()
        quarantine_files.clear()
        investigation_records.clear()
        network_events.clear()
        endpoint_events.clear()

        cyber_monitor.reset()
        machine_monitor.reset()
        response_engine.reset()

        system_state["risk"] = 18
        system_state["ai_risk"] = 16
        system_state["status"] = "PROTECTED"
        system_state["incident"] = (
            "No active incident"
        )

        system_state["modules"] = {
            "endpoint": "SECURE",
            "network": "MONITORING",
            "iot_ot": "NOT CONNECTED",
            "industrial_ot": "NOT CONNECTED",
        }

        system_state["threats"] = 0
        system_state["blocked"] = 0
        system_state["critical"] = 0
        system_state["high"] = 0
        system_state["medium"] = 0
        system_state["low"] = 0

        system_state["endpoint"] = {
            "cpu": 32,
            "memory": 46,
            "network_traffic": 38,
        }

        system_state["network"] = {
            "traffic": 30,
            "connections": 14,
            "failed_connections": 2,
            "unusual_ports": 1,
            "packet_burst": 3,
            "anomaly_score": 0,
            "threat_class": "NORMAL NETWORK TRAFFIC",
            "severity": "LOW",
            "status": "MONITORING",
        }

        system_state["usb"] = {
            "connected": False,
            "device": "WAITING",
            "drive": "-",
            "filesystem": "-",
            "status": "NOT CONNECTED",
            "files_scanned": 0,
            "anomaly_score": 0,
            "threat_class": "NONE",
            "severity": "LOW",
            "action": "MONITOR",
            "ml_prediction": "NONE",
            "last_update": now_iso(),
        }

        system_state["workflow"] = {
            "device_detected": False,
            "anomaly_detected": False,
            "threat_classified": False,
            "device_quarantined": False,
            "forensic_report_generated": False,
        }

        system_state["events"] = []

        add_event(
            "SYSTEM",
            "IRONMIND",
            "System reset completed.",
            0,
        )

        update_timestamp()

        return jsonify(
            {
                "success": True,
                "message": "IronMind AI reset.",
                "state": system_state,
            }
        )


# ============================================================
# HEALTH
# ============================================================

@app.route("/health")
def health():

    return jsonify(
        {
            "status": "healthy",
            "service": "IronMind AI",
            "ml_engine": "IsolationForest",
            "detection": "SERVER-SIDE ML",
            "endpoint_monitoring": True,
            "network_monitoring": True,
            "usb_monitoring": True,
            "iot_ot": "NOT CONNECTED",
            "industrial_ot": "NOT CONNECTED",
            "threat_response": True,
            "forensic_reporting": True,
        }
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
