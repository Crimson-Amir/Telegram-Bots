from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler)
from private import telegram_bot_token
from bot_start import bot_start
from database import create_database
from tasks import not_ready_yet


def main():
    updater = Updater(telegram_bot_token)
    create_database()
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', bot_start))

    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='buy_service'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='settings'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='my_service'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='get_test_service'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='guidance'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='support'))


    updater.start_polling(1)
    updater.idle()


if __name__ == '__main__':
    main()
