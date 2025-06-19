import sqlite3
from pathlib import Path

DB_PATH = Path("data.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS credentials (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
            """)
        conn.commit()

def get_credentials(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM credentials WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return {"username": row[0], "password": row[1]}
        return None

def save_credentials(user_id, username, password):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "REPLACE INTO credentials (user_id, username, password) VALUES (?, ?, ?)",
            (user_id, username, password)
        )
        conn.commit()