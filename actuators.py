import os
import requests
import subprocess
from dotenv import load_dotenv

load_dotenv()

def send_discord_alert(title, message):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url: return
    
    data = {
        "embeds": [{
            "title": title,
            "description": message,
            "color": 15158332,
            "footer": {"text": "J.A.R.V.I.S. Autonomous Sentinel | Defense Active"}
        }]
    }
    try:
        requests.post(webhook_url, json=data, timeout=5)
    except: pass

def lock_workstation():
    """Triggers the system lock-session command."""
    try:
        subprocess.run(["loginctl", "lock-sessions"], check=True)
        return "Workstation locked."
    except Exception as e:
        return f"Lock failed: {str(e)}"

def display_desktop_alert(title, message):
    """Sends a desktop notification to the user's active session."""
    try:
        user = os.getenv("SUDO_USER", "rana")
        cmd = f"sudo -u {user} DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u {user})/bus notify-send '{title}' '{message}'"
        subprocess.run(cmd, shell=True)
        return "Desktop notification sent."
    except:
        return "Notification failed."