"""
CyberSentinel - Notifier Module
=================================
Handles alert output to multiple channels:
1. Terminal output (colored, formatted alerts)
2. Log file output (structured alerts saved to alerts.log)
"""

import os
import time

from colorama import Fore, Style

from app.utils.logger import get_logger


logger = get_logger("notifier")

# Severity-to-color mapping for terminal output
SEVERITY_COLORS = {
    "LOW": Fore.CYAN,
    "MEDIUM": Fore.YELLOW,
    "HIGH": Fore.RED,
    "CRITICAL": Fore.RED + Style.BRIGHT,
}

# Severity-to-emoji mapping for visual impact
SEVERITY_ICONS = {
    "LOW": "ℹ️ ",
    "MEDIUM": "⚠️ ",
    "HIGH": "🔴",
    "CRITICAL": "🚨",
}


class Notifier:
    """
    Alert notification dispatcher.

    Outputs formatted alerts to the terminal with color coding
    and appends structured alert entries to a persistent log file.

    Attributes:
        log_file: Path to the alerts log file.
    """

    def __init__(self, log_file: str = "data/alerts.log"):
        """
        Initialize the Notifier.

        Args:
            log_file: Path to the alerts log file (relative to project root).
        """
        # Resolve log file path relative to project root
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.log_file = os.path.join(project_root, log_file)

        # Ensure the log directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        logger.info("Notifier initialized | log_file=%s", self.log_file)

    def send_alert(self, alert: dict) -> None:
        """
        Send an alert to all output channels.

        Args:
            alert: Structured alert dictionary from AlertManager containing:
                   id, timestamp, threat_type, severity, src_ip, details.
        """
        # Output to terminal with color formatting
        self._print_terminal_alert(alert)

        # Append to the alerts log file
        self._write_log_alert(alert)

    def _print_terminal_alert(self, alert: dict) -> None:
        """
        Print a formatted, colored alert to the terminal.

        Args:
            alert: Alert dictionary to display.
        """
        severity = alert.get("severity", "LOW")
        color = SEVERITY_COLORS.get(severity, Fore.WHITE)
        icon = SEVERITY_ICONS.get(severity, "•")

        # Format the timestamp
        timestamp = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(alert.get("timestamp", time.time()))
        )

        # Build the formatted alert box
        separator = f"{color}{'─' * 70}{Style.RESET_ALL}"

        print(f"\n{separator}")
        print(
            f"  {icon} {color}{Style.BRIGHT}"
            f"SECURITY ALERT #{alert.get('id', '?')}{Style.RESET_ALL}"
        )
        print(separator)
        print(f"  {'Time:':<12} {timestamp}")
        print(f"  {'Type:':<12} {color}{alert.get('threat_type', 'UNKNOWN')}{Style.RESET_ALL}")
        print(f"  {'Severity:':<12} {color}{severity}{Style.RESET_ALL}")
        print(f"  {'Source IP:':<12} {alert.get('src_ip', 'unknown')}")
        print(f"  {'Details:':<12} {alert.get('details', 'No details')}")
        print(separator)

    def _write_log_alert(self, alert: dict) -> None:
        """
        Append a structured alert entry to the alerts log file.

        Each alert is written as a single, parseable log line with
        all relevant fields separated by pipes.

        Args:
            alert: Alert dictionary to log.
        """
        try:
            timestamp = time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.localtime(alert.get("timestamp", time.time()))
            )

            log_entry = (
                f"[{timestamp}] "
                f"ALERT #{alert.get('id', '?')} | "
                f"Type: {alert.get('threat_type', 'UNKNOWN')} | "
                f"Severity: {alert.get('severity', 'LOW')} | "
                f"Source: {alert.get('src_ip', 'unknown')} | "
                f"Details: {alert.get('details', 'No details')}\n"
            )

            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)

        except Exception as e:
            logger.error("Failed to write alert to log file: %s", e)
