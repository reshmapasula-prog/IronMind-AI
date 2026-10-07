"""
IronMind AI - Autonomous Response Engine

This module records and models defensive decisions.

Important:
The Render server cannot physically disconnect a USB device
or directly manipulate the user's Windows machine.

The local USB agent performs local quarantine when instructed.
Render records the security decision and forensic evidence.
"""


from datetime import datetime


class ResponseEngine:

    def __init__(self):

        self.last_action = "NONE"

        self.last_target = ""

        self.last_timestamp = None

    def _record(
        self,
        action,
        target
    ):

        self.last_action = action

        self.last_target = target

        self.last_timestamp = (
            datetime.now().isoformat()
        )

        return {
            "action": action,
            "target": target,
            "timestamp": self.last_timestamp,
            "status": "EXECUTED"
        }

    # ========================================================
    # USB
    # ========================================================

    def quarantine_usb(
        self,
        target="USB DEVICE"
    ):

        return self._record(
            "QUARANTINE",
            target
        )

    # ========================================================
    # ENDPOINT
    # ========================================================

    def isolate_endpoint(
        self,
        target="ENDPOINT"
    ):

        return self._record(
            "ISOLATE",
            target
        )

    # ========================================================
    # NETWORK
    # ========================================================

    def isolate_network(
        self,
        target="NETWORK CONNECTION"
    ):

        return self._record(
            "NETWORK ISOLATION",
            target
        )

    # ========================================================
    # GENERIC BLOCK
    # ========================================================

    def block(
        self,
        target="UNKNOWN"
    ):

        return self._record(
            "BLOCK",
            target
        )

    # ========================================================
    # STATUS
    # ========================================================

    def get_status(self):

        return {
            "last_action": self.last_action,
            "last_target": self.last_target,
            "last_timestamp": self.last_timestamp
        }

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        self.last_action = "NONE"

        self.last_target = ""

        self.last_timestamp = None

        return self.get_status()
