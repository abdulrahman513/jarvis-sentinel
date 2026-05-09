# shield.py
import subprocess
import os
import json
import requests
import time
import database
from datetime import datetime
from rich.console import Console
from scapy.all import sniff, wrpcap, IP, TCP, Raw

console = Console()
VAULT_DIR = "/home/rana/jarvis-sentinel/evidence_vault/"
CONFIG_PATH = "/home/rana/jarvis-sentinel/config.json"

def is_maintenance_active():
    """Checks the config file for the maintenance mode flag."""
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            return config.get("policy_engine", {}).get("maintenance_mode", False)
    except Exception as e:
        console.print(f"[bold red][ERROR] Could not read config for maintenance check: {e}[/bold red]")
        return False

def get_ip_location(ip_address: str) -> dict:
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=5).json()
        if response.get("status") == 'success':
            return {
                "city": response.get("city"), 
                "country": response.get("country"),
                "lat": response.get("lat"), 
                "lon": response.get("lon")
            }
    except: pass
    return {"city": "Unknown", "country": "Unknown"}

def summarize_pcap(pcap_path: str):
    txt_path = pcap_path.replace(".pcap", "_summary.txt")
    try:
        from scapy.all import rdpcap
        packets = rdpcap(pcap_path)
        with open(txt_path, "w") as f:
            f.write(f"J.A.R.V.I.S. FORENSIC EVIDENCE\nSource: {pcap_path}\n{'-'*50}\n")
            for i, pkt in enumerate(packets[:30]):
                if pkt.haslayer(IP):
                    proto = "TCP" if pkt.haslayer(TCP) else "UDP" if pkt.haslayer(UDP) else "OTHER"
                    flags = pkt[TCP].flags if pkt.haslayer(TCP) else "N/A"
                    payload = pkt[Raw].load.hex()[:32] if pkt.haslayer(Raw) else ""
                    f.write(f"[{i}] {pkt[IP].src} -> {pkt[IP].dst} | {proto} | Flags: {flags} | Data: {payload}\n")
        return txt_path
    except: return "Summary Failed"

def capture_packets(ip_address: str, duration: int = 5):
    timestamp = datetime.now().strftime("%H%M%S")
    os.makedirs(VAULT_DIR, exist_ok=True) 
    pcap_file = os.path.join(VAULT_DIR, f"forensics_{ip_address}_{timestamp}.pcap")
    try:
        # Sniffing only the threat host
        packets = sniff(filter=f"host {ip_address}", timeout=duration)
        if len(packets) == 0: 
            return "No Traffic Detected"
        wrpcap(pcap_file, packets)
        summarize_pcap(pcap_file)
        return pcap_file
    except: 
        return "Capture Failed"

def block_ip(ip_address: str) -> dict:
    """The central defense command. Blocks and gathers forensic data."""
    ip_address = ip_address.strip()
    
    # 1. MAINTENANCE GATE: Strictly enforced before any action
    if is_maintenance_active():
        console.print(f"[bold yellow][POLICY] Maintenance Active. Ignoring threat from {ip_address}[/bold yellow]")
        return None

    # 2. DUPLICATE CHECK: Don't re-process if already in DB
    if database.is_blacklisted(ip_address):
        return None
    
    # 3. NEUTRALIZE: Instant Firewall Drop
    console.print(f"[bold red][SYSTEM] FIREWALL BLOCK ACTIVE: {ip_address}[/bold red]")
    subprocess.run(["sudo", "ufw", "deny", "from", ip_address], capture_output=True)
    
    # 4. PERSISTENCE: Log to blacklist immediately
    database.add_to_blacklist(ip_address, "Sentinel Brute Force Detection")
    
    # 5. FORENSICS: Gather Intelligence
    geo = get_ip_location(ip_address)
    pcap_path = capture_packets(ip_address)
    summary_path = pcap_path.replace(".pcap", "_summary.txt") if "forensics" in pcap_path else "N/A"
    
    # 6. RETURN: Data for the Brain and Dashboard
    return {
        "ip": ip_address,
        "geo": geo,
        "summary_path": summary_path,
        "map_url": f"https://www.google.com/maps?q={geo.get('lat')},{geo.get('lon')}" if geo.get('lat') else "N/A"
    }

def listen_to_logs_live():
    """Streams auth logs to the sentinel monitor."""
    cmd = ["journalctl", "-f", "-n", "0"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    for line in process.stdout:
        if "sshd" in line and "Failed password" in line:
            yield line