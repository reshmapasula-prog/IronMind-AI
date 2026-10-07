"""
IronMind AI - ML Cyber Monitor

Detection architecture:

Telemetry
    ↓
Feature Extraction
    ↓
Isolation Forest
    ↓
Anomaly Score
    ↓
Threat Classification
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

import numpy as np
from sklearn.ensemble import IsolationForest


class CyberMonitor:
    def __init__(self) -> None:
        self.status = "MONITORING"
        self.engine = "IsolationForest"
        self.detection_method = "SERVER-SIDE ML"

        self.endpoint_model = self._build_endpoint_model()
        self.network_model = self._build_network_model()
        self.usb_model = self._build_usb_model()

        self.threats_detected = 0
        self.blocked = 0

    # ---------------------------------------------------------
    # MODEL BUILDERS
    # ---------------------------------------------------------

    def _build_endpoint_model(self) -> IsolationForest:
        rng = np.random.default_rng(42)

        normal = np.column_stack(
            [
                rng.normal(30, 8, 1500),       # CPU
                rng.normal(45, 10, 1500),      # memory
                rng.normal(35, 12, 1500),      # network traffic
                rng.normal(8, 3, 1500),        # process activity
                rng.normal(2, 1, 1500),        # privilege activity
            ]
        )

        model = IsolationForest(
            n_estimators=300,
            contamination=0.03,
            random_state=42,
        )

        model.fit(normal)
        return model

    def _build_network_model(self) -> IsolationForest:
        rng = np.random.default_rng(43)

        normal = np.column_stack(
            [
                rng.normal(30, 10, 1500),      # traffic
                rng.normal(15, 5, 1500),       # connections
                rng.normal(4, 2, 1500),        # failed connections
                rng.normal(2, 1, 1500),        # unusual ports
                rng.normal(3, 1.5, 1500),      # packet burst
            ]
        )

        model = IsolationForest(
            n_estimators=300,
            contamination=0.03,
            random_state=43,
        )

        model.fit(normal)
        return model

    def _build_usb_model(self) -> IsolationForest:
        rng = np.random.default_rng(44)

        normal = np.column_stack(
            [
                rng.normal(3.0, 0.8, 1500),    # average log file size
                rng.beta(2, 8, 1500),           # executable ratio
                rng.beta(2, 10, 1500),          # script ratio
                rng.beta(1.5, 12, 1500),        # hidden ratio
                rng.beta(1, 15, 1500),          # system ratio
                rng.normal(5, 2, 1500),         # files per MB
                rng.uniform(0.5, 2.5, 1500),    # extension diversity
            ]
        )

        model = IsolationForest(
            n_estimators=300,
            contamination=0.03,
            random_state=44,
        )

        model.fit(normal)
        return model

    # ---------------------------------------------------------
    # COMMON SCORE CONVERSION
    # ---------------------------------------------------------

    @staticmethod
    def _score(decision_value: float) -> int:
        """
        Convert IsolationForest decision function into
        an easy-to-display 0-100 anomaly score.

        Higher = more anomalous.
        """

        value = float(decision_value)

        score = 50.0 - (value * 220.0)

        score = max(0.0, min(100.0, score))

        return int(round(score))

    @staticmethod
    def _severity(score: int) -> str:
        if score >= 85:
            return "CRITICAL"

        if score >= 70:
            return "HIGH"

        if score >= 40:
            return "MEDIUM"

        return "LOW"

    # ---------------------------------------------------------
    # USB FEATURE EXTRACTION
    # ---------------------------------------------------------

    @staticmethod
    def _usb_features(files: List[Dict[str, Any]]) -> List[float]:
        if not files:
            return [
                2.5,
                0.0,
                0.0,
                0.0,
                0.0,
                2.0,
                1.0,
            ]

        total = len(files)

        sizes = []
        extensions = set()

        executable_count = 0
        script_count = 0
        hidden_count = 0
        system_count = 0

        for item in files:
            try:
                size = int(item.get("size", 0) or 0)
            except Exception:
                size = 0

            sizes.append(max(size, 1))

            extension = str(
                item.get("extension", "")
                or ""
            ).lower()

            if not extension:
                name = str(item.get("name", ""))
                if "." in name:
                    extension = "." + name.rsplit(".", 1)[-1].lower()

            if extension:
                extensions.add(extension)

            # These are FEATURES only.
            # They do not independently decide whether a file is malicious.

            if extension in {
                ".exe",
                ".dll",
                ".scr",
                ".com",
                ".msi",
                ".sys",
            }:
                executable_count += 1

            if extension in {
                ".ps1",
                ".bat",
                ".cmd",
                ".vbs",
                ".vbe",
                ".js",
                ".jse",
                ".wsf",
            }:
                script_count += 1

            if bool(item.get("is_hidden", False)):
                hidden_count += 1

            if bool(item.get("is_system", False)):
                system_count += 1

        average_size = sum(sizes) / len(sizes)

        average_size_mb = average_size / (1024 * 1024)

        log_size = math.log1p(average_size_mb)

        executable_ratio = executable_count / total
        script_ratio = script_count / total
        hidden_ratio = hidden_count / total
        system_ratio = system_count / total

        file_density = total / max(
            sum(sizes) / (1024 * 1024),
            1.0,
        )

        extension_diversity = len(extensions)

        return [
            float(log_size),
            float(executable_ratio),
            float(script_ratio),
            float(hidden_ratio),
            float(system_ratio),
            float(file_density),
            float(extension_diversity),
        ]

    # ---------------------------------------------------------
    # USB ML ANALYSIS
    # ---------------------------------------------------------

    def analyze_usb(
        self,
        files: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        features = self._usb_features(files)

        vector = np.array(
            [features],
            dtype=float,
        )

        decision = float(
            self.usb_model.decision_function(vector)[0]
        )

        prediction = int(
            self.usb_model.predict(vector)[0]
        )

        anomaly_score = self._score(decision)

        # IsolationForest can occasionally score a clearly
        # anomalous prototype too conservatively. The following
        # is a model calibration floor based on the ML prediction.
        if prediction == -1:
            anomaly_score = max(
                anomaly_score,
                72,
            )

        severity = self._severity(anomaly_score)

        if anomaly_score >= 85:
            threat_class = "CRITICAL USB ANOMALY"

        elif anomaly_score >= 70:
            threat_class = "HIGH USB ANOMALY"

        elif anomaly_score >= 40:
            threat_class = "MEDIUM USB ANOMALY"

        else:
            threat_class = "NORMAL USB ACTIVITY"

        return {
            "anomaly_score": int(anomaly_score),
            "threat_class": threat_class,
            "severity": severity,
            "ml_prediction": (
                "ANOMALY"
                if prediction == -1
                else "NORMAL"
            ),
            "ml_detected": True,
            "engine": self.engine,
            "detection_method": self.detection_method,
            "raw_score": round(decision, 6),
            "features": {
                "log_average_file_size": round(features[0], 4),
                "executable_ratio": round(features[1], 4),
                "script_ratio": round(features[2], 4),
                "hidden_ratio": round(features[3], 4),
                "system_ratio": round(features[4], 4),
                "file_density": round(features[5], 4),
                "extension_diversity": round(features[6], 4),
            },
        }

    # ---------------------------------------------------------
    # ENDPOINT ML ANALYSIS
    # ---------------------------------------------------------

    def analyze_endpoint(
        self,
        cpu: float,
        memory: float,
        network_traffic: float,
        process_activity: float,
        privilege_activity: float,
    ) -> Dict[str, Any]:

        vector = np.array(
            [
                [
                    cpu,
                    memory,
                    network_traffic,
                    process_activity,
                    privilege_activity,
                ]
            ],
            dtype=float,
        )

        decision = float(
            self.endpoint_model.decision_function(vector)[0]
        )

        prediction = int(
            self.endpoint_model.predict(vector)[0]
        )

        score = self._score(decision)

        if prediction == -1:
            score = max(score, 72)

        severity = self._severity(score)

        if score >= 85:
            threat_class = "CRITICAL ENDPOINT ANOMALY"
        elif score >= 70:
            threat_class = "HIGH ENDPOINT ANOMALY"
        elif score >= 40:
            threat_class = "MEDIUM ENDPOINT ANOMALY"
        else:
            threat_class = "NORMAL ENDPOINT BEHAVIOR"

        return {
            "anomaly_score": score,
            "threat_class": threat_class,
            "severity": severity,
            "ml_prediction": (
                "ANOMALY"
                if prediction == -1
                else "NORMAL"
            ),
            "ml_detected": True,
            "engine": self.engine,
            "detection_method": self.detection_method,
            "raw_score": round(decision, 6),
        }

    # ---------------------------------------------------------
    # NETWORK ML ANALYSIS
    # ---------------------------------------------------------

    def analyze_network(
        self,
        traffic: float,
        connections: float,
        failed_connections: float,
        unusual_ports: float,
        packet_burst: float,
    ) -> Dict[str, Any]:

        vector = np.array(
            [
                [
                    traffic,
                    connections,
                    failed_connections,
                    unusual_ports,
                    packet_burst,
                ]
            ],
            dtype=float,
        )

        decision = float(
            self.network_model.decision_function(vector)[0]
        )

        prediction = int(
            self.network_model.predict(vector)[0]
        )

        score = self._score(decision)

        if prediction == -1:
            score = max(score, 72)

        severity = self._severity(score)

        if score >= 85:
            threat_class = "CRITICAL NETWORK ANOMALY"
        elif score >= 70:
            threat_class = "HIGH NETWORK ANOMALY"
        elif score >= 40:
            threat_class = "MEDIUM NETWORK ANOMALY"
        else:
            threat_class = "NORMAL NETWORK TRAFFIC"

        return {
            "anomaly_score": score,
            "threat_class": threat_class,
            "severity": severity,
            "ml_prediction": (
                "ANOMALY"
                if prediction == -1
                else "NORMAL"
            ),
            "ml_detected": True,
            "engine": self.engine,
            "detection_method": self.detection_method,
            "raw_score": round(decision, 6),
        }

    # ---------------------------------------------------------
    # STATUS
    # ---------------------------------------------------------

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "engine": self.engine,
            "detection_method": self.detection_method,
            "threats_detected": self.threats_detected,
            "blocked": self.blocked,
        }

    def reset(self) -> None:
        self.status = "MONITORING"
        self.threats_detected = 0
        self.blocked = 0
