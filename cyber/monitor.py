from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

import numpy as np
from sklearn.ensemble import IsolationForest


class CyberMonitor:
    """
    ML-based endpoint and network anomaly detector.

    Two separate IsolationForest models are used because endpoint
    telemetry and network telemetry have different feature semantics.

    This is an anomaly-detection prototype, not a pretrained malware model.
    """

    ENDPOINT_FEATURES = [
        "cpu",
        "memory",
        "network_traffic",
        "process_count",
        "file_activity",
        "usb_activity",
    ]

    NETWORK_FEATURES = [
        "traffic_rate",
        "connection_count",
        "failed_connections",
        "unique_destinations",
        "packet_variance",
        "suspicious_port_activity",
    ]

    USB_FEATURES = [
        "file_size_mb",
        "executable_count",
        "script_count",
        "double_extension_count",
        "autorun_count",
        "file_count",
    ]

    def __init__(self) -> None:
        self.status = "MONITORING"

        self.endpoint_model = self._build_model(random_state=11)
        self.network_model = self._build_model(random_state=22)
        self.usb_model = self._build_model(random_state=33)

        self.endpoint_reference = self._fit_endpoint_model()
        self.network_reference = self._fit_network_model()
        self.usb_reference = self._fit_usb_model()

        self.last_detection: Dict[str, Any] = {
            "source": None,
            "anomaly_score": 0,
            "is_anomaly": False,
            "classification": "NORMAL",
            "timestamp": None,
        }

    @staticmethod
    def _build_model(random_state: int) -> IsolationForest:
        return IsolationForest(
            n_estimators=160,
            contamination=0.05,
            random_state=random_state,
            n_jobs=-1,
        )

    @staticmethod
    def _clip(value: float, low: float = 0.0, high: float = 100.0) -> float:
        return float(max(low, min(high, value)))

    @staticmethod
    def _reference_distribution(
        model: IsolationForest,
        data: np.ndarray,
    ) -> np.ndarray:
        scores = model.decision_function(data)
        return np.asarray(scores, dtype=float)

    def _fit_endpoint_model(self) -> np.ndarray:
        rng = np.random.default_rng(101)

        normal = np.column_stack(
            [
                rng.normal(35, 8, 500).clip(5, 95),
                rng.normal(48, 9, 500).clip(10, 95),
                rng.normal(30, 10, 500).clip(1, 95),
                rng.normal(85, 15, 500).clip(25, 180),
                rng.normal(30, 12, 500).clip(1, 100),
                rng.normal(8, 5, 500).clip(0, 40),
            ]
        )

        self.endpoint_model.fit(normal)
        return self._reference_distribution(self.endpoint_model, normal)

    def _fit_network_model(self) -> np.ndarray:
        rng = np.random.default_rng(202)

        normal = np.column_stack(
            [
                rng.normal(35, 10, 500).clip(1, 100),
                rng.normal(45, 12, 500).clip(1, 150),
                rng.normal(4, 2, 500).clip(0, 20),
                rng.normal(8, 3, 500).clip(1, 30),
                rng.normal(20, 6, 500).clip(1, 70),
                rng.normal(3, 2, 500).clip(0, 20),
            ]
        )

        self.network_model.fit(normal)
        return self._reference_distribution(self.network_model, normal)

    def _fit_usb_model(self) -> np.ndarray:
        rng = np.random.default_rng(303)

        normal = np.column_stack(
            [
                rng.lognormal(1.5, 1.0, 500).clip(0.01, 500),
                rng.poisson(0.3, 500).clip(0, 5),
                rng.poisson(0.4, 500).clip(0, 6),
                rng.poisson(0.05, 500).clip(0, 3),
                rng.poisson(0.01, 500).clip(0, 2),
                rng.normal(80, 30, 500).clip(1, 500),
            ]
        )

        self.usb_model.fit(normal)
        return self._reference_distribution(self.usb_model, normal)

    def _score(
        self,
        model: IsolationForest,
        reference: np.ndarray,
        vector: np.ndarray,
    ) -> float:
        raw = float(model.decision_function(vector.reshape(1, -1))[0])

        # Lower IsolationForest scores indicate stronger anomalies.
        # Convert the model score into a 0-100 anomaly score relative
        # to the normal reference distribution.
        percentile = float(np.mean(reference >= raw))

        score = percentile * 100.0
        return round(self._clip(score), 2)

    @staticmethod
    def _classify(score: float) -> str:
        if score >= 90:
            return "CRITICAL THREAT"
        if score >= 75:
            return "HIGH-RISK ANOMALY"
        if score >= 55:
            return "MEDIUM-RISK ANOMALY"
        if score >= 35:
            return "LOW-RISK ANOMALY"
        return "NORMAL"

    @staticmethod
    def _severity(score: float) -> str:
        if score >= 90:
            return "CRITICAL"
        if score >= 75:
            return "HIGH"
        if score >= 55:
            return "MEDIUM"
        return "LOW"

    def _result(
        self,
        source: str,
        score: float,
        features: Dict[str, Any],
    ) -> Dict[str, Any]:
        classification = self._classify(score)
        is_anomaly = score >= 55

        result = {
            "source": source,
            "anomaly_score": round(score, 2),
            "is_anomaly": is_anomaly,
            "classification": classification,
            "severity": self._severity(score),
            "features": features,
            "model": "IsolationForest",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self.last_detection = result
        self.status = "ANOMALY DETECTED" if is_anomaly else "MONITORING"

        return result

    def detect_endpoint(self, features: Dict[str, Any]) -> Dict[str, Any]:
        vector = np.array(
            [
                float(features.get("cpu", 35)),
                float(features.get("memory", 48)),
                float(features.get("network_traffic", 30)),
                float(features.get("process_count", 80)),
                float(features.get("file_activity", 30)),
                float(features.get("usb_activity", 5)),
            ],
            dtype=float,
        )

        score = self._score(
            self.endpoint_model,
            self.endpoint_reference,
            vector,
        )

        return self._result("ENDPOINT", score, features)

    def detect_network(self, features: Dict[str, Any]) -> Dict[str, Any]:
        vector = np.array(
            [
                float(features.get("traffic_rate", 35)),
                float(features.get("connection_count", 45)),
                float(features.get("failed_connections", 4)),
                float(features.get("unique_destinations", 8)),
                float(features.get("packet_variance", 20)),
                float(features.get("suspicious_port_activity", 3)),
            ],
            dtype=float,
        )

        score = self._score(
            self.network_model,
            self.network_reference,
            vector,
        )

        return self._result("NETWORK", score, features)

    def detect_usb(self, features: Dict[str, Any]) -> Dict[str, Any]:
        vector = np.array(
            [
                float(features.get("file_size_mb", 1)),
                float(features.get("executable_count", 0)),
                float(features.get("script_count", 0)),
                float(features.get("double_extension_count", 0)),
                float(features.get("autorun_count", 0)),
                float(features.get("file_count", 1)),
            ],
            dtype=float,
        )

        score = self._score(
            self.usb_model,
            self.usb_reference,
            vector,
        )

        return self._result("USB", score, features)

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "model": "IsolationForest",
            "models": {
                "endpoint": "ACTIVE",
                "network": "ACTIVE",
                "usb": "ACTIVE",
            },
            "last_detection": self.last_detection,
        }

    def reset(self) -> Dict[str, Any]:
        self.status = "MONITORING"
        self.last_detection = {
            "source": None,
            "anomaly_score": 0,
            "is_anomaly": False,
            "classification": "NORMAL",
            "timestamp": None,
        }
        return self.get_status()
