import pandas as pd
import os
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Path must match your shield.py VAULT_DIR
VAULT_DIR = "/home/rana/jarvis-sentinel/evidence_vault/"
LOG_FILE = os.path.join(VAULT_DIR, "jarvis_forensics.csv")

def generate_security_report():
    """Reads the forensic CSV and generates a professional summary."""
    if not os.path.exists(LOG_FILE):
        console.print("[bold red][ERROR] No forensic logs found. Run the sentinel first.[/bold red]")
        return

    try:
        # 1. Load the data
        # Data format from shield.py: Timestamp, IP, Intel, Action [cite: 33]
        df = pd.read_csv(LOG_FILE, names=["Timestamp", "IP", "Intel", "Action"])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # 2. Filter for the last 7 days (Weekly Report)
        one_week_ago = datetime.now() - timedelta(days=7)
        weekly_df = df[df['Timestamp'] >= one_week_ago].copy()

        if weekly_df.empty:
            console.print(Panel("[yellow]No incidents recorded in the last 7 days. System is quiet.[/yellow]", title="J.A.R.V.I.S. Status"))
            return

        # 3. Analyze Patterns
        total_blocks = len(weekly_df)
        top_attacker = weekly_df['IP'].mode()[0]
        
        # Extract Risk Scores for a deeper summary [cite: 29]
        weekly_df['RiskScore'] = weekly_df['Intel'].str.extract(r'Risk Score: (\d+)%').astype(float)
        avg_risk = weekly_df['RiskScore'].mean()

        # 4. Display Professional Table
        table = Table(title=f"Security Incident Report ({one_week_ago.date()} to {datetime.now().date()})")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Analysis", style="magenta")

        table.add_row("Total Unauthorized Attempts Blocked", str(total_blocks))
        table.add_row("Primary Threat Actor (IP)", f"[red]{top_attacker}[/red]")
        table.add_row("Average Threat Confidence Score", f"{avg_risk:.2f}%")
        table.add_row("Forensic Evidence Location", VAULT_DIR)

        console.print(table)

        # 5. Save a "Management Ready" text file
        report_name = f"management_report_{datetime.now().strftime('%Y-%m-%d')}.txt"
        report_path = os.path.join(VAULT_DIR, report_name)
        
        with open(report_path, "w") as f:
            f.write(f"J.A.R.V.I.S. SENTINEL - WEEKLY SECURITY SUMMARY\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Mitigation Actions: {total_blocks}\n")
            f.write(f"Most Frequent Attacker: {top_attacker}\n")
            f.write(f"Average AbuseIPDB Risk Score: {avg_risk:.2f}%\n")
            f.write(f"Data Source: {LOG_FILE}\n")

        console.print(f"[bold green]✔ Management report generated: {report_path}[/bold green]")

    except Exception as e:
        console.print(f"[bold red][ERROR] Report generation failed: {e}[/bold red]")

if __name__ == "__main__":
    generate_security_report()