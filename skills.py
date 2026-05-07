import shield
import actuators
import reporter
from rich.console import Console

console = Console()

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