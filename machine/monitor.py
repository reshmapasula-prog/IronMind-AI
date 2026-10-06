"""
IronMind AI - IoT / Industrial OT Monitor

Current state:
    NOT CONNECTED

This module is intentionally prepared for future IoT/OT
integration but does not fabricate live hardware telemetry.
"""


class MachineMonitor:

    def __init__(self):

        self.status = "NOT CONNECTED"

        self.connected = False

        self.sensors = 0

        self.temperature = None

        self.vibration = None

        self.rpm = None

        self.alerts = 0

    def get_status(self):

        return {
            "status": "NOT CONNECTED",
            "connected": False,
            "sensors": 0,
            "temperature": None,
            "vibration": None,
            "rpm": None,
            "alerts": 0
        }

    def detect_anomaly(self):

        return {
            "status": "NOT CONNECTED",
            "connected": False,
            "message": (
                "IoT / Industrial OT hardware "
                "is waiting for integration."
            )
        }

    def reset(self):

        self.status = "NOT CONNECTED"

        self.connected = False

        self.sensors = 0

        self.temperature = None

        self.vibration = None

        self.rpm = None

        self.alerts = 0

        return self.get_status()
