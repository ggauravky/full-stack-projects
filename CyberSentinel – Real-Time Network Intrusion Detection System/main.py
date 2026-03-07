"""
╔═══════════════════════════════════════════════════════════════════════╗
║                       CyberSentinel v1.0                             ║
║           Real-Time Network Intrusion Detection System               ║
╚═══════════════════════════════════════════════════════════════════════╝

Main entry point that initializes and orchestrates all modules:
1. Loads configuration from config.yaml
2. Sets up the logging system
3. Initializes the packet sniffer
4. Connects detection engines (RuleEngine + AnomalyDetector)
5. Wires up the alert system (AlertManager + Notifier)
6. Starts the Flask dashboard in a background thread
7. Begins real-time packet capture

Usage:
    Run with administrator/root privileges:

    Windows (Admin PowerShell):
        python main.py

    Linux/Mac:
        sudo python main.py

Press Ctrl+C to stop.
"""

import sys
import signal
import threading

from app.utils.config_loader import get_config
from app.utils.logger import setup_logging, get_logger
from app.sniffer.packet_sniffer import PacketSniffer
from app.detection.rule_engine import RuleEngine
from app.detection.anomaly_detector import AnomalyDetector
from app.alerts.alert_manager import AlertManager
from app.alerts.notifier import Notifier


# Banner displayed at startup
BANNER = r"""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║      ██████╗██╗   ██╗██████╗ ███████╗██████╗                          ║
║     ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗                         ║
║     ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝                         ║
║     ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗                         ║
║     ╚██████╗   ██║   ██████╔╝███████╗██║  ██║                         ║
║      ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝                         ║
║                                                                       ║
║     ███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗       ║
║     ██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║       ║
║     ███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║       ║
║     ╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║       ║
║     ███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗  ║
║     ╚══════╝╚══════╝╚═╝  ╚═══╝  ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝   ║
║                                                                       ║
║     Real-Time Network Intrusion Detection System  v1.0                ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
"""


