from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, MessageHandler, filters, CommandHandler, Application

import logging
import os

TOKEN = os.getenv("BOT_TOKEN", "8180865453:AAHC4o41bqHKGmV2-WPVAPFF6SxE2vAkx80")  # Replace with your actual token or set as env var
bot = Bot(token=TOKEN)

app = Flask(__name__)

# Logging for debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"


@app.route("/")
def home():
    return "Bot is running."


def start(update: Update, context):
    update.message.reply_text("Hello! Send me anything and I'll echo it back.")


def echo(update: Update, context):
    update.message.reply_text(update.message.text)


if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    dispatcher = application.dispatcher

    # Set webhook if running on production
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g., "https://your-app.onrender.com"
    if WEBHOOK_URL:
        bot.set_webhook(f"{WEBHOOK_URL}/webhook/{TOKEN}")

    app.run(debug=True, port=5000)


# Static dictionary of movies/series and their URLs
MEDIA = {
    "Movies": {
        "Death Of A Unicorn": "https://t.me/+nEYMf9yrZvI5M2Q8",
        "Havoc": "https://t.me/+Ijh6aeYphsJlY2M0",
        "Final Destination Bloodlines": "https://t.me/+2K3Huw-P71ViYWVk",
        "Tin Soldier": "https://t.me/+NeuaDch01843ZjQ0",
        "The Ugly Stepsister": "https://t.me/+uyPbyZvgAPsxMmRk",
        "Summer Of 65": "https://t.me/+qoeTn1QRb7owZjY0",
        "Black Bag": "https://t.me/+ncyObRFbjC0yYmNk",
        "Warfare": "https://t.me/+nOAVzNufDQo2ODBk",
        "Captain America Brave New World": "https://t.me/+6Vunqj05DpFhMTI8",
        "In The Lost Lands": "https://t.me/+4cOW6Nc9aVlhZmJk",
    },
    "Series": {
        "MobLand S01": "https://t.me/+kZThd8DayxBiZDNk",
        "Your Friends And Neighbours S01": "https://t.me/+aAhGgya9SsxiYjdk",
        "Prime Target S01": "https://t.me/+ZbOhA41wV6BhYzM0",
        "Georgies & Mandy's First Marriage S01": "https://t.me/+wekh7LvnOF4yOWVk",
        "All The Queen's Men - S1": "https://t.me/+3jQswFBaq1JhNWI0",
        "All The Queen's Men - S2": "https://t.me/+M3Vga9SZgjsxNGE0"
    }
}

# Configure logging to file for user searches and errors
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log'  # All logs will be written to bot.log
)
logger = logging.getLogger(__name__)

def start(update, context):
    """Handle the /start command: send a welcome message with usage instructions."""
    user = update.effective_user.first_name
    message = (
        f"Hi {user}! 👋\n\n"
        "I am a Movie Search Bot. Send me any movie or series name (or part of it), "
        "and I'll find matching titles with links for you."
    )
    update.message.reply_text(message)

def search_movies(update, context):
    """Handle text messages: search the MOVIES dictionary and reply with inline buttons."""
    query = update.message.text.strip()
    user_id = update.effective_user.id
    logger.info("User %s searched for query: '%s'", user_id, query)

    # Find matching titles (case-insensitive, substring match)
    query_lower = query.lower()
    matches = []
    for title, url in MOVIES.items():
        if query_lower in title.lower():
            matches.append((title, url))

    if matches:
        # Create an inline keyboard with one button per match
        keyboard = []
        for title, url in matches:
            button = InlineKeyboardButton(text=title, url=url)
            keyboard.append([button])
        reply_markup = InlineKeyboardMarkup(keyboard)

        response_text = f"Found {len(matches)} result(s) for '{query}':"
        update.message.reply_text(response_text, reply_markup=reply_markup)
    else:
        update.message.reply_text(f"No matches found for '{query}'. Please try a different keyword.")

def handle_error(update, context):
    """Log any errors that occur during update processing."""
    logger.error("Error handling update. Update data: %s\nError: %s", update, context.error)

# Register handlers with the dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, search_movies))
dispatcher.add_error_handler(handle_error)

# Webhook route to receive updates from Telegram
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook_handler():
    """
    This endpoint is set as the Telegram webhook.
    It receives POST requests from Telegram containing update data in JSON form.
    """
    try:
        # Parse the incoming update
        update = Update.de_json(request.get_json(force=True), bot)
        # Process the update through dispatcher
        dispatcher.process_update(update)
    except Exception as e:
        # In case of error, log it and abort the request (Telegram will retry)
        logger.exception("Failed to process incoming Telegram update.")
        abort(400)
    return 'OK'  # Respond with 200 OK to Telegram

if __name__ == "__main__":
    # Optionally, set webhook here if not done manually:
    # bot.set_webhook(f"https://<your-render-app-name>.onrender.com/webhook/{TOKEN}")
    # Run Flask development server (not used in production on Render)
    app.run(host='0.0.0.0', port=5000)
