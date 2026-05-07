# monitor.py
import psutil
import time
import threading
from rich.console import Console

console = Console()

class SystemMonitor:
    def __init__(self):
        self.running = False

    def _watch(self):
        """Internal background loop looking for anomalies."""
        while self.running:
            # Check for abnormal CPU usage (e.g., above 90%)
            cpu_usage = psutil.cpu_percent(interval=1)
            if cpu_usage > 90.0:
                console.print(f"\n[bold red][ALERT] High CPU Usage Detected: {cpu_usage}%![/bold red]")
                console.print("[yellow]Type 'Jarvis, check running processes' to investigate.[/yellow]\n> ", end="")
            
            # Sleeps for 10 seconds before checking again to save resources
            time.sleep(10)

    def start(self):
        """Starts the monitoring thread."""
        self.running = True
        self.thread = threading.Thread(target=self._watch, daemon=True)
        self.thread.start()

    def stop(self):
        """Stops the monitoring thread."""
        self.running = False