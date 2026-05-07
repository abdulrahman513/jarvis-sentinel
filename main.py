# main.py
import re # Add this at the top of main.py
import sys
import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from brain import JarvisBrain
from monitor import SystemMonitor
import shield

console = Console()

def ensure_root_privileges():
    if os.geteuid() != 0:
        args = ['sudo', sys.executable] + sys.argv
        os.execlpe('sudo', *args, os.environ)

def run_sentinel_loop(jarvis):
    console.print("[bold yellow][SYSTEM] J.A.R.V.I.S. Active Stream Monitor engaged.[/bold yellow]")
    
    while True:
        try:
            console.print("[dim]Listening for real-time authentication failures...[/dim]")
            for log_entry in shield.listen_to_logs_live():
                # NEW PRO LOGIC: Extract IP using Regex BEFORE calling AI
                ip_match = re.search(r'from (\d+\.\d+\.\d+\.\d+)', log_entry)
                target_ip = ip_match.group(1) if ip_match else "Unknown"

                # Check if this IP is already being handled to save Quota
                if target_ip in shield.RECENTLY_BLOCKED:
                    continue # Silently skip the AI call

                console.print(f"\n[bold red][ALERT][/bold red] New unique threat: {target_ip}")
                directive = f"NEW LOG: {log_entry}\nAnalyze this. If foreign attack, block and lock."
                
                with console.status("[bold cyan]Consulting Brain...[/bold cyan]"):
                    response = jarvis.think(directive)
                console.print(Panel(Markdown(response), title="Jarvis (Live Response)", border_style="red"))
                
        except Exception as e:
            console.print(f"[bold red]Streamer error: {e}. Restarting...[/bold red]")
            time.sleep(5)

def main():
    ensure_root_privileges()
    
    # Early print to confirm script is actually running
    console.print(Panel.fit("[bold blue]J.A.R.V.I.S. Blue Team Interface[/bold blue]\n[green]Status: ACTIVE | Persistence: ENABLED[/green]"))
    
    with console.status("[bold cyan]Waking up AI core...[/bold cyan]"):
        jarvis = JarvisBrain()
        watcher = SystemMonitor()
        watcher.start()

    if "--sentinel" in sys.argv:
        run_sentinel_loop(jarvis)
        return 

    while True:
        try:
            user_input = console.input("[bold green]Rana@Pop-OS:[/bold green] ")
            if user_input.lower() in ['exit', 'quit']:
                watcher.stop()
                sys.exit(0)
            if user_input.lower() == "sentinel":
                run_sentinel_loop(jarvis)
                continue
            with console.status("[bold cyan]Analyzing...[/bold cyan]"):
                response = jarvis.think(user_input)
            console.print(Panel(Markdown(response), title="Jarvis", border_style="cyan"))
        except KeyboardInterrupt:
            watcher.stop()
            sys.exit(0)
        
        # Inside main.py
        try:
            response = jarvis.think(directive)
        except Exception as e:
            if "429" in str(e):
                console.print("[bold orange]FAILOVER: Gemini Quota hit. Switching to Groq Llama-3.1...[/bold orange]")
        response = groq_brain.think(directive)

if __name__ == "__main__":
    main()