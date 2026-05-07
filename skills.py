# skills.py
import shield
import actuators
from rich.console import Console

console = Console()

def scan_network_connections() -> str:
    """Use this tool to get a list of all currently active TCP/UDP network connections on the system."""
    console.print("[bold yellow][SYSTEM] Jarvis is physically accessing the network stack...[/bold yellow]")
    return shield.get_active_connections()

def trigger_visual_alert(message: str) -> str:
    """Use this tool to pop up a native desktop notification to warn the user of a threat."""
    console.print(f"[bold magenta][SYSTEM] Jarvis is triggering a UI Actuator: {message}[/bold magenta]")
    return actuators.display_desktop_alert("Threat Detected", message)

def lock_screen() -> str:
    """Use this tool to lock the user's computer screen immediately if you suspect a physical intrusion."""
    console.print("[bold red][SYSTEM] Jarvis is locking the workstation...[/bold red]")
    return actuators.lock_workstation()

def block_malicious_ip(ip_address: str) -> str:
    """Use this tool to block an IP address in the system firewall if it is deemed malicious."""
    console.print(f"[bold red][SYSTEM] Jarvis is updating UFW to block IP: {ip_address}[/bold red]")
    return shield.block_ip(ip_address)

def terminate_process(pid: int) -> str:
    """Use this tool to kill a running process by its PID if it is consuming too many resources or looks like malware."""
    console.print(f"[bold red][SYSTEM] Jarvis is sending SIGKILL to PID: {pid}[/bold red]")
    return shield.kill_process_by_pid(pid)

def analyze_auth_logs() -> str:
    """Use this tool to fetch the latest authentication logs to check for brute-force attacks or unauthorized access."""
    console.print("[bold yellow][SYSTEM] Jarvis is reading secure authentication logs...[/bold yellow]")
    return shield.get_recent_auth_logs()

def scan_active_processes() -> str:
    """Use this tool to get a list of currently running system processes, including their PID and memory usage."""
    console.print("[bold yellow][SYSTEM] Jarvis is reading the system process tree...[/bold yellow]")
    return shield.get_running_processes()

def capture_forensic_snapshot(filename: str = "security_breach_snapshot.png") -> str:
    """Use this tool to take a visual screenshot of the user's desktop to preserve evidence during an attack."""
    console.print(f"[bold yellow][SYSTEM] Jarvis is capturing forensic GUI snapshot...[/bold yellow]")
    return actuators.take_security_snapshot(filename)

# List of tools to pass to the AI model
# CRITICAL: Every function defined above MUST be in this list for the AI to see and use it.
JARVIS_TOOLS = [
    scan_network_connections,
    trigger_visual_alert,
    lock_screen,
    block_malicious_ip, 
    terminate_process, 
    analyze_auth_logs,
    scan_active_processes,
    capture_forensic_snapshot
]