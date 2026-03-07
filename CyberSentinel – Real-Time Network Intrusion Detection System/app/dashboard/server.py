"""
CyberSentinel - Dashboard Server Module
=========================================
Flask-based web dashboard that provides a real-time view of:
- Live packet capture count
- Recent security alerts
- Suspicious IP addresses
- Alert statistics

The dashboard auto-refreshes via JavaScript polling.
"""

import time

from flask import Flask, render_template, jsonify

from app.utils.logger import get_logger


logger = get_logger("dashboard")


def create_dashboard_app(alert_manager, sniffer) -> Flask:
    """
    Create and configure the Flask dashboard application.

    Uses a factory pattern so the app can access the AlertManager
    and PacketSniffer instances for real-time data.

    Args:
        alert_manager: AlertManager instance for alert data.
        sniffer: PacketSniffer instance for packet count.

    Returns:
        Configured Flask application.
    """
    app = Flask(
        __name__,
        template_folder="templates",
    )

    # Suppress Flask's default request logging in production
    import logging as _logging
    _logging.getLogger("werkzeug").setLevel(_logging.WARNING)

    @app.route("/")
    def dashboard():
        """Render the main dashboard page."""
        return render_template("dashboard.html")

    @app.route("/api/stats")
    def api_stats():
        """
        API endpoint returning real-time statistics as JSON.

        Response format:
        {
            "packet_count": int,
            "sniffer_running": bool,
            "alerts": {
                "total": int,
                "in_memory": int,
                "by_type": {"PORT_SCAN": 3, ...},
                "by_severity": {"HIGH": 2, ...},
            },
            "recent_alerts": [{alert}, ...],
            "suspicious_ips": [{ip_info}, ...],
            "uptime": str,
        }
        """
        stats = alert_manager.get_stats()
        recent = alert_manager.get_recent_alerts(count=25)
        suspicious = alert_manager.get_suspicious_ips()

        # Format timestamps for display
        for alert in recent:
            alert["time_str"] = time.strftime(
                "%H:%M:%S",
                time.localtime(alert.get("timestamp", 0))
            )

        return jsonify({
            "packet_count": sniffer.packet_count,
            "sniffer_running": sniffer.is_running,
            "alerts": {
                "total": stats["total_alerts"],
                "in_memory": stats["alerts_in_memory"],
                "by_type": stats["by_type"],
                "by_severity": stats["by_severity"],
            },
            "recent_alerts": recent,
            "suspicious_ips": suspicious[:20],  # Top 20 suspicious IPs
        })

    logger.info("Dashboard Flask app created")
    return app
