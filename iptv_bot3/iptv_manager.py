import sqlite3
import random
import string
from datetime import datetime, timedelta

TOKEN_EXPIRY_HOURS = 120

class IPTVManager:
    def __init__(self, db_name="iptv.db"):
        self.db_name = db_name

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def generate_token(self, telegram_id):
        token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        username = f"tg_{token}"
        password = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        with self._connect() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (telegram_id, token, username, password) VALUES (?, ?, ?, ?)",
                      (telegram_id, token, username, password))
            conn.commit()
        return token

    def get_user_by_token(self, token):
        with self._connect() as conn:
            c = conn.cursor()
            c.execute("SELECT username, password, created_at FROM users WHERE token=?", (token,))
            row = c.fetchone()
            if not row:
                return None
            username, password, created_at = row
            created_time = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            if datetime.now() - created_time > timedelta(hours=TOKEN_EXPIRY_HOURS):
                return "expired"
            return {
                "username": username,
                "password": password,
                "expires": created_time + timedelta(hours=TOKEN_EXPIRY_HOURS)
            }
