# shield.py
import subprocess
import os
import json
import requests
import time
import brain
import database
from datetime import datetime
from rich.console import Console
from scapy.all import sniff, wrpcap, IP, TCP, Raw

console = Console()
VAULT_DIR = "/home/rana/jarvis-sentinel/evidence_vault/"

def get_ip_location(ip_address: str) -> dict:
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=5).json()
        if response.get("status") == 'success':
            return {
                "city": response.get("city"), "country": response.get("country"),
                "lat": response.get("lat"), "lon": response.get("lon")
            }
    except: pass
    return {}

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
        packets = sniff(filter=f"host {ip_address}", timeout=duration)
        if len(packets) == 0: return "No Traffic Detected"
        wrpcap(pcap_file, packets)
        summarize_pcap(pcap_file)
        return pcap_file
    except: return "Capture Failed"

def block_ip(ip_address: str) -> dict:
    """Core defense: Uses persistent SQLite blacklist for reboot-proof security."""
    ip_address = ip_address.strip()
    
    # 1. DATABASE CHECK: Replacing the old in-memory dictionary
    if database.is_blacklisted(ip_address):
        # We check the firewall just in case the rule was manually deleted
        return None 
    
    console.print(f"[bold red][SYSTEM] NEW THREAT NEUTRALIZED: {ip_address}[/bold red]")
    
    # 2. IMMEDIATE BLOCK
    subprocess.run(["ufw", "deny", "from", ip_address], capture_output=True)
    
    # 3. UPDATE BLACKLIST: Permanent record
    database.add_to_blacklist(ip_address, "SSH Brute Force Trigger")
    
    # 4. GATHER DATA
    geo = get_ip_location(ip_address)
    pcap_path = capture_packets(ip_address)
    summary_path = pcap_path.replace(".pcap", "_summary.txt") if "forensics" in pcap_path else "N/A"
    
    return {
        "ip": ip_address,
        "geo": geo,
        "summary_path": summary_path,
        "map_url": f"https://www.google.com/maps?q={geo.get('lat')},{geo.get('lon')}" if geo.get('lat') else "N/A"
    }

def listen_to_logs_live():
    cmd = ["journalctl", "-f", "-n", "0"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    for line in process.stdout:
        if "sshd" in line and "Failed password" in line:
            yield line