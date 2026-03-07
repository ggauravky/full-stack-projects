"""
CyberSentinel - Alert Manager Module
======================================
Central alert management system that receives threat data from
detection modules, creates structured alert objects, stores them
in memory for dashboard access, and dispatches them to the notifier.
"""

import time
import threading
from collections import deque

from app.utils.logger import get_logger


logger = get_logger("alert_manager")


# Severity levels and their priority (higher = more critical)
SEVERITY_PRIORITY = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


class AlertManager:
    """
    Central alert management and storage system.

    Receives raw threat data from detection engines, creates
    structured alert objects with unique IDs, stores them in
    a bounded in-memory queue, and dispatches alerts to the
    Notifier for terminal/log output.

    Attributes:
        max_alerts: Maximum number of alerts to store in memory.
        alerts: Thread-safe deque of stored alert dictionaries.
        total_alerts: Total number of alerts generated (lifetime counter).
    """

    def __init__(self, max_alerts: int = 500):
        """
        Initialize the Alert Manager.

        Args:
            max_alerts: Maximum alerts to keep in memory (oldest are evicted).
        """
        self.max_alerts = max_alerts

        # Thread-safe alert storage (deque automatically evicts oldest)
        self.alerts: deque[dict] = deque(maxlen=max_alerts)

        # Lifetime alert counter
        self.total_alerts: int = 0

        # Lock for thread-safe operations
        self._lock = threading.Lock()

        # Notifier instance (set externally)
        self._notifier = None

        # Statistics counters per threat type
        self._stats: dict[str, int] = {}

        logger.info(
            "AlertManager initialized | max_in_memory=%d", max_alerts
        )

    def set_notifier(self, notifier) -> None:
        """
        Register a Notifier instance for alert output.

        Args:
            notifier: Notifier instance with a `send_alert(alert)` method.
        """
        self._notifier = notifier
        logger.debug("Notifier registered with AlertManager")

    def process_alert(self, threat_data: dict) -> dict:
        """
        Process incoming threat data from detection engines.

        Creates a structured alert object, stores it in memory,
        updates statistics, and dispatches to the notifier.

        This method is designed to be used as the alert callback
        for RuleEngine and AnomalyDetector.

        Args:
            threat_data: Dictionary containing:
                - threat_type (str): Type of threat (e.g., PORT_SCAN)
                - severity (str): Severity level (LOW/MEDIUM/HIGH/CRITICAL)
                - src_ip (str): Source IP involved
                - details (str): Human-readable description
                - timestamp (float): Time of detection
                - metadata (dict, optional): Additional data

        Returns:
            The structured alert dictionary that was created.
        """
        with self._lock:
            self.total_alerts += 1
            alert_id = self.total_alerts

        # Build the structured alert object
        alert = {
            "id": alert_id,
            "timestamp": threat_data.get("timestamp", time.time()),
            "threat_type": threat_data.get("threat_type", "UNKNOWN"),
            "severity": threat_data.get("severity", "LOW"),
            "severity_priority": SEVERITY_PRIORITY.get(
                threat_data.get("severity", "LOW"), 0
            ),
            "src_ip": threat_data.get("src_ip", "unknown"),
            "details": threat_data.get("details", "No details provided"),
            "metadata": threat_data.get("metadata", {}),
        }

        # Store the alert in memory
        with self._lock:
            self.alerts.append(alert)

            # Update per-type statistics
            threat_type = alert["threat_type"]
            self._stats[threat_type] = self._stats.get(threat_type, 0) + 1

        logger.warning(
            "🚨 ALERT #%d [%s] Severity: %s | Source: %s | %s",
            alert_id,
            alert["threat_type"],
            alert["severity"],
            alert["src_ip"],
            alert["details"],
        )

        # Dispatch to notifier for terminal/log output
        if self._notifier:
            try:
                self._notifier.send_alert(alert)
            except Exception as e:
                logger.error("Failed to send alert to notifier: %s", e)

        return alert

    def get_recent_alerts(self, count: int = 50) -> list[dict]:
        """
        Get the most recent alerts.

        Args:
            count: Maximum number of alerts to return.

        Returns:
            List of alert dictionaries, most recent first.
        """
        with self._lock:
            # Convert deque to list and return the last N items (reversed)
            alerts_list = list(self.alerts)
            return list(reversed(alerts_list[-count:]))

    def get_alerts_by_severity(self, severity: str) -> list[dict]:
        """
        Get all stored alerts filtered by severity level.

        Args:
            severity: Severity level to filter (LOW/MEDIUM/HIGH/CRITICAL).

        Returns:
            List of matching alert dictionaries.
        """
        with self._lock:
            return [
                alert for alert in self.alerts
                if alert["severity"] == severity.upper()
            ]

    def get_suspicious_ips(self) -> list[dict]:
        """
        Get a summary of suspicious IP addresses from stored alerts.

        Returns:
            List of dicts with IP info, sorted by alert count (descending):
            [{"ip": str, "alert_count": int, "threat_types": list}, ...]
        """
        ip_data: dict[str, dict] = {}

        with self._lock:
            for alert in self.alerts:
                ip = alert["src_ip"]
                # Skip generic network-level alerts
                if ip == "NETWORK":
                    continue

                if ip not in ip_data:
                    ip_data[ip] = {
                        "ip": ip,
                        "alert_count": 0,
                        "threat_types": set(),
                        "max_severity": 0,
                    }

                ip_data[ip]["alert_count"] += 1
                ip_data[ip]["threat_types"].add(alert["threat_type"])
                ip_data[ip]["max_severity"] = max(
                    ip_data[ip]["max_severity"],
                    alert["severity_priority"],
                )

        # Convert sets to lists and sort by alert count
        result = []
        for data in ip_data.values():
            data["threat_types"] = sorted(list(data["threat_types"]))
            # Reverse-map priority to severity name
            severity_names = {v: k for k, v in SEVERITY_PRIORITY.items()}
            data["max_severity"] = severity_names.get(
                data["max_severity"], "UNKNOWN"
            )
            result.append(data)

        return sorted(result, key=lambda x: x["alert_count"], reverse=True)

    def get_stats(self) -> dict:
        """
        Get alert statistics summary.

        Returns:
            Dictionary with:
                - total_alerts: Lifetime alert count
                - alerts_in_memory: Current count of stored alerts
                - by_type: Dict of {threat_type: count}
                - by_severity: Dict of {severity: count}
        """
        with self._lock:
            by_severity: dict[str, int] = {}
            for alert in self.alerts:
                sev = alert["severity"]
                by_severity[sev] = by_severity.get(sev, 0) + 1

            return {
                "total_alerts": self.total_alerts,
                "alerts_in_memory": len(self.alerts),
                "by_type": dict(self._stats),
                "by_severity": by_severity,
            }
