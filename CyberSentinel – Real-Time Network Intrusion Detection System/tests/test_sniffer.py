"""
CyberSentinel - Unit Tests
============================
Tests for core modules:
1. Packet data extraction (mock scapy packets)
2. Rule Engine detection logic
3. Anomaly Detector logic
4. Alert Manager alert creation and storage
5. Config Loader functionality
"""

import os
import time
import tempfile
import pytest

# ─── Test: Config Loader ─────────────────────────────────────────

from app.utils.config_loader import load_config, get_config, reset_config_cache


class TestConfigLoader:
    """Tests for the configuration loader module."""

    def setup_method(self):
        """Reset config cache before each test."""
        reset_config_cache()

    def test_load_valid_config(self, tmp_path):
        """Test loading a valid YAML config file."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(
            "detection:\n  port_scan:\n    threshold: 10\n"
            "dashboard:\n  port: 8080\n"
        )
        config = load_config(str(config_file))
        assert isinstance(config, dict)
        assert config["detection"]["port_scan"]["threshold"] == 10
        assert config["dashboard"]["port"] == 8080

    def test_load_missing_config(self):
        """Test that loading a missing config raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/path/config.yaml")

    def test_get_config_section(self, tmp_path):
        """Test retrieving a specific config section."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(
            "sniffer:\n  interface: eth0\n"
            "detection:\n  port_scan:\n    threshold: 20\n"
        )
        section = get_config("detection", str(config_file))
        assert section["port_scan"]["threshold"] == 20

    def test_get_config_invalid_section(self, tmp_path):
        """Test that requesting an invalid section raises KeyError."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("sniffer:\n  interface: eth0\n")
        with pytest.raises(KeyError):
            get_config("nonexistent", str(config_file))


# ─── Test: Rule Engine ───────────────────────────────────────────

from app.detection.rule_engine import RuleEngine


class TestRuleEngine:
    """Tests for the signature-based rule engine."""

    def setup_method(self):
        """Initialize a RuleEngine with low thresholds for testing."""
        self.alerts = []
        self.engine = RuleEngine(
            port_scan_threshold=5,      # Alert after 5 unique ports
            port_scan_window=60,
            spike_threshold=10,          # Alert at 10 packets/second
            spike_window=2,
            alert_cooldown=1,            # Short cooldown for testing
        )
        self.engine.set_alert_callback(lambda alert: self.alerts.append(alert))

    def test_port_scan_detection(self):
        """Test that accessing many unique ports triggers a port scan alert."""
        base_time = time.time()

        # Simulate one IP accessing 6 unique ports (threshold is 5)
        for port in range(6):
            packet = {
                "timestamp": base_time + port * 0.1,
                "src_ip": "10.0.0.50",
                "dst_ip": "192.168.1.1",
                "protocol": "TCP",
                "src_port": 54321,
                "dst_port": 1000 + port,
                "size": 64,
            }
            self.engine.analyze(packet)

        # Verify a PORT_SCAN alert was triggered
        port_scan_alerts = [
            a for a in self.alerts if a["threat_type"] == "PORT_SCAN"
        ]
        assert len(port_scan_alerts) >= 1
        assert port_scan_alerts[0]["src_ip"] == "10.0.0.50"
        assert port_scan_alerts[0]["severity"] == "HIGH"

    def test_no_port_scan_below_threshold(self):
        """Test that accessing fewer ports than threshold does NOT alert."""
        base_time = time.time()

        # Access only 3 unique ports (threshold is 5)
        for port in range(3):
            packet = {
                "timestamp": base_time + port * 0.1,
                "src_ip": "10.0.0.99",
                "dst_ip": "192.168.1.1",
                "protocol": "TCP",
                "src_port": 54321,
                "dst_port": 2000 + port,
                "size": 64,
            }
            self.engine.analyze(packet)

        port_scan_alerts = [
            a for a in self.alerts if a["threat_type"] == "PORT_SCAN"
        ]
        assert len(port_scan_alerts) == 0

    def test_traffic_spike_detection(self):
        """Test that high packet rates trigger a traffic spike alert."""
        base_time = time.time()

        # Send 25 packets in 2 seconds (12.5 pps, threshold is 10)
        for i in range(25):
            packet = {
                "timestamp": base_time + i * 0.08,  # ~12.5 pps over 2s
                "src_ip": f"10.0.0.{i % 255}",
                "dst_ip": "192.168.1.1",
                "protocol": "TCP",
                "src_port": 54321,
                "dst_port": 80,
                "size": 64,
            }
            self.engine.analyze(packet)

        spike_alerts = [
            a for a in self.alerts if a["threat_type"] == "TRAFFIC_SPIKE"
        ]
        assert len(spike_alerts) >= 1

    def test_alert_cooldown(self):
        """Test that duplicate alerts are suppressed during cooldown."""
        base_time = time.time()

        # Trigger two port scans from the same IP quickly
        for port in range(12):
            packet = {
                "timestamp": base_time + port * 0.05,
                "src_ip": "10.0.0.77",
                "dst_ip": "192.168.1.1",
                "protocol": "TCP",
                "src_port": 54321,
                "dst_port": 3000 + port,
                "size": 64,
            }
            self.engine.analyze(packet)

        # Should only get 1 port scan alert due to cooldown
        port_scan_alerts = [
            a for a in self.alerts if a["threat_type"] == "PORT_SCAN"
            and a["src_ip"] == "10.0.0.77"
        ]
        assert len(port_scan_alerts) == 1


