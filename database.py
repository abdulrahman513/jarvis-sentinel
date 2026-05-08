# database.py
import sqlite3
import os

DB_PATH = "/home/rana/jarvis-sentinel/jarvis_sentinel.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    
    # Existing Incidents Table
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
    
    # NEW: Persistent Blacklist Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blacklist (
            ip_address TEXT PRIMARY KEY,
            blocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            reason TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

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
    print("[SYSTEM] Database & Blacklist Table Initialized.")