from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("8180865453:AAHC4o41bqHKGmV2-WPVAPFF6SxE2vAkx80")  # Set your bot token in environment variables

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://webhook.site/2399bcae-cf4e-4c9a-b717-af8d59921835")

# Mock database of media content
MEDIA = {
    "movies": [
        {"Death Of A Unicorn": "Death Of A Unicorn", "url": "https://t.me/+nEYMf9yrZvI5M2Q8"},
        {"title": "Interstellar", "url": "https://example.com/interstellar.mp4"},
        {"Death Of A Unicorn": "https://t.me/+nEYMf9yrZvI5M2Q8"},
        {"Havoc": "https://t.me/+Ijh6aeYphsJlY2M0"},
        {"Final Destination Bloodlines": "https://t.me/+2K3Huw-P71ViYWVk"},
        {"Tin Soldier": "https://t.me/+NeuaDch01843ZjQ0"},
        {"The Ugly Stepsister": "https://t.me/+uyPbyZvgAPsxMmRk"},
        {"Summer Of 65": "https://t.me/+qoeTn1QRb7owZjY0"},
        {"Black Bag": "https://t.me/+ncyObRFbjC0yYmNk"},
        {"Warfare": "https://t.me/+nOAVzNufDQo2ODBk"},
        {"Captain America Brave New World": "https://t.me/+6Vunqj05DpFhMTI8"},
        {"In The Lost Lands": "https://t.me/+4cOW6Nc9aVlhZmJk"},
    ],
    "series": [
        {
            "title": "Stranger Things",
            "seasons": {
                "Season 1": ["https://example.com/st1e1.mp4", "https://example.com/st1e2.mp4"],
                "Season 2": ["https://example.com/st2e1.mp4"]
            }
        }
    ]
}

# ---------------------- TELEGRAM BOT LOGIC ----------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎬 Movies", callback_data="movies")],
        [InlineKeyboardButton("📺 Series", callback_data="series")]
    ]
    await update.message.reply_text("Welcome! Choose an option:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip().lower()
    results = []

    # Search movies
    for movie in MEDIA["movies"]:
        if query in movie["title"].lower():
            results.append(f"🎬 {movie['title']} - [Watch]({movie['url']})")

    # Search series
    for series in MEDIA["series"]:
        if query in series["title"].lower():
            results.append(f"📺 {series['title']} (Series)")

    if results:
        await update.message.reply_text("\n".join(results), parse_mode="Markdown")
    else:
        await update.message.reply_text("No results found.")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "movies":
        keyboard = [
            [InlineKeyboardButton(movie["title"], url=movie["url"])]
            for movie in MEDIA["movies"]
        ]
        await query.edit_message_text("🎬 Movies:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "series":
        keyboard = [
            [InlineKeyboardButton(series["title"], callback_data=f"series_{i}")]
            for i, series in enumerate(MEDIA["series"])
        ]
        await query.edit_message_text("📺 Series:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("series_"):
        index = int(query.data.split("_")[1])
        series = MEDIA["series"][index]
        season_keyboard = [
            [InlineKeyboardButton(season, callback_data=f"season_{index}_{season}")]
            for season in series["seasons"]
        ]
        await query.edit_message_text(f"{series['title']} - Select Season:", reply_markup=InlineKeyboardMarkup(season_keyboard))

    elif query.data.startswith("season_"):
        _, series_index, season_name = query.data.split("_", 2)
        series = MEDIA["series"][int(series_index)]
        episodes = series["seasons"][season_name]
        episode_keyboard = [
            [InlineKeyboardButton(f"Episode {i+1}", url=ep_url)]
            for i, ep_url in enumerate(episodes)
        ]
        await query.edit_message_text(f"{series['title']} - {season_name}:", reply_markup=InlineKeyboardMarkup(episode_keyboard))


# ---------------------- DEPLOY ON FLASK ----------------------

@app.route('/')
def home():
    return 'Bot is running!'

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot.application.bot)
    bot.application.update_queue.put(update)
    return 'OK'

if __name__ == '__main__':
    application = Application.builder().token(BOT_TOKEN).build()

    # Telegram command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search))
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Save the bot instance for webhook
    bot = type("BotWrapper", (), {"application": application})
    app.run(debug=True, port=5000)

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
