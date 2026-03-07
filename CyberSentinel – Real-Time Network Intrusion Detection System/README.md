# 🛡️ CyberSentinel — Real-Time Network Intrusion Detection System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Scapy](https://img.shields.io/badge/Scapy-2.5+-2496ED?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A professional-grade Python cybersecurity tool that monitors network traffic in real-time, detects suspicious behavior, and generates security alerts.**

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Dashboard](#-dashboard)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Example Output](#-example-output)
- [Technologies](#-technologies)

---

## 🎯 Overview

**CyberSentinel** is a network intrusion detection system (NIDS) built in Python. It captures live network packets, analyzes them using both signature-based rules and statistical anomaly detection, and generates real-time alerts when suspicious behavior is detected.

### What It Detects

| Threat Type | Description |
|---|---|
| **Port Scanning** | Single IP accessing many unique ports rapidly |
| **Traffic Spikes** | Packets-per-second exceeding threshold (potential DoS) |
| **Rate Anomalies** | Statistical deviations from normal traffic patterns |
| **Unknown IPs** | Connections from untrusted/unknown source addresses |

---

## ✨ Features

- **🔍 Real-Time Packet Capture** — Scapy-based sniffer with protocol extraction (TCP/UDP/ICMP)
- **🧠 Dual Detection Engine** — Signature-based rules + statistical anomaly detection
- **🚨 Multi-Channel Alerts** — Colored terminal output + persistent log files
- **🌐 Web Dashboard** — Dark-themed Flask dashboard with auto-refreshing stats
- **⚙️ Configurable Thresholds** — YAML-based configuration for all detection parameters
- **🔒 Alert Cooldown** — Prevents alert flooding from duplicate detections
- **📊 Session Statistics** — Summary report on shutdown with alert breakdowns
- **🧪 Unit Tested** — Comprehensive test suite with pytest

---

## 🏗️ Architecture

```
                    ┌──────────────┐
                    │   main.py    │
                    │ (Entry Point)│
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
     ┌────────▼───────┐    │    ┌───────▼────────┐
     │ PacketSniffer   │    │    │ Flask Dashboard │
     │ (scapy capture) │    │    │ (web UI)        │
     └────────┬───────┘    │    └────────────────┘
              │            │
     ┌────────▼────────────▼──────────┐
     │         Detection Layer         │
     │  ┌───────────┐ ┌─────────────┐ │
     │  │RuleEngine │ │AnomalyDetect│ │
     │  │(signatures)│ │(statistics) │ │
     │  └─────┬─────┘ └──────┬──────┘ │
     └────────┼───────────────┼────────┘
              │               │
     ┌────────▼───────────────▼────────┐
     │         Alert System            │
     │  ┌────────────┐ ┌───────────┐  │
     │  │AlertManager│→│ Notifier  │  │
     │  │(storage)   │ │(output)   │  │
     │  └────────────┘ └───────────┘  │
     └─────────────────────────────────┘
```

---

## 📦 Installation

### Prerequisites

- **Python 3.10+** installed
- **Administrator/root privileges** (required for packet capture)
- **Npcap** (Windows) or **libpcap** (Linux/Mac) for scapy packet capture

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd cybersentinel
```

### Step 2: Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows (PowerShell):
.\venv\Scripts\Activate

# Linux/Mac:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Npcap (Windows Only)

Download and install [Npcap](https://npcap.com/#download) with "WinPcap API-compatible Mode" enabled. This is required for scapy to capture packets on Windows.

---

## 🚀 Usage

### Start CyberSentinel

> ⚠️ **Important:** Packet sniffing requires elevated privileges!

```bash
# Windows — Run PowerShell as Administrator:
python main.py

# Linux/Mac:
sudo python main.py
```

### What Happens

1. Configuration is loaded from `config.yaml`
2. All detection engines are initialized
3. Flask dashboard starts at `http://localhost:5000`
4. Packet capture begins (you'll see a progress counter)
5. Alerts appear in the terminal when threats are detected

### Stop CyberSentinel

Press **Ctrl+C** for a graceful shutdown. You'll see a session summary:

```
  ╔══════════════════════════════════════╗
  ║         SESSION SUMMARY              ║
  ╠══════════════════════════════════════╣
  ║  Packets captured:  12,847           ║
  ║  Total alerts:      7                ║
  ║  Alerts in memory:  7                ║
  ╚══════════════════════════════════════╝

  Alerts by type:
    • PORT_SCAN: 3
    • UNKNOWN_IP: 4
```

---

## ⚙️ Configuration

Edit `config.yaml` to customize all detection parameters:

```yaml
# Port Scan Detection
detection:
  port_scan:
    threshold: 15      # Unique ports before alert
    time_window: 60    # Seconds to track

  traffic_spike:
    threshold: 100     # Max packets/second
    time_window: 10    # Seconds for rate calc

  unknown_ip:
    enabled: true
    trusted_ips:
      - "192.168.1.0/24"
      - "10.0.0.0/8"

# Dashboard
dashboard:
  enabled: true
  port: 5000
```

---

## 🌐 Dashboard

CyberSentinel includes a real-time web dashboard accessible at `http://localhost:5000`.

### Dashboard Features

- **📊 Stats Cards** — Live packet count, total alerts, suspicious IPs, threat types
- **🚨 Alerts Table** — Real-time feed of security alerts with severity badges
- **⚠️ Suspicious IPs** — Ranked list of flagged IP addresses
- **🔄 Auto-Refresh** — Updates every 3 seconds via API polling
- **🌙 Dark Theme** — Professional cybersecurity aesthetic

---

## 📁 Project Structure

```
cybersentinel/
├── app/
│   ├── sniffer/
│   │   └── packet_sniffer.py      # Scapy packet capture engine
│   ├── detection/
│   │   ├── rule_engine.py         # Signature-based detection rules
│   │   └── anomaly_detector.py    # Statistical anomaly detection
│   ├── alerts/
│   │   ├── alert_manager.py       # Central alert management
│   │   └── notifier.py            # Terminal + log file output
│   ├── dashboard/
│   │   ├── server.py              # Flask dashboard server
│   │   └── templates/
│   │       └── dashboard.html     # Dashboard UI template
│   └── utils/
│       ├── config_loader.py       # YAML config parser
│       └── logger.py              # Colored logging system
├── data/
│   └── alerts.log                 # Persistent alert log file
├── tests/
│   └── test_sniffer.py            # Unit tests
├── main.py                        # Application entry point
├── config.yaml                    # Configuration file
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 🧪 Testing

Run the test suite (no admin privileges needed):

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --tb=short
```

### Test Coverage

| Module | Tests |
|---|---|
| Config Loader | Valid/invalid config loading, section access |
| Rule Engine | Port scan detection, traffic spikes, cooldowns |
| Anomaly Detector | Unknown IPs, trusted IP bypass, deduplication |
| Alert Manager | Alert creation, storage, eviction, statistics |
| Notifier | Log file writing |

---

## 📸 Example Output

### Terminal Alert

```
──────────────────────────────────────────────────────────────────────
  🔴 SECURITY ALERT #3
──────────────────────────────────────────────────────────────────────
  Time:        2026-03-05 00:15:42
  Type:        PORT_SCAN
  Severity:    HIGH
  Source IP:   10.0.0.50
  Details:     Port scan detected from 10.0.0.50: 18 unique ports
               accessed in 60s (threshold: 15)
──────────────────────────────────────────────────────────────────────
```

### Alerts Log File (`data/alerts.log`)

```
[2026-03-05 00:15:42] ALERT #3 | Type: PORT_SCAN | Severity: HIGH | Source: 10.0.0.50 | Details: Port scan detected...
[2026-03-05 00:16:01] ALERT #4 | Type: UNKNOWN_IP | Severity: LOW | Source: 203.0.113.50 | Details: Connection from unknown IP...
```

---

## 🛠️ Technologies

| Technology | Purpose |
|---|---|
| **Python 3.10+** | Core programming language |
| **Scapy** | Packet capture and protocol analysis |
| **Flask** | Web dashboard server |
| **Pandas** | Data manipulation (traffic analysis) |
| **PyYAML** | Configuration file parsing |
| **scikit-learn** | Anomaly detection (optional) |
| **Colorama** | Colored terminal output (Windows support) |
| **pytest** | Unit testing framework |

---

## 📜 License

This project is licensed under the MIT License.

---

<div align="center">

**Built with 🔒 by CyberSentinel**

*Stay secure. Stay vigilant.*

</div>
