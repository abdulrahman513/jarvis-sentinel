# main.py (Final Production Version)
import re
import sys
import os
import threading
import time
import shield
import brain
import database
import actuators
from brain import JarvisBrain
from groq_brain import GroqBrain 
from monitor import SystemMonitor
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()
PROCESSED_LOGS = set()
LAST_ALERT_TIME = 0
IS_LOCKED = False

def handle_forensics_async(threat_ip, defense_data, jarvis, groq_fallback):
    global LAST_ALERT_TIME, IS_LOCKED
    try:
        # 1. AI ANALYSIS
        analysis = ""
        try:
            analysis = brain.analyze_forensic_summary(defense_data['summary_path'])
            if "500" in analysis or "ERROR" in analysis: raise Exception("Server Glitch")
        except:
            analysis = groq_fallback.think(f"Analyze this attack: {defense_data['summary_path']}")

        # 2. PERSISTENCE
        database.log_incident(
            threat_ip, "High Risk", defense_data['geo'].get('city', 'Unknown'), 
            defense_data['summary_path'], defense_data['summary_path'], "UFW_BLOCK", analysis
        )
        
        # 3. SMART NOTIFICATION (Rate limiting alerts to 1 per 5 seconds)
        current_time = time.time()
        if (current_time - LAST_ALERT_TIME) > 5:
            discord_msg = f"🛡️ **Mitigated:** `{threat_ip}`\n**Insight:** {analysis}\n**Map:** [View]({defense_data['map_url']})"
            actuators.send_discord_alert("J.A.R.V.I.S. Mitigation", discord_msg)
            LAST_ALERT_TIME = current_time
        
        console.print(Panel(Markdown(f"### Background Analysis Complete\n**IP:** {threat_ip}\n**Analysis:** {analysis}"), border_style="green"))
    except Exception as e:
        console.print(f"[bold red][ERROR] Forensics Failed for {threat_ip}: {e}[/bold red]")

def run_sentinel_loop(jarvis, groq_fallback):
    global IS_LOCKED
    console.print("[bold yellow][SYSTEM] J.A.R.V.I.S. Active Stream Monitor engaged.[/bold yellow]")
    
    for log_line in shield.listen_to_logs_live():
        if log_line in PROCESSED_LOGS: continue
        
        ip_match = re.search(r'from\s+(\d+\.\d+\.\d+\.\d+)', log_line)
        if ip_match:
            threat_ip = ip_match.group(1)
            
            # IMMEDIATE BLOCK (Database check prevents duplicates here)
            defense_data = shield.block_ip(threat_ip)
            if not defense_data: continue 
            
            PROCESSED_LOGS.add(log_line)
            
            # SMART LOCK: Only lock if not already locked
            if not IS_LOCKED:
                actuators.lock_workstation()
                IS_LOCKED = True
                # Reset lock state after 30 seconds to allow for future locks
                threading.Timer(30, lambda: globals().update(IS_LOCKED=False)).start()

            # OFFLOAD FORENSICS
            threading.Thread(
                target=handle_forensics_async, 
                args=(threat_ip, defense_data, jarvis, groq_fallback),
                daemon=True
            ).start()
            
            console.print(f"[bold green][INFO] Neutralized {threat_ip}. Processing intel...[/bold green]")

def main():
    if os.geteuid() != 0:
        console.print("[bold red][ERROR] Requires root.[/bold red]")
        return

    jarvis = JarvisBrain()
    groq_fallback = GroqBrain()
    watcher = SystemMonitor()
    watcher.start()

    if "--sentinel" in sys.argv:
        run_sentinel_loop(jarvis, groq_fallback)

if __name__ == "__main__":
    main()