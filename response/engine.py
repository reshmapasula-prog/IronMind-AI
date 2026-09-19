class ResponseEngine:
    """
    Simulated AI response engine for the IronMind AI prototype.
    """

    def __init__(self):
        self.status = "ACTIVE"
        self.last_action = "SYSTEM MONITORING"

    def respond_to_threat(self, threat_type="UNKNOWN THREAT"):
        self.last_action = f"THREAT RESPONSE: {threat_type}"

        return {
            "status": "PROTECTED",
            "action": self.last_action,
            "message": "Threat detected and simulated response executed."
        }

    def respond_to_machine_anomaly(self):
        self.last_action = "MACHINE ANOMALY RESPONSE"

        return {
            "status": "PROTECTED",
            "action": self.last_action,
            "message": "Machine anomaly detected and simulated response executed."
        }

    def get_status(self):
        return {
            "status": self.status,
            "last_action": self.last_action
        }

    def reset(self):
        self.status = "ACTIVE"
        self.last_action = "SYSTEM MONITORING"

        return self.get_status()
