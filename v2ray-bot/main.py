from telegram.ext import (Updater, CommandHandler)
from private import telegram_bot_token
from bot_start import bot_start
from database import create_database


def main():
    updater = Updater(telegram_bot_token)
    create_database()
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', bot_start))

    updater.start_polling(1)
    updater.idle()


if __name__ == '__main__':
    main()
