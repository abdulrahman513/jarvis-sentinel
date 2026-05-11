# 🛡️ Jarvis Sentinel: Autonomous Blue Team Security Agent

**Jarvis Sentinel** is a modular, AI-enhanced security orchestration and response (SOAR) agent designed for Linux environments. It monitors system integrity, analyzes network traffic in real-time, and executes automated defensive countermeasures against active threats.

## 🚀 Key Features
- **Intelligent Monitoring:** Real-time log and network traffic analysis using `Scapy`.
- **Active Defense (Shield):** Automated firewall management (UFW) and session mitigation.
- **Threat Intelligence:** Native integration with `AbuseIPDB` for global IP reputation checking.
- **Automated Response:** Triggers system locks (`loginctl`) and Discord alerts upon high-confidence threat detection.
- **Forensic Vault:** Secure logging of malicious packets for post-incident investigation.
- **Web Dashboard:** A clean HTML interface to monitor sentinel status and threat history.

## 🛠️ Tech Stack
- **Core:** Python 3.x
- **Network Analysis:** Scapy
- **Database:** SQLite
- **Automation:** Systemd (runs as a background service)
- **Dashboard:** Flask / HTML / CSS

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/abdulrahman513/jarvis-sentinel.git](https://github.com/abdulrahman513/jarvis-sentinel.git)
   cd jarvis-sentinel
