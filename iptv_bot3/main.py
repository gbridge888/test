import os
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters
)
from database import init_db
from iptv_manager import IPTVManager

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
iptv = IPTVManager()

# 初始化 Telegram Bot 應用
application = Application.builder().token(TOKEN).build()
bot = Bot(token=TOKEN)

# 初始化 FastAPI App
app = FastAPI()
init_db()

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 歡迎使用 IPTV Token Bot，請輸入 /gettoken 取得驗證碼。")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📘 說明：\n"
        "/gettoken - 產生驗證碼\n"
        "輸入驗證碼 - 回傳 IPTV 連結（有效 120 小時）"
    )

async def gettoken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = iptv.generate_token(update.effective_user.id)
    await update.message.reply_text(
        f"🔑 驗證碼為：`{token}`\n請輸入此驗證碼取得 IPTV 連結。",
        parse_mode="Markdown"
    )

async def handle_token_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        link = f"https://yourdomain.com/get.php?username={username}&password={password}&type=m3u_plus"
        await update.message.reply_text(
            f"✅ IPTV 連結：\n`{link}`\n\n有效至：{expires}",
            parse_mode="Markdown"
        )

# 加入 handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("gettoken", gettoken))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_token_input))

# Webhook 通知處理（FastAPI）
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return {"status": "ok"}

# 設定 Webhook（Render 啟動時呼叫）
@app.on_event("startup")
async def startup():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)

# 運行伺服器（本地測試用）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))