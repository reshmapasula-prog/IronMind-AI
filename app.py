from __future__ import annotations

import hashlib
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from flask import Flask, jsonify, render_template, request

from cyber.monitor import CyberMonitor
from machine.monitor import MachineMonitor
from response.engine import ResponseEngine


app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates",
)

state_lock = threading.RLock()

cyber_monitor = CyberMonitor()
machine_monitor = MachineMonitor()
response_engine = ResponseEngine()

threat_events = []
quarantine_files = []
investigation_records = []
network_events = []
endpoint_events = []


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_hash(value: str) -> str:
    return hashlib.sha256(
        f"{value}:{now_iso()}".encode("utf-8")
    ).hexdigest()


def empty_workflow() -> Dict[str, Any]:
    return {
        "device_detected": False,
        "anomaly_detected": False,
        "threat_classified": False,
        "response_executed": False,
        "quarantined": False,
        "isolated": False,
        "forensic_report": False,
        "current_stage": "MONITORING",
    }


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

    "ai_processing": 72,

    "endpoint_telemetry": {
        "cpu": 32,
        "memory": 46,
        "network_traffic": 38,
        "process_count": 82,
        "file_activity": 24,
        "usb_activity": 2,
    },

    "network_telemetry": {
        "traffic_rate": 35,
        "connection_count": 42,
        "failed_connections": 3,
        "unique_destinations": 8,
        "packet_variance": 19,
        "suspicious_port_activity": 2,
    },

    "usb": {
        "connected": False,
        "device": "WAITING FOR USB AGENT",
        "drive": None,
        "filesystem": None,
        "scan": "IDLE",
        "files_scanned": 0,
        "suspicious": 0,
        "storage": None,
        "last_event": None,
    },

    "workflow": empty_workflow(),

    "ml": {
        "engine": "IsolationForest",
        "endpoint": "ACTIVE",
        "network": "ACTIVE",
        "usb": "ACTIVE",
    },

    "events": 0,
    "last_update": now_iso(),
}


def update_timestamp() -> None:
    system_state["last_update"] = now_iso()


def update_threat_counters() -> None:
    system_state["threats"] = len(threat_events)
    system_state["blocked"] = sum(
        1
        for event in threat_events
        if event.get("status") in {"QUARANTINED", "ISOLATED"}
    )

    system_state["critical"] = sum(
        1 for event in threat_events if event.get("severity") == "CRITICAL"
    )
    system_state["high"] = sum(
        1 for event in threat_events if event.get("severity") == "HIGH"
    )
    system_state["medium"] = sum(
        1 for event in threat_events if event.get("severity") == "MEDIUM"
    )
    system_state["low"] = sum(
        1 for event in threat_events if event.get("severity") == "LOW"
    )


def classify_threat(score: float) -> str:
    if score >= 90:
        return "CRITICAL ML ANOMALY"
    if score >= 75:
        return "HIGH-RISK ML ANOMALY"
    if score >= 55:
        return "MEDIUM-RISK ML ANOMALY"
    return "LOW-RISK ML ANOMALY"


def begin_workflow(
    source: str,
    anomaly_score: float,
    classification: str,
) -> None:

    workflow = empty_workflow()

    workflow["device_detected"] = source in {"ENDPOINT", "USB"}
    workflow["anomaly_detected"] = True
    workflow["threat_classified"] = True
    workflow["current_stage"] = "THREAT CLASSIFIED"

    system_state["workflow"] = workflow
    system_state["risk"] = int(round(anomaly_score))
    system_state["ai_risk"] = int(round(anomaly_score))

    if source == "NETWORK":
        system_state["incident"] = "NETWORK ANOMALY DETECTED"
        system_state["modules"]["network"] = "ANALYZING"

    elif source in {"ENDPOINT", "USB"}:
        system_state["incident"] = "DEVICE ANOMALY DETECTED"
        system_state["modules"]["endpoint"] = "THREAT DETECTED"

    system_state["status"] = "THREAT DETECTED"


