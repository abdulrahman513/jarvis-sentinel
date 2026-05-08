import psutil
import time
import threading
from rich.console import Console

console = Console()

class SystemMonitor:
    def __init__(self):
        self.running = False

    def _watch(self):
        while self.running:
            cpu = psutil.cpu_percent(interval=1)
            if cpu > 90.0:
                console.print(f"\n[bold red][ALERT] Critical CPU: {cpu}%![/bold red]")
            time.sleep(20) # Optimized check-interval for background daemon

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._watch, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False