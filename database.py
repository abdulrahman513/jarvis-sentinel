# database.py
import sqlite3
import os

DB_PATH = "/home/rana/jarvis-sentinel/jarvis_sentinel.db"

def init_db():
    """Initializes all tables for the J.A.R.V.I.S. SIEM suite."""
    conn = sqlite3.connect(DB_PATH)
    # Enable WAL mode for stable concurrent access between Sentinel and Dashboard
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    
    # 1. Incidents Table: The long-term log of every attack
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            intel TEXT,
            location TEXT,
            pcap_path TEXT,
            summary_path TEXT,
            action_taken TEXT,
            brain_analysis TEXT
        )
    ''')
    
    # 2. Persistent Blacklist Table: Ensures blocks survive reboots
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blacklist (
            ip_address TEXT PRIMARY KEY,
            blocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            reason TEXT
        )
    ''')

    # 3. Chat History Table: Persistent memory for the Tactical AI Interface
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            role TEXT,
            message TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# --- CHAT MEMORY FUNCTIONS ---

def save_chat(role, message):
    """Saves a message to the persistent chat history."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO chat_history (role, message) VALUES (?, ?)", (role, message))
    conn.commit()
    conn.close()

def get_chat_history(limit=25):
    """Retrieves the last X messages for the Dashboard chat window."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Fetch in order to maintain conversation flow
    cursor.execute("SELECT role, message FROM chat_history ORDER BY timestamp ASC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- INCIDENT & STATS FUNCTIONS ---

def get_recent_incidents(limit=30):
    """Fetches the latest threats for the Intelligence Queue."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidents ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_db_stats():
    """Calculates counts for the Dashboard Metric Tiles."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM incidents")
    total_incidents = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM blacklist")
    total_blocked = cursor.fetchone()[0]
    conn.close()
    return {"incidents": total_incidents, "blocked": total_blocked}

def get_report_stats():
    """Aggregates data for the AI-generated Management Reports."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), intel FROM incidents GROUP BY intel")
    summary = cursor.fetchall()
    conn.close()
    return summary

# --- DEFENSE FUNCTIONS ---

def add_to_blacklist(ip, reason="Auth Failure"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO blacklist (ip_address, reason) VALUES (?, ?)", (ip, reason))
    conn.commit()
    conn.close()

def is_blacklisted(ip):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM blacklist WHERE ip_address = ?", (ip,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def log_incident(ip, intel, location, pcap, summary, action, analysis):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO incidents (ip_address, intel, location, pcap_path, summary_path, action_taken, brain_analysis)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (ip, intel, location, pcap, summary, action, analysis))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("[SYSTEM] Database Core Upgraded: All tables active.")