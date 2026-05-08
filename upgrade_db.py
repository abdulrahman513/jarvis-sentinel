import sqlite3

DB_PATH = "/home/rana/jarvis-sentinel/jarvis_sentinel.db"

def upgrade():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Add a column for the AI's analysis notes
        cursor.execute('ALTER TABLE incidents ADD COLUMN brain_analysis TEXT')
        conn.commit()
        print("Database upgraded: Column 'brain_analysis' added.")
    except sqlite3.OperationalError:
        print("Column already exists. Skipping.")
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade()
    