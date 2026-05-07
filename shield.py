import subprocess
import csv
import os
import json
import requests
import actuators
import time
from datetime import datetime
from rich.console import Console
from dotenv import load_dotenv
from scapy.all import sniff, wrpcap, IP, TCP, UDP

load_dotenv()
console = Console()

VAULT_DIR = "/home/rana/jarvis-sentinel/evidence_vault/"
LOG_FILE = os.path.join(VAULT_DIR, "jarvis_forensics.csv")

RECENTLY_BLOCKED = {}

def is_trusted(ip_address: str) -> bool:
    """Checks the Policy Engine for whitelisted IPs or Maintenance Mode."""
    try:
        if not os.path.exists("config.json"):
            return False
        with open("config.json", "r") as f:
            config = json.load(f)

        # Updated path to match the new nested structure
        policy = config.get("policy_engine", {})
        
        if policy.get("maintenance_mode", False):
            console.print("[bold yellow][POLICY] Maintenance Mode ACTIVE. Ignoring threat.[/bold yellow]")
            return True

        return ip_address in policy.get("trusted_ips", [])
    except Exception as e:
        console.print(f"[bold red][ERROR] Config Read Failed: {e}[/bold red]")
        return False

def get_ip_location(ip_address: str) -> dict:
    """Fetches geographic coordinates and origin info for the attacker."""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=5).json()
        # Fixed: Changed response.status to response.get("status")
        if response.get("status") == 'success':
            return {
                "city": response.get("city"),
                "country": response.get("country"),
                "lat": response.get("lat"),
                "lon": response.get("lon"),
                "isp": response.get("isp")
            }
    except: pass
    return {}

def summarize_pcap(pcap_path: str):
    """Translates binary PCAP data into a human-readable forensic summary."""
    txt_path = pcap_path.replace(".pcap", "_summary.txt")
    try:
        from scapy.all import rdpcap
        packets = rdpcap(pcap_path)
        with open(txt_path, "w") as f:
            f.write(f"J.A.R.V.I.S. FORENSIC TRANSLATION\nSource File: {pcap_path}\n")
            f.write("-" * 40 + "\n")
            for i, pkt in enumerate(packets[:20]):
                if pkt.haslayer(IP):
                    proto = "TCP" if pkt.haslayer(TCP) else "UDP" if pkt.haslayer(UDP) else "OTHER"
                    f.write(f"[{i}] {pkt[IP].src} -> {pkt[IP].dst} | Proto: {proto} | Size: {len(pkt)} bytes\n")
        return txt_path
    except: return "Summary Failed"

def capture_packets(ip_address: str, duration: int = 10):
    timestamp = datetime.now().strftime("%H%M%S")
    os.makedirs(VAULT_DIR, exist_ok=True) 
    pcap_file = os.path.join(VAULT_DIR, f"forensics_{ip_address}_{timestamp}.pcap")
    
    console.print(f"[bold cyan][SYSTEM] Jarvis is capturing live traffic...[/bold cyan]")
    try:
        packets = sniff(filter=f"host {ip_address}", timeout=duration)
        wrpcap(pcap_file, packets)
        summarize_pcap(pcap_file)
        return pcap_file
    except Exception as e:
        console.print(f"[bold red][ERROR] Capture Error: {e}[/bold red]")
        return "Capture Failed"

def check_ip_reputation(ip_address: str) -> str:
    api_key = os.getenv("ABUSEIPDB_API_KEY")
    if not api_key: return "No API Key"
    url = 'https://api.abuseipdb.com/api/v2/check'
    params = {'ipAddress': ip_address, 'maxAgeInDays': '90'}
    headers = {'Accept': 'application/json', 'Key': api_key}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return f"Risk Score: {data['data']['abuseConfidenceScore']}% | Origin: {data['data']['countryCode']}"
        return "Lookup Failed"
    except: return "Connection Error"

def block_ip(ip_address: str) -> str:
    if ip_address in ["127.0.0.1", "::1"]: return "SKIP: Localhost"
    
    current_time = time.time()
    console.print(f"[bold red][SYSTEM] Jarvis is executing active defense: {ip_address}[/bold red]")
    
    # Intelligence Gathering
    intel = check_ip_reputation(ip_address)
    geo = get_ip_location(ip_address)
    location_str = f"{geo.get('city', 'Unknown')}, {geo.get('country', 'Unknown')}"
    
    # Generate Link
    if geo.get('lat'):
        map_url = f"https://www.google.com/maps?q={geo.get('lat')},{geo.get('lon')}"
    else:
        map_url = "Location Unavailable"
    
    RECENTLY_BLOCKED[ip_address] = current_time
    pcap_path = capture_packets(ip_address)

    try:
        subprocess.run(["ufw", "deny", "from", ip_address], check=True)
        subprocess.run(["ufw", "--force", "enable"], capture_output=True)
        
        with open(LOG_FILE, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ip_address, intel, "UFW_BLOCK", location_str])

        # New Discord Format
        discord_msg = (
            f"🛡️ **Intrusion Mitigated**\n"
            f"**Target IP:** `{ip_address}`\n"
            f"**Intelligence:** {intel}\n"
            f"**Approx Location:** {location_str}\n"
            f"**Coordinates:** [View on Map]({map_url})\n"
            f"**Forensics:** `{pcap_path}` (Summary available)"
        )
        actuators.send_discord_alert("J.A.R.V.I.S. Sentinel Alert", discord_msg)
        actuators.lock_workstation()
        actuators.display_desktop_alert("Intrusion Mitigated", f"IP {ip_address} has been blocked.")

        return f"SUCCESS: {ip_address} blocked. Origin: {location_str}."
    except Exception as e:
        return f"Defensive Error: {str(e)}"

def listen_to_logs_live():
    cmd = ["journalctl", "-f", "-n", "0"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    console.print("[bold green][SYSTEM] Jarvis is now live-syncing with the System Journal...[/bold green]")
    for line in process.stdout:
        if "sshd" in line and "Failed password" in line:
            yield line

def get_active_connections() -> str:
    return subprocess.run(["ss", "-tunp"], capture_output=True, text=True).stdout

def get_recent_auth_logs() -> str:
    cmd = "journalctl -n 20 | grep 'Failed password'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip() if result.stdout.strip() else "No recent history."

def get_running_processes() -> str:
    result = subprocess.run(["ps", "-eo", "pid,user,%mem,command", "--sort=-%mem"], capture_output=True, text=True)
    return '\n'.join(result.stdout.split('\n')[:100])