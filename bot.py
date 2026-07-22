from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋\nلینک اینستاگرام را ارسال کنید تا دانلود شود."
    )

async def download_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "instagram.com" not in url:
        await update.message.reply_text("لطفا یک لینک معتبر اینستاگرام ارسال کنید.")
        return

    await update.message.reply_text("⏳ در حال دانلود...")

    try:
        ydl_opts = {
            "outtmpl": "downloaded.%(ext)s",
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, "rb") as f:
            await update.message.reply_video(f)

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"خطا: {e}")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_instagram))

    app.run_polling()

if __name__ == "__main__":
    main()
