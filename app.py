import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8180865453:AAHC4o41bqHKGmV2-WPVAPFF6SxE2vAkx80")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://webhook.site/2399bcae-cf4e-4c9a-b717-af8d59921835")

# Flask setup
app = Flask(__name__)

# Telegram bot application
telegram_app = Application.builder().token(BOT_TOKEN).updater(None).build()

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm your bot. Just send me something!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You said: {update.message.text}")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Webhook route
@app.route("/webhook", methods=["POST"])
async def webhook():
    update_data = request.get_json(force=True)
    update = Update.de_json(update_data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK"

# Healthcheck route
@app.route("/", methods=["GET"])
def index():
    return "Bot is running."

# Setup webhook once before running Flask
async def setup():
    await telegram_app.bot.set_webhook(WEBHOOK_URL)

def run():
    asyncio.run(setup())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

# Run
if __name__ == "__main__":
    run()
