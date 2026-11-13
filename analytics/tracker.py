import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "analytics.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            status TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_post(content, status="generated"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO posts (content, status, created_at) VALUES (?, ?, ?)",
        (content, status, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    print(f"✅ Post saved to database (ID: {cursor.lastrowid})")

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM posts")
    total = cursor.fetchone()[0]
    conn.close()
    return {"total_posts": total}

# Initialize database
init_db()

if __name__ == "__main__":
    print(f"📊 Total posts: {get_stats()['total_posts']}")