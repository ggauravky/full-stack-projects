"""
CyberSentinel - Rule Engine Module
====================================
Implements signature-based detection rules for identifying
suspicious network behavior patterns:

1. Port Scan Detection:
   Detects when a single IP accesses too many unique ports
   within a configurable time window.

2. Traffic Spike Detection:
   Detects abnormally high packet rates that may indicate
   a DoS attack or network flood.
"""

import time
from collections import defaultdict
from typing import Callable

from app.utils.logger import get_logger


logger = get_logger("rule_engine")


class RuleEngine:
    """
    Signature-based threat detection engine.

    Analyzes parsed packet data against predefined rules and
    triggers alerts when thresholds are exceeded.

    Attributes:
        port_scan_threshold: Max unique ports per IP before alert.
        port_scan_window: Time window (seconds) for port tracking.
        spike_threshold: Max packets/second before alert.
        spike_window: Time window (seconds) for rate calculation.
    """

    def __init__(
        self,
        port_scan_threshold: int = 15,
        port_scan_window: int = 60,
        spike_threshold: int = 100,
        spike_window: int = 10,
        alert_cooldown: int = 30,
    ):
        """
        Initialize the Rule Engine with detection thresholds.

        Args:
            port_scan_threshold: Number of unique ports to trigger a port scan alert.
            port_scan_window: Time window in seconds for port scan tracking.
            spike_threshold: Packets per second to trigger a traffic spike alert.
            spike_window: Time window in seconds for spike rate calculation.
            alert_cooldown: Seconds before re-alerting the same threat from the same IP.
        """
        self.port_scan_threshold = port_scan_threshold
        self.port_scan_window = port_scan_window
        self.spike_threshold = spike_threshold
        self.spike_window = spike_window
        self.alert_cooldown = alert_cooldown

        # ---- Internal State ----

        # Port scan tracking: {src_ip: [(timestamp, dst_port), ...]}
        self._port_access_log: dict[str, list[tuple[float, int]]] = defaultdict(list)

        # Traffic spike tracking: list of packet timestamps
        self._packet_timestamps: list[float] = []

        # Alert cooldown tracking: {(threat_type, src_ip): last_alert_time}
        self._alert_cooldowns: dict[tuple[str, str], float] = {}

        # Registered alert callback
        self._alert_callback: Callable[[dict], None] | None = None

        logger.info(
            "RuleEngine initialized | port_scan=%d ports in %ds | "
            "spike=%d pps in %ds | cooldown=%ds",
            port_scan_threshold,
            port_scan_window,
            spike_threshold,
            spike_window,
            alert_cooldown,
        )

    def set_alert_callback(self, callback: Callable[[dict], None]) -> None:
        """
        Register a callback function to receive alert notifications.

        The callback receives a dictionary:
            {
                "threat_type": str,
                "severity": str,
                "src_ip": str,
                "details": str,
                "timestamp": float,
            }

        Args:
            callback: Function to call when a threat is detected.
        """
        self._alert_callback = callback

    def _is_cooldown_active(self, threat_type: str, src_ip: str) -> bool:
        """
        Check if the alert cooldown is active for a specific threat+IP combo.
        Prevents flooding the alert system with duplicate alerts.
        """
        key = (threat_type, src_ip)
        last_alert = self._alert_cooldowns.get(key, 0)
        return (time.time() - last_alert) < self.alert_cooldown

    def _trigger_alert(self, alert_data: dict) -> None:
        """
        Trigger an alert via the registered callback.

        Updates cooldown tracking and dispatches the alert.
        """
        threat_type = alert_data["threat_type"]
        src_ip = alert_data.get("src_ip", "unknown")

        # Check cooldown to avoid alert flooding
        if self._is_cooldown_active(threat_type, src_ip):
            return

        # Update cooldown timestamp
        self._alert_cooldowns[(threat_type, src_ip)] = time.time()

        # Dispatch alert
        if self._alert_callback:
            self._alert_callback(alert_data)
        else:
            logger.warning("Alert triggered but no callback registered: %s", alert_data)

    def _cleanup_old_entries(self, current_time: float) -> None:
        """
        Remove expired entries from tracking data structures
        to prevent memory leaks during long-running sessions.
        """
        # Clean up port access log
        for ip in list(self._port_access_log.keys()):
            self._port_access_log[ip] = [
                (ts, port) for ts, port in self._port_access_log[ip]
                if current_time - ts <= self.port_scan_window
            ]
            # Remove empty entries
            if not self._port_access_log[ip]:
                del self._port_access_log[ip]

        # Clean up packet timestamps
        cutoff = current_time - self.spike_window
        self._packet_timestamps = [
            ts for ts in self._packet_timestamps if ts > cutoff
        ]

        # Clean up old cooldowns (keep for 2x cooldown period)
        expired_keys = [
            key for key, ts in self._alert_cooldowns.items()
            if current_time - ts > self.alert_cooldown * 2
        ]
        for key in expired_keys:
            del self._alert_cooldowns[key]

    def analyze(self, packet_data: dict) -> None:
        """
        Analyze a parsed packet against all detection rules.

        This is the main entry point — register this method as a
        handler with the PacketSniffer.

        Args:
            packet_data: Dictionary from PacketSniffer containing
                         src_ip, dst_ip, protocol, src_port, dst_port, etc.
        """
        current_time = packet_data.get("timestamp", time.time())

        # Periodic cleanup (every ~1000 packets or based on time)
        self._packet_timestamps.append(current_time)
        if len(self._packet_timestamps) % 500 == 0:
            self._cleanup_old_entries(current_time)

        # Run all detection rules
        self._check_port_scan(packet_data, current_time)
        self._check_traffic_spike(current_time)

    def _check_port_scan(self, packet_data: dict, current_time: float) -> None:
        """
        Detect port scanning behavior.

        A port scan is identified when a single source IP accesses
        more unique destination ports than the threshold within
        the configured time window.

        Args:
            packet_data: Parsed packet information dictionary.
            current_time: Current timestamp for window calculations.
        """
        src_ip = packet_data.get("src_ip")
        dst_port = packet_data.get("dst_port")

        # Only check if we have both source IP and destination port
        if not src_ip or dst_port is None:
            return

        # Record this port access
        self._port_access_log[src_ip].append((current_time, dst_port))

        # Filter to entries within the time window
        window_start = current_time - self.port_scan_window
        recent_entries = [
            (ts, port) for ts, port in self._port_access_log[src_ip]
            if ts >= window_start
        ]
        self._port_access_log[src_ip] = recent_entries

        # Count unique ports accessed in the window
        unique_ports = set(port for _, port in recent_entries)

        if len(unique_ports) >= self.port_scan_threshold:
            self._trigger_alert({
                "threat_type": "PORT_SCAN",
                "severity": "HIGH",
                "src_ip": src_ip,
                "details": (
                    f"Port scan detected from {src_ip}: "
                    f"{len(unique_ports)} unique ports accessed in "
                    f"{self.port_scan_window}s (threshold: {self.port_scan_threshold})"
                ),
                "timestamp": current_time,
                "metadata": {
                    "unique_ports": len(unique_ports),
                    "ports_sample": sorted(list(unique_ports))[:10],  # First 10 ports
                },
            })

    def _check_traffic_spike(self, current_time: float) -> None:
        """
        Detect abnormal traffic spikes.

        Calculates the current packets-per-second rate and triggers
        an alert if it exceeds the configured threshold.

        Args:
            current_time: Current timestamp for rate calculation.
        """
        # Filter timestamps to the spike detection window
        window_start = current_time - self.spike_window
        recent_packets = [
            ts for ts in self._packet_timestamps if ts >= window_start
        ]

        # Calculate packets per second
        if self.spike_window > 0:
            packets_per_second = len(recent_packets) / self.spike_window
        else:
            return

        if packets_per_second >= self.spike_threshold:
            self._trigger_alert({
                "threat_type": "TRAFFIC_SPIKE",
                "severity": "MEDIUM",
                "src_ip": "NETWORK",
                "details": (
                    f"Traffic spike detected: {packets_per_second:.1f} packets/sec "
                    f"(threshold: {self.spike_threshold} pps)"
                ),
                "timestamp": current_time,
                "metadata": {
                    "packets_per_second": round(packets_per_second, 1),
                    "window_seconds": self.spike_window,
                },
            })
