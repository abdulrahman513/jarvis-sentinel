import shield
import reporter
import re
import sys
import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from brain import JarvisBrain
from groq_brain import GroqBrain
from monitor import SystemMonitor

console = Console()

def ensure_root_privileges():
    if os.geteuid() != 0:
        args = ['sudo', sys.executable] + sys.argv
        os.execlpe('sudo', *args, os.environ)

def run_sentinel_loop(jarvis, groq_brain):
    console.print("[bold yellow][SYSTEM] J.A.R.V.I.S. Active Stream Monitor engaged.[/bold yellow]")
    while True:
        try:
            for log_entry in shield.listen_to_logs_live():
                ip_match = re.search(r'from (\d+\.\d+\.\d+\.\d+)', log_entry)
                target_ip = ip_match.group(1) if ip_match else "Unknown"

                if target_ip in shield.RECENTLY_BLOCKED:
                    continue

                console.print(f"\n[bold red][ALERT][/bold red] New unique threat: {target_ip}")
                directive = f"NEW LOG: {log_entry}\nAnalyze this. If foreign attack, block and lock."
                
                try:
                    with console.status("[bold cyan]Consulting Gemini...[/bold cyan]"):
                        response = jarvis.think(directive)
                except Exception as e:
                    if "429" in str(e):
                        console.print("[bold orange]FAILOVER: Gemini limit hit. Using Groq...[/bold orange]")
                        response = groq_brain.think(directive)
                    else:
                        response = f"Brain Error: {e}"

                console.print(Panel(Markdown(response), title="Jarvis (Live Response)", border_style="red"))
        except Exception as e:
            console.print(f"[bold red]Sentinel error: {e}. Restarting...[/bold red]")
            time.sleep(5)

def main():
    ensure_root_privileges()
    console.print(Panel.fit("[bold blue]J.A.R.V.I.S. Blue Team Interface[/bold blue]\n[green]Status: ACTIVE[/green]"))
    
    with console.status("[bold cyan]Waking up AI cores...[/bold cyan]"):
        jarvis = JarvisBrain()
        groq_brain = GroqBrain()
        watcher = SystemMonitor()
        watcher.start()

    if "--report" in sys.argv:
        reporter.generate_security_report()
        watcher.stop()
        return    

    if "--sentinel" in sys.argv:
        run_sentinel_loop(jarvis, groq_brain)
        return 

    while True:
        try:
            user_input = console.input("[bold green]Rana@Pop-OS:[/bold green] ")
            if user_input.lower() in ['exit', 'quit']:
                watcher.stop()
                sys.exit(0)
            
            if user_input.lower() == "sentinel":
                run_sentinel_loop(jarvis, groq_brain)
                continue

            with console.status("[bold cyan]Analyzing...[/bold cyan]"):
                try:
                    response = jarvis.think(user_input)
                except Exception as e:
                    if "429" in str(e):
                        response = groq_brain.think(user_input)
                    else:
                        response = f"Error: {e}"
            
            console.print(Panel(Markdown(response), title="Jarvis", border_style="cyan"))
        except KeyboardInterrupt:
            watcher.stop()
            sys.exit(0)

if __name__ == "__main__":
    main()