class CyberMonitor:
    """
    Simulated cybersecurity monitoring module
    for the IronMind AI prototype.
    """

    def __init__(self):
        self.status = "MONITORING"
        self.threat_level = "LOW"
        self.threats_detected = 0
        self.blocked = 24
        self.network = "MONITORING"
        self.endpoint = "SECURE"

    def get_status(self):
        return {
            "status": self.status,
            "threat_level": self.threat_level,
            "threats_detected": self.threats_detected,
            "blocked": self.blocked,
            "network": self.network,
            "endpoint": self.endpoint
        }

    def detect_threat(self):
        self.status = "THREAT DETECTED"
        self.threat_level = "HIGH"
        self.threats_detected += 1
        self.endpoint = "THREAT BLOCKED"
        self.blocked += 1

        return self.get_status()

    def reset(self):
        self.status = "MONITORING"
        self.threat_level = "LOW"
        self.threats_detected = 0
        self.network = "MONITORING"
        self.endpoint = "SECURE"

        return self.get_status()
