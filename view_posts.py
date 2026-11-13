import sqlite3
import json
from pathlib import Path
from datetime import datetime

def get_columns(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]

def view_all_posts():
    print("\n" + "=" * 60)
    print("📁 ALL SAVED POSTS")
    print("=" * 60)

    db_path = Path("analytics/analytics.db")
    if not db_path.exists():
        print("❌ Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get columns
    columns = get_columns(cursor, "posts")
    print(f"📋 Columns in posts table: {columns}")
    
    # Build select columns (only existing ones)
    select_cols = ["id", "content", "status", "created_at"]
    extra_cols = []
    for col in ["tone", "model_used"]:
        if col in columns:
            extra_cols.append(col)
    select_cols = ["id", "content", "status"] + extra_cols + ["created_at"]
    
    query = f"SELECT {', '.join(select_cols)} FROM posts ORDER BY id DESC"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    print(f"\n📊 DATABASE ({len(rows)} posts):")
    print("-" * 40)
    for row in rows:
        # map to dict by column order
        data = dict(zip(select_cols, row))
        print(f"\nID: {data['id']}")
        print(f"Status: {data['status']}")
        if 'tone' in data:
            print(f"Tone: {data['tone']}")
        if 'model_used' in data:
            print(f"Model: {data['model_used']}")
        print(f"Created: {data['created_at']}")
        print(f"Content: {data['content'][:150]}...")
        print("-" * 30)
    
    # Also check posts folder and logs...