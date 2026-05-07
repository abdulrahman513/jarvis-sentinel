# shield.py
import subprocess
import csv
import os
import requests
import actuators
import time
from datetime import datetime
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()
console = Console()

VAULT_DIR = "/media/rana/80B68532B68529AC/jarvis/evidence_vault"

# SOC Pro Feature: Cooldown Cache to prevent "Notification Storms"
RECENTLY_BLOCKED = {}

def capture_packets(ip_address: str, duration: int = 10):
    timestamp = datetime.now().strftime("%H%M%S")
    pcap_file = os.path.join(VAULT_DIR, f"forensics_{ip_address}_{timestamp}.pcap")
    console.print(f"[bold cyan][SYSTEM] Jarvis is capturing live traffic...[/bold cyan]")
    cmd = ["tcpdump", "-i", "any", "host", ip_address, "-w", pcap_file, "-U"]
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        process.wait(timeout=duration)
        return pcap_file
    except Exception:
        if process: process.terminate()
        return "Capture ended."

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
    except Exception: return "Connection Error"

# ... (Keep your other imports and VAULT_DIR)

def is_trusted(ip_address: str) -> bool:
    """Checks the Policy Engine for whitelisted IPs or Maintenance Mode."""
    try:
        # We read the config live so changes take effect immediately
        with open("config.json", "r") as f:
            config = json.load(f)
        
        # If Maintenance Mode is ON, Jarvis stays awake but won't block anyone
        if config.get("maintenance_mode", False):
            console.print("[bold yellow][POLICY] Maintenance Mode ACTIVE. Ignoring threat.[/bold yellow]")
            return True
            
        return ip_address in config.get("trusted_ips", [])
    except Exception as e:
        console.print(f"[bold red][ERROR] Config Read Failed: {e}[/bold red]")
        return False # Safer to assume NOT trusted if the file is broken

# --- UPDATE YOUR block_ip function to use the new check ---

def block_ip(ip_address: str) -> str:
    # 1. The Policy Check (New)
    if is_trusted(ip_address):
        return f"SKIP: {ip_address} is a trusted source or Maintenance Mode is active."

    # 2. The Rest of the defense (Existing)
    console.print(f"[bold red][SYSTEM] Jarvis is executing active defense against: {ip_address}[/bold red]")
    # ... (the rest of your block_ip code)

    console.print(f"[bold red][SYSTEM] Jarvis is executing active defense against: {ip_address}[/bold red]")
    intel = check_ip_reputation(ip_address)
    
    # Add to cooldown immediately to prevent double-processing
    RECENTLY_BLOCKED[ip_address] = current_time
    
    pcap_path = capture_packets(ip_address)
    
    try:
        subprocess.run(["ufw", "deny", "from", ip_address], check=True)
        subprocess.run(["ufw", "--force", "enable"], capture_output=True)
        
        # Log to CSV
        log_file = os.path.join(VAULT_DIR, "jarvis_forensics.csv")
        with open(log_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ip_address, intel, "UFW_BLOCK"])
        
        discord_msg = f"**Action:** IP Blocked\n**Target IP:** `{ip_address}`\n**Intel:** {intel}\n**Forensics:** `{pcap_path}`"
        actuators.send_discord_alert("Intrusion Mitigated", discord_msg)
        
        return f"IP {ip_address} blocked."
    except Exception as e:
        return f"Block Error: {e}"

def listen_to_logs_live():
    """Universal Log Streamer: Listens to the whole journal and filters manually."""
    # We remove the unit filter and just follow the live journal
    cmd = ["journalctl", "-f", "-n", "0"]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    
    console.print("[bold green][SYSTEM] Jarvis is now live-syncing with the System Journal...[/bold green]")
    
    for line in process.stdout:
        # We look for both the service tag and the failure string
        if "sshd" in line and "Failed password" in line:
            yield line

def get_recent_auth_logs() -> str:
    try:
        cmd = "journalctl -n 20 | grep 'Failed password'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip() if result.stdout.strip() else "No recent history."
    except Exception: return "Error"

def get_active_connections() -> str:
    return subprocess.run(["ss", "-tunp"], capture_output=True, text=True).stdout

def get_running_processes() -> str:
    result = subprocess.run(["ps", "-eo", "pid,user,%mem,command", "--sort=-%mem"], capture_output=True, text=True)
    return '\n'.join(result.stdout.split('\n')[:100])