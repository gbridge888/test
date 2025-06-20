import sqlite3
import random
import string
from datetime import datetime, timedelta

class IPTVManager:
    def __init__(self, db_path="data.db"):
        self.db_path = db_path

    def generate_token(self, telegram_id: int) -> str:
        token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        username = f"tg_{token}"
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        expires = (datetime.utcnow() + timedelta(hours=120)).strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO users (telegram_id, token, username, password, expires) VALUES (?, ?, ?, ?, ?)",
                  (telegram_id, token, username, password, expires))
        conn.commit()
        conn.close()
        return token

    def get_user_by_token(self, token: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE token=?", (token,))
        row = c.fetchone()
        conn.close()

        if not row:
            return None
        expires = datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S")
        if datetime.utcnow() > expires:
            return "expired"

        return {
            "id": row[0],
            "telegram_id": row[1],
            "token": row[2],
            "username": row[3],
            "password": row[4],
            "expires": expires
        }

    def get_user_by_auth(self, username: str, password: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        row = c.fetchone()
        conn.close()

        if not row:
            return None

        return {
            "id": row[0],
            "telegram_id": row[1],
            "token": row[2],
            "username": row[3],
            "password": row[4],
            "expires": datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S")
        }