# ─── Test: Anomaly Detector ──────────────────────────────────────

from app.detection.anomaly_detector import AnomalyDetector


class TestAnomalyDetector:
    """Tests for the statistical anomaly detector."""

    def setup_method(self):
        """Initialize an AnomalyDetector for testing."""
        self.alerts = []
        self.detector = AnomalyDetector(
            std_dev_multiplier=2.0,
            min_samples=5,
            trusted_ips=["192.168.1.0/24", "10.0.0.0/8", "127.0.0.1"],
            unknown_ip_enabled=True,
            alert_cooldown=1,
        )
        self.detector.set_alert_callback(lambda alert: self.alerts.append(alert))

    def test_unknown_ip_detection(self):
        """Test that connections from untrusted IPs trigger alerts."""
        packet = {
            "timestamp": time.time(),
            "src_ip": "203.0.113.50",  # External IP, not in trusted list
            "dst_ip": "192.168.1.100",
            "protocol": "TCP",
            "src_port": 54321,
            "dst_port": 80,
            "size": 64,
        }
        self.detector.analyze(packet)

        unknown_alerts = [
            a for a in self.alerts if a["threat_type"] == "UNKNOWN_IP"
        ]
        assert len(unknown_alerts) == 1
        assert unknown_alerts[0]["src_ip"] == "203.0.113.50"

    def test_trusted_ip_no_alert(self):
        """Test that trusted IPs do NOT trigger unknown IP alerts."""
        packet = {
            "timestamp": time.time(),
            "src_ip": "192.168.1.50",  # In the trusted 192.168.1.0/24 range
            "dst_ip": "192.168.1.1",
            "protocol": "TCP",
            "src_port": 54321,
            "dst_port": 443,
            "size": 64,
        }
        self.detector.analyze(packet)

        unknown_alerts = [
            a for a in self.alerts if a["threat_type"] == "UNKNOWN_IP"
        ]
        assert len(unknown_alerts) == 0

    def test_duplicate_ip_not_alerted(self):
        """Test that the same unknown IP only triggers one alert."""
        for _ in range(5):
            packet = {
                "timestamp": time.time(),
                "src_ip": "8.8.8.8",
                "dst_ip": "192.168.1.100",
                "protocol": "UDP",
                "src_port": 53,
                "dst_port": 12345,
                "size": 64,
            }
            self.detector.analyze(packet)

        unknown_alerts = [
            a for a in self.alerts if a["threat_type"] == "UNKNOWN_IP"
            and a["src_ip"] == "8.8.8.8"
        ]
        # Only 1 alert despite 5 packets from the same IP
        assert len(unknown_alerts) == 1


# ─── Test: Alert Manager ─────────────────────────────────────────

from app.alerts.alert_manager import AlertManager


