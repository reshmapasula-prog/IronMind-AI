from datetime import datetime, timezone
from typing import Dict, Any


class MachineMonitor:
    """
    IoT / Industrial OT connector foundation.

    No physical IoT or OT system is connected to this Render deployment.
    Therefore this module deliberately reports NOT CONNECTED instead of
    generating fake machine telemetry.
    """

    def __init__(self) -> None:
        self.status = "NOT CONNECTED"
        self.integration = "WAITING FOR INTEGRATION"

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "integration": self.integration,
            "connected": False,
            "telemetry": None,
            "message": (
                "No IoT or Industrial/OT hardware is connected. "
                "Connector is ready for integration."
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def simulate_anomaly(self) -> Dict[str, Any]:
        return {
            "status": "NOT CONNECTED",
            "connected": False,
            "message": (
                "Simulation disabled. Connect an IoT/OT data source "
                "before enabling machine anomaly detection."
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def reset(self) -> Dict[str, Any]:
        return self.get_status()