def main():
    """
    Main function — initializes all modules and starts CyberSentinel.
    """
    # Display the startup banner
    print(BANNER)

    # ──────────────────────────────────────────────────────────────
    # Step 1: Load Configuration
    # ──────────────────────────────────────────────────────────────
    try:
        config = get_config()
    except FileNotFoundError as e:
        print(f"❌ Configuration Error: {e}")
        sys.exit(1)

    # ──────────────────────────────────────────────────────────────
    # Step 2: Setup Logging
    # ──────────────────────────────────────────────────────────────
    log_config = config.get("logging", {})
    setup_logging(
        log_level=log_config.get("level", "INFO"),
        log_file=log_config.get("log_file", "data/cybersentinel.log"),
        max_file_size=log_config.get("max_file_size", 5_242_880),
        backup_count=log_config.get("backup_count", 3),
    )
    logger = get_logger("main")
    logger.info("CyberSentinel starting up...")

    # ──────────────────────────────────────────────────────────────
    # Step 3: Initialize the Alert System
    # ──────────────────────────────────────────────────────────────
    alert_config = config.get("alerts", {})

    # Create the Notifier (terminal + log file output)
    notifier = Notifier(
        log_file=alert_config.get("log_file", "data/alerts.log"),
    )

    # Create the AlertManager and connect the notifier
    alert_manager = AlertManager(
        max_alerts=alert_config.get("max_in_memory", 500),
    )
    alert_manager.set_notifier(notifier)

    logger.info("✅ Alert system initialized")

    # ──────────────────────────────────────────────────────────────
    # Step 4: Initialize Detection Engines
    # ──────────────────────────────────────────────────────────────
    detection_config = config.get("detection", {})
    cooldown = alert_config.get("cooldown", 30)

    # Rule Engine (port scan + traffic spike detection)
    port_scan_config = detection_config.get("port_scan", {})
    spike_config = detection_config.get("traffic_spike", {})

    rule_engine = RuleEngine(
        port_scan_threshold=port_scan_config.get("threshold", 15),
        port_scan_window=port_scan_config.get("time_window", 60),
        spike_threshold=spike_config.get("threshold", 100),
        spike_window=spike_config.get("time_window", 10),
        alert_cooldown=cooldown,
    )
    rule_engine.set_alert_callback(alert_manager.process_alert)

    # Anomaly Detector (statistical + unknown IP detection)
    anomaly_config = detection_config.get("anomaly", {})
    unknown_ip_config = detection_config.get("unknown_ip", {})

    anomaly_detector = AnomalyDetector(
        std_dev_multiplier=anomaly_config.get("std_dev_multiplier", 2.5),
        min_samples=anomaly_config.get("min_samples", 30),
        trusted_ips=unknown_ip_config.get("trusted_ips", []),
        unknown_ip_enabled=unknown_ip_config.get("enabled", True),
        alert_cooldown=cooldown,
    )
    anomaly_detector.set_alert_callback(alert_manager.process_alert)

    logger.info("✅ Detection engines initialized (RuleEngine + AnomalyDetector)")

    # ──────────────────────────────────────────────────────────────
    # Step 5: Initialize the Packet Sniffer
    # ──────────────────────────────────────────────────────────────
    sniffer_config = config.get("sniffer", {})

    sniffer = PacketSniffer(
        interface=sniffer_config.get("interface"),
        bpf_filter=sniffer_config.get("filter"),
        max_packets=sniffer_config.get("max_packets", 0),
    )

    # Register detection engines as packet handlers
    sniffer.register_handler(rule_engine.analyze)
    sniffer.register_handler(anomaly_detector.analyze)

    logger.info("✅ Packet sniffer initialized and handlers connected")

    # ──────────────────────────────────────────────────────────────
    # Step 6: Start the Flask Dashboard (background thread)
    # ──────────────────────────────────────────────────────────────
    dashboard_config = config.get("dashboard", {})

    if dashboard_config.get("enabled", True):
        try:
            from app.dashboard.server import create_dashboard_app

            dashboard_app = create_dashboard_app(alert_manager, sniffer)
            dashboard_host = dashboard_config.get("host", "0.0.0.0")
            dashboard_port = dashboard_config.get("port", 5000)

            # Run Flask in a daemon thread so it stops when main exits
            dashboard_thread = threading.Thread(
                target=lambda: dashboard_app.run(
                    host=dashboard_host,
                    port=dashboard_port,
                    debug=False,
                    use_reloader=False,
                ),
                daemon=True,
                name="DashboardThread",
            )
            dashboard_thread.start()

            logger.info(
                "✅ Dashboard started at http://%s:%d",
                dashboard_host,
                dashboard_port,
            )
            print(
                f"\n  🌐 Dashboard: http://localhost:{dashboard_port}\n"
            )

        except ImportError as e:
            logger.warning("Flask not installed — dashboard disabled: %s", e)
        except Exception as e:
            logger.error("Failed to start dashboard: %s", e)

    # ──────────────────────────────────────────────────────────────
    # Step 7: Setup Graceful Shutdown
    # ──────────────────────────────────────────────────────────────
    def shutdown_handler(signum, frame):
        """Handle Ctrl+C / SIGINT for graceful shutdown."""
        print("\n\n  🛑 Shutting down CyberSentinel...\n")
        sniffer.stop()

        # Print summary statistics
        stats = alert_manager.get_stats()
        print("  ╔══════════════════════════════════════╗")
        print("  ║         SESSION SUMMARY              ║")
        print("  ╠══════════════════════════════════════╣")
        print(f"  ║  Packets captured:  {sniffer.packet_count:<16} ║")
        print(f"  ║  Total alerts:      {stats['total_alerts']:<16} ║")
        print(f"  ║  Alerts in memory:  {stats['alerts_in_memory']:<16} ║")
        print("  ╚══════════════════════════════════════╝")

        if stats["by_type"]:
            print("\n  Alerts by type:")
            for threat_type, count in stats["by_type"].items():
                print(f"    • {threat_type}: {count}")

        print("\n  Goodbye! Stay secure. 🔒\n")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)

    # ──────────────────────────────────────────────────────────────
    # Step 8: Start Packet Capture (blocking)
    # ──────────────────────────────────────────────────────────────
    print("  🔍 Starting packet capture... (Press Ctrl+C to stop)\n")

    try:
        sniffer.start()
    except PermissionError:
        print("\n  ❌ ERROR: Administrator/root privileges required!")
        print("  Please run CyberSentinel with elevated permissions.")
        print("    Windows: Run PowerShell as Administrator")
        print("    Linux/Mac: sudo python main.py\n")
        sys.exit(1)
    except Exception as e:
        logger.critical("Fatal error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
