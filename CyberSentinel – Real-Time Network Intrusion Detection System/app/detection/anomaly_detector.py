"""
CyberSentinel - Anomaly Detector Module
=========================================
Implements statistical anomaly detection for network traffic:

1. Traffic Rate Anomaly Detection:
   Tracks historical packet rates and flags significant deviations
   using standard deviation analysis.

2. Unknown IP Detection:
   Maintains a list of trusted IPs and flags connections
   from previously unseen/untrusted source addresses.
"""

import time
import ipaddress
from collections import deque

from app.utils.logger import get_logger


logger = get_logger("anomaly_detector")


class AnomalyDetector:
    """
    Statistical anomaly detection engine for network traffic.

    Uses rolling statistics (mean + standard deviation) to detect
    unusual traffic patterns and maintains a trusted IP list to
    identify unknown sources.

    Attributes:
        std_dev_multiplier: How many standard deviations from the mean
                            constitutes an anomaly.
        min_samples: Minimum history samples before enabling detection.
        trusted_ips: Set of trusted IP addresses/networks.
    """

    def __init__(
        self,
        std_dev_multiplier: float = 2.5,
        min_samples: int = 30,
        trusted_ips: list[str] | None = None,
        unknown_ip_enabled: bool = True,
        alert_cooldown: int = 30,
    ):
        """
        Initialize the Anomaly Detector.

        Args:
            std_dev_multiplier: Number of standard deviations above mean
                                to trigger an anomaly alert.
            min_samples: Minimum number of rate samples before detection activates.
            trusted_ips: List of trusted IP addresses or CIDR ranges.
            unknown_ip_enabled: Whether to flag unknown source IPs.
            alert_cooldown: Seconds before re-alerting the same anomaly type.
        """
        self.std_dev_multiplier = std_dev_multiplier
        self.min_samples = min_samples
        self.unknown_ip_enabled = unknown_ip_enabled
        self.alert_cooldown = alert_cooldown

        # Parse trusted IPs into a set of ip_address/ip_network objects
        self._trusted_networks: list[ipaddress.IPv4Network | ipaddress.IPv4Address] = []
        self._parse_trusted_ips(trusted_ips or [])

        # ---- Traffic Rate Anomaly State ----
        # Rolling window of packet rates (packets per interval)
        self._rate_history: deque[float] = deque(maxlen=200)
        # Counter for packets in the current interval
        self._current_interval_count: int = 0
        # Timestamp marking the start of the current interval
        self._interval_start: float = time.time()
        # Interval length in seconds for rate sampling
        self._rate_interval: float = 5.0

        # ---- Unknown IP Tracking ----
        # Set of all IPs seen so far
        self._seen_ips: set[str] = set()
        # Cooldown tracking: {(threat_type, ip): last_alert_time}
        self._alert_cooldowns: dict[tuple[str, str], float] = {}

        # Alert callback
        self._alert_callback = None

        logger.info(
            "AnomalyDetector initialized | std_dev=%.1f | min_samples=%d | "
            "trusted_networks=%d | unknown_ip=%s",
            std_dev_multiplier,
            min_samples,
            len(self._trusted_networks),
            unknown_ip_enabled,
        )

    def _parse_trusted_ips(self, ip_list: list[str]) -> None:
        """
        Parse a list of IP strings into ipaddress objects.
        Supports both individual IPs and CIDR notation.
        """
        for ip_str in ip_list:
            try:
                if "/" in ip_str:
                    # CIDR notation (e.g., "192.168.1.0/24")
                    network = ipaddress.ip_network(ip_str, strict=False)
                    self._trusted_networks.append(network)
                else:
                    # Individual IP address
                    addr = ipaddress.ip_address(ip_str)
                    self._trusted_networks.append(addr)
            except ValueError as e:
                logger.warning("Invalid trusted IP '%s': %s", ip_str, e)

    def _is_trusted_ip(self, ip_str: str) -> bool:
        """
        Check if an IP address is in the trusted list.

        Args:
            ip_str: IP address string to check.

        Returns:
            True if the IP is trusted, False otherwise.
        """
        try:
            addr = ipaddress.ip_address(ip_str)
        except ValueError:
            return False

        for trusted in self._trusted_networks:
            if isinstance(trusted, (ipaddress.IPv4Network, ipaddress.IPv6Network)):
                if addr in trusted:
                    return True
            else:
                if addr == trusted:
                    return True
        return False

    def set_alert_callback(self, callback) -> None:
        """Register a callback function to receive anomaly alerts."""
        self._alert_callback = callback

    def _is_cooldown_active(self, threat_type: str, identifier: str) -> bool:
        """Check if alert cooldown is active for a threat+identifier combo."""
        key = (threat_type, identifier)
        last_alert = self._alert_cooldowns.get(key, 0)
        return (time.time() - last_alert) < self.alert_cooldown

    def _trigger_alert(self, alert_data: dict) -> None:
        """Trigger an alert if cooldown allows it."""
        threat_type = alert_data["threat_type"]
        identifier = alert_data.get("src_ip", "unknown")

        if self._is_cooldown_active(threat_type, identifier):
            return

        self._alert_cooldowns[(threat_type, identifier)] = time.time()

        if self._alert_callback:
            self._alert_callback(alert_data)
        else:
            logger.warning("Anomaly alert triggered but no callback: %s", alert_data)

    def analyze(self, packet_data: dict) -> None:
        """
        Analyze a parsed packet for anomalies.

        This is the main entry point — register this method as a
        handler with the PacketSniffer.

        Args:
            packet_data: Dictionary from PacketSniffer containing
                         src_ip, dst_ip, protocol, etc.
        """
        current_time = packet_data.get("timestamp", time.time())

        # Check for unknown source IPs
        if self.unknown_ip_enabled:
            self._check_unknown_ip(packet_data, current_time)

        # Update traffic rate statistics
        self._update_rate_stats(current_time)

    def _update_rate_stats(self, current_time: float) -> None:
        """
        Track packet rates over time and detect statistical anomalies.

        Counts packets within fixed intervals, then compares each
        interval's rate against the rolling mean ± (std_dev * multiplier).

        Args:
            current_time: Current timestamp.
        """
        self._current_interval_count += 1

        # Check if the current interval has elapsed
        elapsed = current_time - self._interval_start
        if elapsed >= self._rate_interval:
            # Calculate the rate for this interval
            rate = self._current_interval_count / elapsed
            self._rate_history.append(rate)

            # Reset for the next interval
            self._current_interval_count = 0
            self._interval_start = current_time

            # Only check for anomalies if we have enough history
            if len(self._rate_history) >= self.min_samples:
                self._check_rate_anomaly(rate, current_time)

    def _check_rate_anomaly(self, current_rate: float, current_time: float) -> None:
        """
        Detect if the current traffic rate is anomalous.

        Uses the mean and standard deviation of historical rates
        to determine if the current rate is significantly above normal.

        Args:
            current_rate: Current packets-per-second rate.
            current_time: Current timestamp.
        """
        # Calculate rolling statistics
        rates = list(self._rate_history)
        n = len(rates)
        mean_rate = sum(rates) / n
        variance = sum((r - mean_rate) ** 2 for r in rates) / n
        std_dev = variance ** 0.5

        # Calculate the anomaly threshold
        threshold = mean_rate + (std_dev * self.std_dev_multiplier)

        if current_rate > threshold and std_dev > 0:
            deviation = (current_rate - mean_rate) / std_dev if std_dev > 0 else 0

            self._trigger_alert({
                "threat_type": "RATE_ANOMALY",
                "severity": "HIGH" if deviation > 4 else "MEDIUM",
                "src_ip": "NETWORK",
                "details": (
                    f"Traffic rate anomaly detected: {current_rate:.1f} pps "
                    f"(mean: {mean_rate:.1f}, threshold: {threshold:.1f}, "
                    f"deviation: {deviation:.1f}σ)"
                ),
                "timestamp": current_time,
                "metadata": {
                    "current_rate": round(current_rate, 1),
                    "mean_rate": round(mean_rate, 1),
                    "std_dev": round(std_dev, 1),
                    "deviation_sigma": round(deviation, 1),
                },
            })

    def _check_unknown_ip(self, packet_data: dict, current_time: float) -> None:
        """
        Detect connections from unknown/untrusted source IPs.

        Flags source IPs that are not in the trusted IP list and
        have not been seen before.

        Args:
            packet_data: Parsed packet information dictionary.
            current_time: Current timestamp.
        """
        src_ip = packet_data.get("src_ip")
        if not src_ip:
            return

        # Skip if IP has already been seen
        if src_ip in self._seen_ips:
            return

        # Add to seen IPs set
        self._seen_ips.add(src_ip)

        # Check if the IP is in the trusted list
        if not self._is_trusted_ip(src_ip):
            self._trigger_alert({
                "threat_type": "UNKNOWN_IP",
                "severity": "LOW",
                "src_ip": src_ip,
                "details": (
                    f"Connection from unknown/untrusted IP: {src_ip} "
                    f"(protocol: {packet_data.get('protocol', 'unknown')})"
                ),
                "timestamp": current_time,
                "metadata": {
                    "protocol": packet_data.get("protocol"),
                    "dst_ip": packet_data.get("dst_ip"),
                    "dst_port": packet_data.get("dst_port"),
                },
            })