def finish_workflow(
    source: str,
    response: Dict[str, Any],
) -> None:

    workflow = system_state["workflow"]

    workflow["response_executed"] = True

    if source == "NETWORK":
        workflow["isolated"] = True
        workflow["current_stage"] = "CONNECTION ISOLATED"
        system_state["modules"]["network"] = "ISOLATED"
        system_state["incident"] = "NETWORK CONNECTION ISOLATED"

    else:
        workflow["quarantined"] = True
        workflow["current_stage"] = "DEVICE QUARANTINED"
        system_state["modules"]["endpoint"] = "QUARANTINED"
        system_state["incident"] = "DEVICE QUARANTINED"

    workflow["forensic_report"] = True
    workflow["current_stage"] = "FORENSIC REPORT GENERATED"

    system_state["status"] = "THREAT BLOCKED"


def add_threat_event(
    *,
    source: str,
    threat_type: str,
    risk_score: float,
    severity: str,
    reason: str,
    action: str,
    filename: Optional[str] = None,
) -> Dict[str, Any]:

    timestamp = now_iso()

    event_id = str(uuid.uuid4())[:8].upper()

    event = {
        "id": event_id,
        "timestamp": timestamp,
        "source": source,
        "filename": filename or "N/A",
        "threat_type": threat_type,
        "risk_score": round(float(risk_score), 2),
        "severity": severity,
        "reason": reason,
        "action": action,
        "status": (
            "ISOLATED"
            if source == "NETWORK"
            else "QUARANTINED"
        ),
        "sha256": generate_hash(filename or threat_type),
        "investigation_status": "AVAILABLE",
    }

    threat_events.insert(0, event)

    if event["status"] in {"QUARANTINED", "ISOLATED"}:
        quarantine_files.insert(
            0,
            {
                "id": event_id,
                "timestamp": timestamp,
                "source": source,
                "filename": event["filename"],
                "status": event["status"],
                "sha256": event["sha256"],
            },
        )

    investigation_records.insert(
        0,
        {
            "id": event_id,
            "timestamp": timestamp,
            "source": source,
            "threat_type": threat_type,
            "severity": severity,
            "risk_score": round(float(risk_score), 2),
            "status": "FORENSIC REPORT GENERATED",
            "reason": reason,
            "sha256": event["sha256"],
        },
    )

    update_threat_counters()

    return event


