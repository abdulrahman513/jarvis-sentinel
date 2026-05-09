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

    # monitor.py - Add this at the end of your block_ip logic
    def notify_dashboard(ip_address, lat, lon):
        with open("/tmp/jarvis_event.json", "w") as f:
         json.dump({"ip": ip_address, "lat": lat, "lon": lon}, f)    

    def stop(self):
        self.running = False