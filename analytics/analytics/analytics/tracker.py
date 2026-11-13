# analytics/tracker.py
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "analytics.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            status TEXT,
            tone TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_post(content, status="generated", tone="professional"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO posts (content, status, tone, created_at) VALUES (?, ?, ?, ?)",
        (content, status, tone, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    print(f"✅ Post saved (ID: {cursor.lastrowid})")

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM posts")
    total = cursor.fetchone()[0]
    conn.close()
    return {"total_posts": total}

init_db()