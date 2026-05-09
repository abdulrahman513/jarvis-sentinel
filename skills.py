# In skills.py
import sqlite3
import database
import shield
import actuators
import reporter
from rich.console import Console

console = Console()

def query_incident_history(ip_address: str) -> str:
    """Queries the J.A.R.V.I.S. database for the exact timestamp and details of a specific IP's block."""
    conn = sqlite3.connect(database.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, action_taken, brain_analysis FROM incidents WHERE ip_address = ?", (ip_address,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return f"IP {ip_address} was blocked on {result[0]} via {result[1]}. Analysis: {result[2]}"
    return f"No record found for IP {ip_address}."

# Make sure to add it to your JARVIS_TOOLS list at the bottom!
JARVIS_TOOLS = [
    # ... your other tools ...
    query_incident_history
]

def scan_network_connections() -> str:
    return shield.get_active_connections()

def trigger_visual_alert(message: str) -> str:
    return actuators.display_desktop_alert("J.A.R.V.I.S. Alert", message)

def lock_screen() -> str:
    return actuators.lock_workstation()

def block_malicious_ip(ip_address: str) -> str:
    return shield.block_ip(ip_address)

def analyze_auth_logs() -> str:
    return shield.get_recent_auth_logs()

def scan_active_processes() -> str:
    return shield.get_running_processes()

def generate_weekly_report() -> str:
    console.print("[bold yellow][SYSTEM] Jarvis is compiling the security report...[/bold yellow]")
    return reporter.generate_security_report()

JARVIS_TOOLS = [
    scan_network_connections,
    trigger_visual_alert,
    lock_screen,
    block_malicious_ip,
    analyze_auth_logs,
    scan_active_processes,
    generate_weekly_report
]