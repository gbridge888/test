import os
import sqlite3
import logging
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, Response
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters
)
from datetime import datetime
from iptv_manager import IPTVManager
from database import init_db
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
iptv = IPTVManager()

application = Application.builder().token(TOKEN).build()
app = FastAPI()
init_db()

@app.get("/")
def root():
    return {"status": "ok", "message": "IPTV Telegram Bot Server running"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 歡迎使用 IPTV Token Bot，請輸入 /gettoken 取得驗證碼。")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📘 *IPTV Bot 指令說明*\n\n"
        "🔹 `/start` - 開始使用本機器人\n"
        "🔹 `/gettoken` - 產生 IPTV 驗證碼（有效 120 小時）\n"
        "🔹 `/status` - 查詢目前 IPTV 狀態（是否過期、IPTV 連結等）\n"
        "🔹 `/help` - 查看指令說明\n\n"
        "🔸 取得驗證碼後，請直接貼上驗證碼，機器人會回傳您的專屬 IPTV 連結。",
        parse_mode="Markdown"
    )

async def gettoken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    valid_count = iptv.count_valid_users()
    if valid_count >= 50:
        await update.message.reply_text("⚠️ 使用人數已達上限（50 人），請稍後再試。")
        return

    token = iptv.generate_token(update.effective_user.id)
    await update.message.reply_text(
        f"🔑 驗證碼為：`{token}`\n請輸入此驗證碼取得 IPTV 連結。",
        parse_mode="Markdown"
    )

async def handle_token_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    token = update.message.text.strip()
    result = iptv.get_user_by_token(token)
    if result is None:
        await update.message.reply_text("❌ 無效的 token")
    elif result == "expired":
        await update.message.reply_text("⏰ token 已過期，請重新取得。")
    else:
        username = result['username']
        password = result['password']
        expires = result['expires'].strftime('%Y-%m-%d %H:%M')
        link = f"https://iptv888.zabc.net/get.php?username={username}&password={password}&type=m3u_plus"
        await update.message.reply_text(
            f"✅ IPTV 連結：\n`{link}`\n\n有效至：{expires}",
            parse_mode="Markdown"
        )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT username, password, expires FROM users WHERE telegram_id=? ORDER BY id DESC LIMIT 1", (user_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        await update.message.reply_text("❌ 尚未產生過驗證碼，請使用 /gettoken 產生。")
        return

    username, password, expires_str = row
    expires = datetime.strptime(expires_str, "%Y-%m-%d %H:%M:%S")
    now = datetime.utcnow()
    remaining = expires - now

    if remaining.total_seconds() < 0:
        status = "❌ 已過期"
    else:
        days = remaining.days
        hours = remaining.seconds // 3600
        status = f"✅ 有效 ({days} 天 {hours} 小時)"

    iptv_url = f"https://iptv888.zabc.net/get.php?username={username}&password={password}&type=m3u_plus"

    await update.message.reply_text(
        f"📊 使用者狀態：\n\n"
        f"👤 使用者名稱：`{username}`\n"
        f"🔐 密碼：`{password}`\n"
        f"⏳ 過期時間：{expires.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"📅 狀態：{status}\n\n"
        f"▶️ IPTV 連結：\n`{iptv_url}`",
        parse_mode="Markdown"
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error("❗️ Uncaught Exception", exc_info=context.error)

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("gettoken", gettoken))
application.add_handler(CommandHandler("status", status_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_token_input))
application.add_error_handler(error_handler)

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"status": "ok"}

@app.get("/get.php")
async def get_php(request: Request):
    username = request.query_params.get("username")
    password = request.query_params.get("password")
    stream_type = request.query_params.get("type", "m3u")

    if not username or not password:
        return Response(content="# Missing username or password", media_type="application/x-mpegURL", status_code=400)

    user = iptv.get_user_by_auth(username, password)
    if user is None:
        return Response(content="# Invalid username or password", media_type="application/x-mpegURL", status_code=403)

    expires: datetime = user["expires"]
    if datetime.utcnow() > expires:
        return Response(content="# Token expired", media_type="application/x-mpegURL", status_code=403)

    redirect_url = f"https://iptv.mydiver.eu.org/get.php?username=tg_92xht45u&password=d928ik7qx9du&type=m3u_plus"
    return RedirectResponse(url=redirect_url)

@app.on_event("startup")
async def startup():
    await application.initialize()
    await application.bot.initialize()
    await application.bot.get_me()
    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.bot.set_webhook(WEBHOOK_URL)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

