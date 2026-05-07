import pandas as pd
import os
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table

console = Console()

# Unified Path to match your project folder
VAULT_DIR = "/home/rana/jarvis-sentinel/evidence_vault/"
LOG_FILE = os.path.join(VAULT_DIR, "jarvis_forensics.csv")

def generate_security_report():
    """Analyzes forensic logs and prints a Rich Table 'chart' to the terminal."""
    if not os.path.exists(LOG_FILE):
        return "[ERROR] No forensic logs found in vault. The sentinel must block an IP first."

    try:
        # Load the data - handling your specific CSV columns
        df = pd.read_csv(LOG_FILE, names=["Timestamp", "IP", "Intel", "Action", "Location"])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        week_ago = datetime.now() - timedelta(days=7)
        weekly_data = df[df['Timestamp'] >= week_ago].copy()

        if weekly_data.empty:
            return "Security audit complete: No incidents found in the last 7 days."

        total_incidents = len(weekly_data)
        top_offender = weekly_data['IP'].mode()[0]
        
        # Build the Visual Table (The "Chart")
        table = Table(title="J.A.R.V.I.S. Weekly Security Report", header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold white")
        
        table.add_row("Total Mitigations", str(total_incidents))
        table.add_row("Primary Attacker", f"[red]{top_offender}[/red]")
        table.add_row("Last Known Origin", weekly_data.iloc[-1]['Location'])
        
        console.print(table)

        return f"Report generated successfully. System mitigated {total_incidents} threats this week."

    except Exception as e:
        return f"Reporting Error: {str(e)}"

if __name__ == "__main__":
    generate_security_report()