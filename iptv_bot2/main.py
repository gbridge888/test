from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from iptv_manager import IPTVManager
from database import init_db
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

init_db()
iptv = IPTVManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 歡迎使用 Xtream Codes Proxy 機器人！請使用 /gettoken 開始。")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 可用命令:\n"
        "🔸 /gettoken - 取得播放清單\n"
        "🔸 /mycredentials - 查看帳密\n"
        "🔸 /status - 檢查伺服器\n"
        "🔸 /refresh - 重設連結"
    )

async def gettoken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    creds = iptv.create_or_get_credentials(update.effective_user.id)
    await update.message.reply_text(
        f"✅ 您的 M3U 播放連結：\n{creds['m3u_link']}\n\n"
        f"用戶名: {creds['username']}\n密碼: {creds['password']}"
    )

async def mycredentials(update: Update, context: ContextTypes.DEFAULT_TYPE):
    creds = iptv.get_credentials(update.effective_user.id)
    if creds:
        await update.message.reply_text(
            f"🔐 您的登入資訊：\n用戶名: {creds['username']}\n密碼: {creds['password']}\n\n🔗 {creds['m3u_link']}"
        )
    else:
        await update.message.reply_text("❌ 尚未產生過登入資訊，請使用 /gettoken")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ IPTV Proxy 目前狀態正常")

async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    creds = iptv.create_or_get_credentials(update.effective_user.id)
    await update.message.reply_text(f"🔄 已重設連結：\n{creds['m3u_link']}")

app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("gettoken", gettoken))
app.add_handler(CommandHandler("mycredentials", mycredentials))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("refresh", refresh))


# ----------- Fake HTTP Server -----------

def run_fake_http_server():
    class FakeHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/ping":
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"pong")
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            # 不打印访问日志，避免干扰
            return

    server_address = ("0.0.0.0", 8080)
    httpd = HTTPServer(server_address, FakeHandler)
    print("✅ Fake HTTP Server running at http://0.0.0.0:8080")
    httpd.serve_forever()


if __name__ == "__main__":
    # 以守护线程启动 Fake HTTP Server
    threading.Thread(target=run_fake_http_server, daemon=True).start()

    # 启动 Telegram Bot 主循环
    print("🤖 Telegram Bot 正在运行...")
    app.run_polling()

