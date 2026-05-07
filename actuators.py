# actuators.py
import subprocess
import os
import requests
from rich.console import Console
from dotenv import load_dotenv

# Ensure .env is loaded for the Webhook URL
load_dotenv()
console = Console()

def send_discord_alert(title: str, message: str, color: int = 15158332) -> str:
    """Sends a professional-grade security alert to a Discord Webhook."""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return "Discord Error: Webhook URL not found in .env"

    payload = {
        "embeds": [{
            "title": f"🚨 {title}",
            "description": message,
            "color": color, # Default is Red
            "footer": {"text": "J.A.R.V.I.S. Autonomous Sentinel"}
        }]
    }

    try:
        # Standard ISO format for Discord timestamps
        from datetime import datetime
        payload["embeds"][0]["timestamp"] = datetime.utcnow().isoformat()
        
        # CRITICAL: timeout=10 prevents the entire agent from freezing if Discord is lagging
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 204:
            return "Discord alert dispatched."
        return f"Discord Error: {response.status_code}"
    except Exception as e:
        return f"Discord Connection Error: {e}"

def display_desktop_alert(title: str, message: str) -> str:
    """Sends a native desktop notification."""
    console.print(f"[bold magenta][SYSTEM] Jarvis is sending DBus Signal: {message}[/bold magenta]")
    try:
        subprocess.run(["notify-send", "-u", "critical", title, message], check=True)
        return "Notification sent."
    except Exception as e:
        return f"Notification Error: {e}"

def lock_workstation() -> str:
    """Locks the Linux desktop session."""
    console.print("[bold red][SYSTEM] Jarvis is locking the workstation...[/bold red]")
    try:
        # Most reliable way to lock GNOME/COSMIC from root
        subprocess.run(["loginctl", "lock-sessions"], check=True)
        return "Workstation locked successfully."
    except Exception as e:
        return f"Lock Error: {e}"

def take_security_snapshot(filename: str = "alert_snapshot.png") -> str:
    """Captures the screen if possible (forensic evidence)."""
    try:
        import pyautogui
        console.print(f"[bold yellow][SYSTEM] Jarvis is taking a forensic snapshot: {filename}[/bold yellow]")
        pyautogui.screenshot(filename)
        return f"Snapshot saved as {filename}"
    except Exception:
        return "Snapshot failed: GUI dependency or session issue."