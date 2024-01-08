from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler)
from private import telegram_bot_token
from bot_start import bot_start, main_menu, send_main_message
from database import create_database
from tasks import not_ready_yet, buy_service, all_query_handler, payment_page, get_service_con, apply_card_pay
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

    dp.add_handler(CallbackQueryHandler(main_menu, pattern='main_menu'))
    dp.add_handler(CallbackQueryHandler(send_main_message, pattern='send_main_message'))
    dp.add_handler(CallbackQueryHandler(buy_service, pattern='select_server'))
    dp.add_handler(CallbackQueryHandler(payment_page, pattern=r'service_\d+'))
    dp.add_handler(get_service_con)

    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern=r'payment_by_wallet_\d+'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern=r'payment_by_crypto_\d+'))
    dp.add_handler(CallbackQueryHandler(apply_card_pay, pattern=r'accept_card_pay_\d+'))
    dp.add_handler(CallbackQueryHandler(apply_card_pay, pattern=r'refuse_card_pay_\d+'))
    dp.add_handler(CallbackQueryHandler(apply_card_pay, pattern=r'ok_card_pay_accept_\d+'))
    dp.add_handler(CallbackQueryHandler(apply_card_pay, pattern=r'ok_card_pay_refuse_\d+'))
    dp.add_handler(CallbackQueryHandler(apply_card_pay, pattern='cancel_pay'))


    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='settings'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='my_service'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='get_test_service'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='guidance'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='support'))
    dp.add_handler(CallbackQueryHandler(all_query_handler))

    updater.start_polling(1)
    updater.idle()


if __name__ == '__main__':
    main()