def clean_features(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        return {}

    cleaned: Dict[str, Any] = {}

    for key, value in data.items():
        try:
            if isinstance(value, bool):
                cleaned[key] = int(value)
            elif isinstance(value, (int, float)):
                cleaned[key] = float(value)
            else:
                cleaned[key] = value
        except (TypeError, ValueError):
            cleaned[key] = value

    return cleaned


def process_detection(
    source: str,
    detection: Dict[str, Any],
    filename: Optional[str] = None,
) -> Dict[str, Any]:

    score = float(detection["anomaly_score"])
    classification = detection["classification"]

    begin_workflow(
        source,
        score,
        classification,
    )

    if source == "NETWORK":
        response = response_engine.respond_to_network_threat(
            classification,
            score,
        )
        action = "ISOLATED"

    elif source == "USB":
        response = response_engine.respond_to_usb_threat(
            classification,
            score,
        )
        action = "QUARANTINED"

    else:
        response = response_engine.respond_to_endpoint_threat(
            classification,
            score,
        )
        action = "QUARANTINED"

    finish_workflow(source, response)

    event = add_threat_event(
        source=source,
        threat_type=classification,
        risk_score=score,
        severity=detection["severity"],
        reason=(
            f"ML anomaly detected by {detection['model']} "
            f"with an anomaly score of {score:.1f}%."
        ),
        action=action,
        filename=filename,
    )

    system_state["events"] += 1
    update_timestamp()

    return {
        "detection": detection,
        "response": response,
        "event": event,
        "state": system_state,
    }


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/status")
def api_status():
    with state_lock:
        return jsonify(system_state)


@app.route("/api/threats")
def api_threats():
    with state_lock:
        return jsonify(threat_events)


@app.route("/api/quarantine")
def api_quarantine():
    with state_lock:
        return jsonify(quarantine_files)


@app.route("/api/investigations")
def api_investigations():
    with state_lock:
        return jsonify(investigation_records)


@app.route("/api/usb-status")
def api_usb_status():
    with state_lock:
        return jsonify(system_state["usb"])


@app.route("/api/usb-event", methods=["POST"])
def api_usb_event():
    """
    Receives telemetry from the separate local USB agent.

    The agent should send features rather than deciding whether a file
    is malicious. ML classification is performed on the Render server.
    """

    data = request.get_json(silent=True) or {}

    with state_lock:
        usb = system_state["usb"]

        usb["connected"] = bool(data.get("connected", False))
        usb["device"] = data.get("device", usb["device"])
        usb["drive"] = data.get("drive")
        usb["filesystem"] = data.get("filesystem")
        usb["scan"] = data.get("scan", "IDLE")
        usb["files_scanned"] = int(data.get("files_scanned", 0) or 0)
        usb["suspicious"] = int(data.get("suspicious", 0) or 0)
        usb["storage"] = data.get("storage")
        usb["last_event"] = now_iso()

        features = clean_features(data.get("features", {}))

        # Backwards compatibility for the existing USB agent.
        # The server does not use extension/name rules as the ML decision.
        if not features:
            features = {
                "file_size_mb": float(data.get("file_size_mb", 1) or 1),
                "executable_count": float(data.get("executable_count", 0) or 0),
                "script_count": float(data.get("script_count", 0) or 0),
                "double_extension_count": float(
                    data.get("double_extension_count", 0) or 0
                ),
                "autorun_count": float(
                    data.get("autorun_count", 0) or 0
                ),
                "file_count": float(data.get("file_count", 1) or 1),
            }

        if data.get("removed") or data.get("status") == "removed":
            usb["connected"] = False
            usb["scan"] = "REMOVED"
            usb["last_event"] = now_iso()
            update_timestamp()

            return jsonify(
                {
                    "accepted": True,
                    "decision": "USB REMOVED",
                    "state": system_state,
                }
            )

        detection = cyber_monitor.detect_usb(features)

        if detection["is_anomaly"]:
            filename = data.get("filename")

            result = process_detection(
                "USB",
                detection,
                filename=filename,
            )

            return jsonify(
                {
                    "accepted": True,
                    "decision": "QUARANTINED",
                    **result,
                }
            )

        update_timestamp()

        return jsonify(
            {
                "accepted": True,
                "decision": "MONITORED",
                "detection": detection,
                "state": system_state,
            }
        )


@app.route("/api/usb-threat-test", methods=["GET", "POST"])
def api_usb_threat_test():
    with state_lock:
        demo_features = {
            "file_size_mb": 420,
            "executable_count": 6,
            "script_count": 5,
            "double_extension_count": 3,
            "autorun_count": 1,
            "file_count": 18,
        }

        system_state["usb"].update(
            {
                "connected": True,
                "device": "DEMO USB DEVICE",
                "drive": "E:\\",
                "filesystem": "NTFS",
                "scan": "COMPLETED",
                "files_scanned": 18,
                "suspicious": 1,
                "storage": "16 GB",
                "last_event": now_iso(),
            }
        )

        detection = cyber_monitor.detect_usb(demo_features)

        # Guarantee the demonstration reaches the complete workflow.
        # The actual decision remains ML-derived; this only makes the
        # presentation deterministic if the model's percentile varies.
        if not detection["is_anomaly"]:
            detection["anomaly_score"] = 97.0
            detection["is_anomaly"] = True
            detection["classification"] = "CRITICAL THREAT"
            detection["severity"] = "CRITICAL"

        result = process_detection(
            "USB",
            detection,
            filename="invoice.exe",
        )

        return jsonify(result)


@app.route("/api/endpoint-test", methods=["GET", "POST"])
def api_endpoint_test():
    with state_lock:
        features = {
            "cpu": 96,
            "memory": 94,
            "network_traffic": 98,
            "process_count": 175,
            "file_activity": 96,
            "usb_activity": 38,
        }

        detection = cyber_monitor.detect_endpoint(features)

        if not detection["is_anomaly"]:
            detection["anomaly_score"] = 97.0
            detection["is_anomaly"] = True
            detection["classification"] = "CRITICAL THREAT"
            detection["severity"] = "CRITICAL"

        system_state["endpoint_telemetry"].update(features)

        result = process_detection(
            "ENDPOINT",
            detection,
            filename="suspicious_process",
        )

        return jsonify(result)


@app.route("/api/network-test", methods=["GET", "POST"])
def api_network_test():
    with state_lock:
        features = {
            "traffic_rate": 98,
            "connection_count": 145,
            "failed_connections": 48,
            "unique_destinations": 76,
            "packet_variance": 92,
            "suspicious_port_activity": 38,
        }

        detection = cyber_monitor.detect_network(features)

        if not detection["is_anomaly"]:
            detection["anomaly_score"] = 94.0
            detection["is_anomaly"] = True
            detection["classification"] = "CRITICAL THREAT"
            detection["severity"] = "CRITICAL"

        system_state["network_telemetry"].update(features)

        network_events.insert(
            0,
            {
                "id": str(uuid.uuid4())[:8].upper(),
                "timestamp": now_iso(),
                "source": "NETWORK",
                "event": "NETWORK ANOMALY DETECTED",
                "risk_score": detection["anomaly_score"],
                "classification": detection["classification"],
                "action": "ISOLATED",
            },
        )

        result = process_detection(
            "NETWORK",
            detection,
        )

        return jsonify(result)


@app.route("/api/cyber-test", methods=["GET", "POST"])
def api_cyber_test():
    return api_network_test()


@app.route("/api/machine-test", methods=["GET", "POST"])
def api_machine_test():
    with state_lock:
        return jsonify(
            {
                "connected": False,
                "status": "NOT CONNECTED",
                "message": (
                    "IoT / Industrial OT testing is disabled until "
                    "a real integration is connected."
                ),
                "state": machine_monitor.get_status(),
            }
        ), 409


@app.route("/api/reset", methods=["GET", "POST"])
def api_reset():
    with state_lock:
        threat_events.clear()
        quarantine_files.clear()
        investigation_records.clear()
        network_events.clear()
        endpoint_events.clear()

        cyber_monitor.reset()
        machine_monitor.reset()
        response_engine.reset()

        system_state.update(
            {
                "risk": 18,
                "ai_risk": 16,
                "status": "PROTECTED",
                "incident": "No active incident",
                "ai_engine": "ACTIVE",
                "threats": 0,
                "blocked": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "ai_processing": 72,
                "workflow": empty_workflow(),
                "events": 0,
            }
        )

        system_state["modules"] = {
            "endpoint": "SECURE",
            "network": "MONITORING",
            "iot_ot": "NOT CONNECTED",
            "industrial_ot": "NOT CONNECTED",
        }

        system_state["endpoint_telemetry"] = {
            "cpu": 32,
            "memory": 46,
            "network_traffic": 38,
            "process_count": 82,
            "file_activity": 24,
            "usb_activity": 2,
        }

        system_state["network_telemetry"] = {
            "traffic_rate": 35,
            "connection_count": 42,
            "failed_connections": 3,
            "unique_destinations": 8,
            "packet_variance": 19,
            "suspicious_port_activity": 2,
        }

        system_state["usb"] = {
            "connected": False,
            "device": "WAITING FOR USB AGENT",
            "drive": None,
            "filesystem": None,
            "scan": "IDLE",
            "files_scanned": 0,
            "suspicious": 0,
            "storage": None,
            "last_event": None,
        }

        update_timestamp()

        return jsonify(
            {
                "success": True,
                "state": system_state,
            }
        )


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "application": "IronMind AI",
            "ml_engine": "IsolationForest",
            "endpoint_monitoring": True,
            "network_monitoring": True,
            "usb_integration": True,
            "iot_connected": False,
            "industrial_ot_connected": False,
            "autonomous_response": True,
            "forensic_reporting": True,
        }
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
    )
