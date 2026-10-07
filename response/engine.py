"""
IronMind AI - Response Engine

The server creates an enforcement decision.

IMPORTANT:
The Render server cannot directly control the Windows endpoint.
The Windows agent performs the local enforcement and sends
an enforcement confirmation back to Render.
"""

from datetime import datetime


class ResponseEngine:

    def __init__(self):
        self.last_action = "NONE"
        self.last_target = ""
        self.last_timestamp = None
        self.last_status = "IDLE"

    def _decision(self, action, target):
        self.last_action = action
        self.last_target = target
        self.last_timestamp = datetime.now().isoformat()
        self.last_status = "REQUESTED"

        return {
            "action": action,
            "target": target,
            "timestamp": self.last_timestamp,
            "status": "REQUESTED"
        }

    # --------------------------------------------------------
    # USB
    # --------------------------------------------------------

    def quarantine_usb(self, target="USB DEVICE"):
        return self._decision(
            "QUARANTINE",
            target
        )

    # --------------------------------------------------------
    # ENDPOINT
    # --------------------------------------------------------

    def isolate_endpoint(self, target="ENDPOINT"):
        return self._decision(
            "ISOLATE_ENDPOINT",
            target
        )

    # --------------------------------------------------------
    # NETWORK
    # --------------------------------------------------------

    def isolate_network(self, target="NETWORK CONNECTION"):
        return self._decision(
            "ISOLATE_NETWORK",
            target
        )

    # --------------------------------------------------------
    # GENERIC BLOCK
    # --------------------------------------------------------

    def block(self, target="UNKNOWN"):
        return self._decision(
            "BLOCK",
            target
        )

    # --------------------------------------------------------
    # ENFORCEMENT CONFIRMATION
    # --------------------------------------------------------

    def confirm(self, action, target, success):
        self.last_action = action
        self.last_target = target
        self.last_timestamp = datetime.now().isoformat()

        self.last_status = (
            "ENFORCED"
            if success
            else "FAILED"
        )

        return {
            "action": action,
            "target": target,
            "timestamp": self.last_timestamp,
            "status": self.last_status
        }

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    def get_status(self):
        return {
            "last_action": self.last_action,
            "last_target": self.last_target,
            "last_timestamp": self.last_timestamp,
            "last_status": self.last_status
        }

    # --------------------------------------------------------
    # RESET
    # --------------------------------------------------------

    def reset(self):
        self.last_action = "NONE"
        self.last_target = ""
        self.last_timestamp = None
        self.last_status = "IDLE"

        return self.get_status()
