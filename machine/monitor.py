"""
IronMind AI - IoT / Industrial OT Connector

No physical IoT or OT system is connected yet.
Therefore this module reports NOT CONNECTED instead
of generating fake sensor telemetry.
"""


class MachineMonitor:
    def __init__(self):
        self.status = "NOT CONNECTED"
        self.temperature = None
        self.vibration = None
        self.rpm = None
        self.anomaly = False

    def get_status(self):
        return {
            "status": "NOT CONNECTED",
            "connection": "WAITING FOR INTEGRATION",
            "temperature": None,
            "vibration": None,
            "rpm": None,
            "anomaly": False,
            "message": (
                "IoT / Industrial OT hardware is not connected."
            ),
        }

    def simulate_anomaly(self):
        return {
            "success": False,
            "status": "NOT CONNECTED",
            "message": (
                "IoT / Industrial OT simulation is disabled. "
                "Connect a real sensor or OT integration first."
            ),
        }

    def reset(self):
        self.status = "NOT CONNECTED"
        self.temperature = None
        self.vibration = None
        self.rpm = None
        self.anomaly = False
