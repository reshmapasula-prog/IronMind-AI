class MachineMonitor:
    """
    Simulated machine / IoT monitoring module
    for the IronMind AI prototype.
    """

    def __init__(self):
        self.status = "READY"
        self.temperature = 62
        self.vibration = 3.2
        self.rpm = 1450
        self.anomaly = False

    def get_status(self):
        return {
            "status": self.status,
            "temperature": self.temperature,
            "vibration": self.vibration,
            "rpm": self.rpm,
            "anomaly": self.anomaly
        }

    def simulate_anomaly(self):
        self.status = "WARNING"
        self.temperature = 82
        self.vibration = 7.4
        self.rpm = 1780
        self.anomaly = True

        return self.get_status()

    def reset(self):
        self.status = "READY"
        self.temperature = 62
        self.vibration = 3.2
        self.rpm = 1450
        self.anomaly = False

        return self.get_status()
