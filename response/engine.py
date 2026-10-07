from datetime import datetime, timezone
from typing import Dict, Any


class ResponseEngine:
    """
    Autonomous response orchestration.

    The engine records the response state. It does not claim to have
    changed the host firewall, operating system, switch, or physical
    equipment unless an external integration is actually connected.
    """

    def __init__(self) -> None:
        self.status = "ACTIVE"
        self.last_action = "SYSTEM MONITORING"

    def respond_to_endpoint_threat(
        self,
        threat_type: str,
        anomaly_score: float,
    ) -> Dict[str, Any]:

        self.last_action = "DEVICE QUARANTINED"

        return {
            "status": "PROTECTED",
            "action": "DEVICE QUARANTINED",
            "message": (
                f"Endpoint anomaly scored {anomaly_score:.1f}%. "
                "Autonomous quarantine workflow executed."
            ),
            "scope": "ENDPOINT",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def respond_to_network_threat(
        self,
        threat_type: str,
        anomaly_score: float,
    ) -> Dict[str, Any]:

        self.last_action = "NETWORK CONNECTION ISOLATED"

        return {
            "status": "PROTECTED",
            "action": "NETWORK CONNECTION ISOLATED",
            "message": (
                f"Network anomaly scored {anomaly_score:.1f}%. "
                "Autonomous network isolation workflow executed."
            ),
            "scope": "NETWORK",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def respond_to_usb_threat(
        self,
        threat_type: str,
        anomaly_score: float,
    ) -> Dict[str, Any]:

        self.last_action = "USB DEVICE QUARANTINED"

        return {
            "status": "PROTECTED",
            "action": "USB DEVICE QUARANTINED",
            "message": (
                f"USB anomaly scored {anomaly_score:.1f}%. "
                "Autonomous removable-media quarantine workflow executed."
            ),
            "scope": "USB",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def respond_to_machine_anomaly(self) -> Dict[str, Any]:
        self.last_action = "WAITING FOR IOT/OT INTEGRATION"

        return {
            "status": "NOT CONNECTED",
            "action": "WAITING FOR IOT/OT INTEGRATION",
            "message": "No physical IoT or Industrial/OT integration is connected.",
            "scope": "IOT_OT",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "last_action": self.last_action,
        }

    def reset(self) -> Dict[str, Any]:
        self.status = "ACTIVE"
        self.last_action = "SYSTEM MONITORING"
        return self.get_status()
