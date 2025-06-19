
import os
import random
import string
from database import get_credentials, save_credentials

class IPTVManager:
    def __init__(self):
        self.base_url = os.getenv("IPTV_DOMAIN", "https://iptv.mydiver.eu.org")
        self.prefix = os.getenv("IPTV_USERNAME_PREFIX", "tg_")
        self.pass_length = int(os.getenv("IPTV_PASSWORD_LENGTH", 10))

    def _generate_password(self):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=self.pass_length))

    def create_or_get_credentials(self, user_id: int):
        creds = get_credentials(user_id)
        if creds:
            return {
                "username": creds["username"],
                "password": creds["password"],
                "m3u_link": f"{self.base_url}/get.php?username={creds['username']}&password={creds['password']}&type=m3u_plus"
            }

        username = f"{self.prefix}{user_id}"
        password = self._generate_password()
        save_credentials(user_id, username, password)

        return {
            "username": username,
            "password": password,
            "m3u_link": f"{self.base_url}/get.php?username={username}&password={password}&type=m3u_plus"
        }

    def get_credentials(self, user_id: int):
        creds = get_credentials(user_id)
        if creds:
            return {
                "username": creds["username"],
                "password": creds["password"],
                "m3u_link": f"{self.base_url}/get.php?username={creds['username']}&password={creds['password']}&type=m3u_plus"
            }
        return None
