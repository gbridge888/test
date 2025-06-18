from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from iptv_class import IPTV
import os

iptv = IPTV()
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 歡迎使用 IPTV Bot！\n輸入 /m3u 取得 M3U 播放清單")

async def m3u(update: Update, context: ContextTypes.DEFAULT_TYPE):
    playlist = iptv.liveContent("dummy")
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(playlist)
    await update.message.reply_document(document=open("playlist.m3u", "rb"))

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("m3u", m3u))
    app.run_polling()
