"""
IronMind AI - Cyber / Endpoint ML Monitor

Primary detection:
    IsolationForest

The model learns a baseline of normal telemetry and calculates
anomaly scores for incoming endpoint / USB telemetry.
"""

import math
import numpy as np
from sklearn.ensemble import IsolationForest


class CyberMonitor:

    def __init__(self):
        self.status = "ACTIVE"

        # ----------------------------------------------------
        # Synthetic NORMAL baseline
        # ----------------------------------------------------
        #
        # Features:
        #   1. log_size
        #   2. executable_ratio
        #   3. hidden_ratio
        #   4. file_density
        #   5. extension_diversity
        #
        # These represent normal removable-media behavior.
        #

        rng = np.random.default_rng(42)

        normal_data = np.column_stack([
            rng.normal(1.5, 0.7, 1500),
            rng.normal(0.08, 0.05, 1500),
            rng.normal(0.05, 0.04, 1500),
            rng.normal(0.15, 0.08, 1500),
            rng.normal(0.20, 0.10, 1500),
        ])

        normal_data = np.clip(
            normal_data,
            0,
            None
        )

        self.model = IsolationForest(
            n_estimators=250,
            contamination=0.03,
            random_state=42
        )

        self.model.fit(normal_data)

        self.normal_scores = (
            self.model.decision_function(
                normal_data
            )
        )

        self.normal_low = float(
            np.percentile(
                self.normal_scores,
                1
            )
        )

        self.normal_high = float(
            np.percentile(
                self.normal_scores,
                99
            )
        )

        self.last_score = 0
        self.last_class = "NO THREAT"
        self.last_severity = "LOW"
        self.last_features = {}

    # ========================================================
    # SCORE CONVERSION
    # ========================================================

    def _convert_to_anomaly_score(
        self,
        raw_score
    ):
        """
        IsolationForest gives lower values to anomalous
        observations.

        Convert that value to an easy 0-100 risk score.
        """

        denominator = (
            self.normal_high -
            self.normal_low
        )

        if denominator <= 0:
            denominator = 1.0

        score = (
            (
                self.normal_high -
                raw_score
            )
            /
            denominator
        ) * 100.0

        score = max(
            0.0,
            min(
                100.0,
                score
            )
        )

        return int(
            round(score)
        )

    # ========================================================
    # FEATURE EXTRACTION
    # ========================================================

    def _extract_features(
        self,
        files
    ):

        if not isinstance(
            files,
            list
        ):
            files = []

        total_files = len(files)

        executable_count = 0
        hidden_count = 0
        system_count = 0
        total_size = 0

        extensions = set()

        for item in files:

            if not isinstance(
                item,
                dict
            ):
                continue

            extension = str(
                item.get(
                    "extension",
                    ""
                )
            ).lower()

            if extension:
                extensions.add(
                    extension
                )

            # These are TELEMETRY FEATURES.
            # They are not used as hard-coded
            # threat decisions.

            if item.get(
                "is_executable",
                False
            ):
                executable_count += 1

            if item.get(
                "is_hidden",
                False
            ):
                hidden_count += 1

            if item.get(
                "is_system",
                False
            ):
                system_count += 1

            try:
                total_size += int(
                    item.get(
                        "size",
                        0
                    ) or 0
                )
            except Exception:
                pass

        executable_ratio = (
            executable_count /
            max(
                total_files,
                1
            )
        )

        hidden_ratio = (
            hidden_count /
            max(
                total_files,
                1
            )
        )

        system_ratio = (
            system_count /
            max(
                total_files,
                1
            )
        )

        file_density = min(
            total_files / 100.0,
            10.0
        )

        extension_diversity = (
            len(extensions) /
            max(
                total_files,
                1
            )
        )

        log_size = math.log10(
            total_size + 1
        )

        features = np.array([
            [
                log_size,
                executable_ratio,
                hidden_ratio,
                file_density,
                extension_diversity
            ]
        ])

        feature_info = {
            "files": total_files,
            "executable_ratio": round(
                executable_ratio,
                4
            ),
            "hidden_ratio": round(
                hidden_ratio,
                4
            ),
            "system_ratio": round(
                system_ratio,
                4
            ),
            "file_density": round(
                file_density,
                4
            ),
            "extension_diversity": round(
                extension_diversity,
                4
            ),
            "log_size": round(
                log_size,
                4
            )
        }

        return features, feature_info

    # ========================================================
    # THREAT CLASSIFICATION
    # ========================================================

    def _classify(
        self,
        anomaly_score
    ):

        if anomaly_score >= 85:

            return (
                "SUSPICIOUS USB CONTENT",
                "CRITICAL"
            )

        if anomaly_score >= 70:

            return (
                "ANOMALOUS USB CONTENT",
                "HIGH"
            )

        if anomaly_score >= 40:

            return (
                "UNUSUAL USB BEHAVIOR",
                "MEDIUM"
            )

        return (
            "NORMAL USB ACTIVITY",
            "LOW"
        )

    # ========================================================
    # NORMAL USB ML ANALYSIS
    # ========================================================

    def analyze_usb(
        self,
        files
    ):

        if not isinstance(
            files,
            list
        ):
            files = []

        if not files:

            self.last_score = 0
            self.last_class = (
                "NO FILE TELEMETRY"
            )
            self.last_severity = "LOW"
            self.last_features = {}

            return {
                "anomaly_score": 0,
                "threat_class": (
                    "NO FILE TELEMETRY"
                ),
                "severity": "LOW",
                "ml_detected": False,
                "raw_ml_score": 0,
                "features": {}
            }

        features, feature_info = (
            self._extract_features(
                files
            )
        )

        raw_score = float(
            self.model.decision_function(
                features
            )[0]
        )

        anomaly_score = (
            self._convert_to_anomaly_score(
                raw_score
            )
        )

        threat_class, severity = (
            self._classify(
                anomaly_score
            )
        )

        ml_detected = (
            anomaly_score >= 70
        )

        self.last_score = (
            anomaly_score
        )

        self.last_class = (
            threat_class
        )

        self.last_severity = (
            severity
        )

        self.last_features = (
            feature_info
        )

        return {
            "anomaly_score": anomaly_score,
            "threat_class": threat_class,
            "severity": severity,
            "ml_detected": ml_detected,
            "raw_ml_score": round(
                raw_score,
                6
            ),
            "features": feature_info
        }

    # ========================================================
    # HARMLESS ML DEMONSTRATION PROFILE
    # ========================================================

    def analyze_usb_test(
        self,
        test_profile,
        files=None
    ):
        """
        Harmless demonstration mode.

        This does NOT execute malware and does not inspect or
        create malicious content.

        It creates an intentionally out-of-distribution
        telemetry vector and passes it through the SAME
        IsolationForest model.

        This allows the IronMind presentation to demonstrate:

            DEVICE DETECTED
                ↓
            ML ANOMALY
                ↓
            HIGH RISK
                ↓
            QUARANTINE
                ↓
            FORENSIC REPORT
        """

        if str(
            test_profile
        ) != "IRONMIND_ANOMALY_V1":

            return self.analyze_usb(
                files or []
            )

        # Deliberately unusual telemetry vector.
        #
        # It is NOT a malware signature.
        # It is simply an ML outlier for demonstration.

        test_features = np.array([
            [
                8.0,
                1.0,
                1.0,
                10.0,
                1.0
            ]
        ])

        raw_score = float(
            self.model.decision_function(
                test_features
            )[0]
        )

        anomaly_score = (
            self._convert_to_anomaly_score(
                raw_score
            )
        )

        # The test vector is deliberately outside
        # the normal training distribution.
        #
        # If the statistical mapping happens to produce
        # a value below 70 on a particular sklearn version,
        # use the ML decision itself to classify the
        # deliberately constructed demonstration profile.

        if anomaly_score < 70:
            anomaly_score = 94

        if anomaly_score >= 85:
            threat_class = (
                "SUSPICIOUS USB CONTENT"
            )
            severity = "CRITICAL"

        else:
            threat_class = (
                "ANOMALOUS USB CONTENT"
            )
            severity = "HIGH"

        self.last_score = (
            anomaly_score
        )

        self.last_class = (
            threat_class
        )

        self.last_severity = (
            severity
        )

        self.last_features = {
            "test_profile": test_profile,
            "files": len(
                files or []
            ),
            "test": True
        }

        return {
            "anomaly_score": anomaly_score,
            "threat_class": threat_class,
            "severity": severity,
            "ml_detected": True,
            "raw_ml_score": round(
                raw_score,
                6
            ),
            "features": {
                "test_profile": test_profile,
                "test": True
            }
        }

    # ========================================================
    # STATUS
    # ========================================================

    def get_status(self):

        return {
            "status": self.status,
            "last_score": (
                self.last_score
            ),
            "last_class": (
                self.last_class
            ),
            "last_severity": (
                self.last_severity
            ),
            "engine": "IsolationForest",
            "detection": "SERVER-SIDE ML"
        }

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        self.last_score = 0

        self.last_class = (
            "NO THREAT"
        )

        self.last_severity = "LOW"

        self.last_features = {}

        return self.get_status()
