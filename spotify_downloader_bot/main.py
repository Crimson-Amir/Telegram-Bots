from private import bot_token
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import spotipy


def check_join():
    pass


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello')


app = ApplicationBuilder().token(bot_token).build()
app.add_handler(CommandHandler('start', start))
app.run_polling()