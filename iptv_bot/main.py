# main.py

import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from iptv_class import IPTV

iptv = IPTV()
BOT_TOKEN = os.getenv("BOT_TOKEN")


# ---------- Telegram Bot ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 歡迎使用 IPTV Bot！\n輸入 /m3u 取得 M3U 播放清單")

async def m3u(update: Update, context: ContextTypes.DEFAULT_TYPE):
    playlist = iptv.liveContent("dummy")
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(playlist)
    await update.message.reply_document(document=open("playlist.m3u", "rb"))

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("m3u", m3u))
    print("🤖 Telegram Bot is running...")
    app.run_polling()


# ---------- Fake HTTP Server ----------
class FakeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"Received GET request from {self.client_address}")
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"This is a fake IPTV HTTP server response.")

    def log_message(self, format, *args):
        return  # 靜音日誌

def run_fake_server(port=8080):
    server = HTTPServer(("0.0.0.0", port), FakeHandler)
    print(f"🌐 Fake server running on http://localhost:{port}")
    server.serve_forever()


# ---------- Main ----------
if __name__ == '__main__' :
    # 建立 HTTP Server 的執行緒
    server_thread = threading.Thread(target=run_fake_server, args=(8080,))
    server_thread.daemon = True
    server_thread.start()

    # 執行 Telegram Bot
    run_bot()