class TestAlertManager:
    """Tests for the alert manager module."""

    def setup_method(self):
        """Initialize an AlertManager for testing."""
        self.manager = AlertManager(max_alerts=10)

    def test_process_alert_creates_structured_alert(self):
        """Test that process_alert creates a properly structured alert."""
        threat_data = {
            "threat_type": "PORT_SCAN",
            "severity": "HIGH",
            "src_ip": "10.0.0.50",
            "details": "Test port scan alert",
            "timestamp": time.time(),
        }
        alert = self.manager.process_alert(threat_data)

        assert alert["id"] == 1
        assert alert["threat_type"] == "PORT_SCAN"
        assert alert["severity"] == "HIGH"
        assert alert["src_ip"] == "10.0.0.50"
        assert "details" in alert

    def test_get_recent_alerts(self):
        """Test retrieving recent alerts in reverse chronological order."""
        for i in range(5):
            self.manager.process_alert({
                "threat_type": f"TYPE_{i}",
                "severity": "LOW",
                "src_ip": f"10.0.0.{i}",
                "details": f"Alert {i}",
                "timestamp": time.time() + i,
            })

        recent = self.manager.get_recent_alerts(count=3)
        assert len(recent) == 3
        # Most recent first
        assert recent[0]["threat_type"] == "TYPE_4"

    def test_max_alerts_eviction(self):
        """Test that old alerts are evicted when max is reached."""
        for i in range(15):
            self.manager.process_alert({
                "threat_type": "FLOOD",
                "severity": "LOW",
                "src_ip": "10.0.0.1",
                "details": f"Alert {i}",
                "timestamp": time.time(),
            })

        assert self.manager.total_alerts == 15
        assert len(self.manager.alerts) == 10  # max_alerts=10

    def test_suspicious_ips(self):
        """Test the suspicious IP aggregation."""
        for i in range(3):
            self.manager.process_alert({
                "threat_type": "PORT_SCAN",
                "severity": "HIGH",
                "src_ip": "10.0.0.50",
                "details": "Port scan",
                "timestamp": time.time(),
            })
        self.manager.process_alert({
            "threat_type": "UNKNOWN_IP",
            "severity": "LOW",
            "src_ip": "203.0.113.1",
            "details": "Unknown IP",
            "timestamp": time.time(),
        })

        suspicious = self.manager.get_suspicious_ips()
        assert len(suspicious) == 2
        # IP with most alerts should be first
        assert suspicious[0]["ip"] == "10.0.0.50"
        assert suspicious[0]["alert_count"] == 3

    def test_stats(self):
        """Test statistics reporting."""
        self.manager.process_alert({
            "threat_type": "PORT_SCAN",
            "severity": "HIGH",
            "src_ip": "10.0.0.1",
            "details": "Scan",
            "timestamp": time.time(),
        })
        self.manager.process_alert({
            "threat_type": "TRAFFIC_SPIKE",
            "severity": "MEDIUM",
            "src_ip": "NETWORK",
            "details": "Spike",
            "timestamp": time.time(),
        })

        stats = self.manager.get_stats()
        assert stats["total_alerts"] == 2
        assert stats["by_type"]["PORT_SCAN"] == 1
        assert stats["by_type"]["TRAFFIC_SPIKE"] == 1
        assert stats["by_severity"]["HIGH"] == 1
        assert stats["by_severity"]["MEDIUM"] == 1


# ─── Test: Notifier ──────────────────────────────────────────────

from app.alerts.notifier import Notifier


class TestNotifier:
    """Tests for the notifier module."""

    def test_write_alert_to_log_file(self, tmp_path):
        """Test that alerts are written to the log file."""
        log_file = tmp_path / "test_alerts.log"
        notifier = Notifier(log_file=str(log_file))

        alert = {
            "id": 1,
            "timestamp": time.time(),
            "threat_type": "PORT_SCAN",
            "severity": "HIGH",
            "src_ip": "10.0.0.50",
            "details": "Port scan detected",
        }
        notifier._write_log_alert(alert)

        # Verify the log file was created and contains the alert
        assert log_file.exists()
        content = log_file.read_text()
        assert "PORT_SCAN" in content
        assert "10.0.0.50" in content
        assert "ALERT #1" in content
