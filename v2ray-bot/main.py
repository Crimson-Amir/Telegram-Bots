from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler)
from private import telegram_bot_token
from bot_start import bot_start
from database import create_database
from tasks import not_ready_yet, buy_service
from admin_task import admin_add_update_inbound, add_service, all_service, del_service


def main():
    updater = Updater(telegram_bot_token)
    create_database()
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', bot_start))
    dp.add_handler(CommandHandler('help', bot_start))
    dp.add_handler(CommandHandler('add_inbound', admin_add_update_inbound))
    dp.add_handler(CommandHandler('add_service', add_service))
    dp.add_handler(CommandHandler('all_service', all_service))
    dp.add_handler(CommandHandler('del_service', del_service))

    dp.add_handler(CallbackQueryHandler(buy_service, pattern='buy_service'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='settings'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='my_service'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='get_test_service'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='guidance'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='support'))

    updater.start_polling(1)
    updater.idle()


if __name__ == '__main__':
    main()
