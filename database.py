import sqlite3
import os

DB_PATH = "/home/rana/jarvis-sentinel/jarvis_sentinel.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    
    # 1. Incidents & Blacklist
    cursor.execute('''CREATE TABLE IF NOT EXISTS incidents (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, ip_address TEXT, intel TEXT, location TEXT, pcap_path TEXT, summary_path TEXT, action_taken TEXT, brain_analysis TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS blacklist (ip_address TEXT PRIMARY KEY, blocked_at DATETIME DEFAULT CURRENT_TIMESTAMP, reason TEXT)''')
    
    # 2. Chat Sessions & Messages
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, role TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

# --- SESSION LOGIC ---
def create_session(title="Tactical Interface Session"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_sessions (title) VALUES (?)", (title,))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def get_all_sessions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chat_sessions ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_session(session_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
    conn.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

def save_message(session_id, role, message):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO chat_messages (session_id, role, message) VALUES (?, ?, ?)", (session_id, role, message))
    conn.commit()
    conn.close()

def get_session_messages(session_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role, message FROM chat_messages WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- CORE LOGIC ---
def is_blacklisted(ip):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM blacklist WHERE ip_address = ?", (ip,))
    res = cursor.fetchone() is not None
    conn.close()
    return res

def get_recent_incidents(limit=30):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidents ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_to_blacklist(ip, reason="Manual Block"):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT OR IGNORE INTO blacklist (ip_address, reason) VALUES (?, ?)", (ip, reason))
    conn.commit()
    conn.close()

def log_incident(ip, intel, location, pcap, summary, action, analysis):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO incidents (ip_address, intel, location, pcap_path, summary_path, action_taken, brain_analysis) VALUES (?,?,?,?,?,?,?)", (ip, intel, location, pcap, summary, action, analysis))
    conn.commit()
    conn.close()

def get_report_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), intel FROM incidents GROUP BY intel")
    summary = cursor.fetchall()
    conn.close()
    return summary

if __name__ == "__main__":
    init_db()
    print("[SYSTEM] Multi-Session Database Online.")