import sqlite3

def init_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        token TEXT,
        username TEXT,
        password TEXT,
        expires TEXT
    )
    """)
    conn.commit()
    conn.close()

