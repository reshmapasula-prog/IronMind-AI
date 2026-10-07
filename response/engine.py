"""
IronMind AI - Autonomous Response Engine

This module records and orchestrates response decisions.

Important:
The Render server does not claim to have changed the Windows
firewall, disabled an account, or physically isolated a device
unless a real endpoint integration performs that action.
"""


from datetime import datetime, timezone


class ResponseEngine:
    def __init__(self):
        self.status = "ACTIVE"
        self.last_action = "SYSTEM MONITORING"

    @staticmethod
    def _timestamp():
        return datetime.now(timezone.utc).isoformat()

    def respond_to_threat(
        self,
        source="UNKNOWN",
        anomaly_score=0,
        threat_class="UNKNOWN",
        severity="LOW",
    ):
        score = int(anomaly_score or 0)

        if score >= 70:
            action = "QUARANTINE / ISOLATE"
            response_status = "CONTAINMENT REQUIRED"
        else:
            action = "MONITOR"
            response_status = "MONITORING"

        self.last_action = action

        return {
            "timestamp": self._timestamp(),
            "source": source,
            "anomaly_score": score,
            "threat_class": threat_class,
            "severity": severity,
            "action": action,
            "status": response_status,
            "execution": (
                "RESPONSE DECISION RECORDED"
            ),
        }

    def respond_to_machine_anomaly(self):
        self.last_action = "WAITING FOR OT INTEGRATION"

        return {
            "timestamp": self._timestamp(),
            "action": "WAITING FOR INTEGRATION",
            "status": "NOT CONNECTED",
            "execution": "NO OT ACTION EXECUTED",
        }

    def get_status(self):
        return {
            "status": self.status,
            "last_action": self.last_action,
        }

    def reset(self):
        self.status = "ACTIVE"
        self.last_action = "SYSTEM MONITORING"
