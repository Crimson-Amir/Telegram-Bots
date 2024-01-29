from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler)
from private import telegram_bot_token
from bot_start import bot_start, main_menu, send_main_message
from database import create_database

from tasks import (buy_service, all_query_handler, payment_page, get_service_con, apply_card_pay,
                   my_service, create_file_and_return, server_detail_customer, personalization_service,
                   personalization_service_lu, apply_card_pay_lu, get_service_con_per, get_free_service, help_sec,
                   show_help, support, setting, change_notif, start_timer, financial_transactions,
                   wallet_page, financial_transactions_wallet, payment_page_upgrade, buy_credit_volume,
                   pay_way_for_credit, credit_charge, apply_card_pay_credit, pay_from_wallet, remove_service,
                   check_all_configs, remove_service_from_db, rate_service, get_pay_file,
                   admin_reserve_service, people_ask, pay_per_use, pay_per_use_calculator)

from utilities import not_ready_yet, just_for_show

from admin_task import (admin_add_update_inbound, add_service, all_service, del_service, run_in_system,
                        say_to_every_one, message_to_user, clear_depleted_service, say_to_customer_of_server,
                        add_credit_to_server_customer_wallet, add_credit_to_customer)

from private import ADMIN_CHAT_ID
import requests
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

telegram_bot_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
requests.post(telegram_bot_url, data={'chat_id': ADMIN_CHAT_ID, 'text':'🟠 THE BOT STARTED'})
create_database()


def main():
    updater = Updater(telegram_bot_token)
    dp = updater.dispatcher

    commands = {
        'start': bot_start,
        'help': bot_start,
        'add_inbound': admin_add_update_inbound,
        'check_all_configs': check_all_configs,
        'add_service': add_service,
        'all_service': all_service,
        'del_service': del_service,
        'start_timer': start_timer,
        'run_in_system': run_in_system,
        'say_to_every_one': say_to_every_one,
        'admin_reserve_service': admin_reserve_service,
        'message_to_user': message_to_user,
        'clear_depleted_service': clear_depleted_service,
        'say_to_customer_of_server': say_to_customer_of_server,
        'add_credit_to_customer_wallet': add_credit_to_server_customer_wallet,
        'add_credit_to_customer': add_credit_to_customer,
    }

    for key, value in commands.items():
        dp.add_handler(CommandHandler(key, value))

    dp.add_handler(get_service_con)
    dp.add_handler(get_service_con_per)
    dp.add_handler(credit_charge)

    dp.add_handler(CallbackQueryHandler(rate_service, pattern=r'rate_(.*)'))
    dp.add_handler(CallbackQueryHandler(people_ask, pattern=r'ask_(.*)'))
    dp.add_handler(CallbackQueryHandler(remove_service_from_db, pattern=r'remove_service_from_db_(.*)'))
    dp.add_handler(CallbackQueryHandler(pay_from_wallet, pattern=r'accept_wallet_upgrade_pay_\d+'))
    dp.add_handler(CallbackQueryHandler(pay_from_wallet, pattern=r'payment_by_wallet_\d+'))
    dp.add_handler(CallbackQueryHandler(pay_from_wallet, pattern=r'accept_wallet_pay_\d+'))
    dp.add_handler(CallbackQueryHandler(pay_from_wallet, pattern=r'payment_by_wallet_upgrade_service_\d+'))

    dp.add_handler(CallbackQueryHandler(remove_service, pattern=r'remove_service_(.*)'))
    dp.add_handler(CallbackQueryHandler(remove_service, pattern=r'accept_rm_ser_(.*)'))

    dp.add_handler(CallbackQueryHandler(change_notif, pattern='service_notification'))
    dp.add_handler(CallbackQueryHandler(change_notif, pattern='wallet_notification'))

    dp.add_handler(CallbackQueryHandler(main_menu, pattern='main_menu'))
    dp.add_handler(CallbackQueryHandler(pay_per_use, pattern='pay_per_use_'))
    dp.add_handler(CallbackQueryHandler(pay_per_use, pattern=r'active_ppu_\d+'))
    dp.add_handler(CallbackQueryHandler(get_pay_file, pattern='get_pay_file'))
    dp.add_handler(CallbackQueryHandler(just_for_show, pattern='just_for_show'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='ranking_page'))
    dp.add_handler(CallbackQueryHandler(main_menu, pattern='main_menu_in_new_message'))
    dp.add_handler(CallbackQueryHandler(help_sec, pattern='guidance'))
    dp.add_handler(CallbackQueryHandler(support, pattern='support'))
    dp.add_handler(CallbackQueryHandler(setting, pattern='setting'))
    dp.add_handler(CallbackQueryHandler(financial_transactions_wallet, pattern='financial_transactions_wallet'))
    dp.add_handler(CallbackQueryHandler(financial_transactions, pattern='financial_transactions'))
    dp.add_handler(CallbackQueryHandler(wallet_page, pattern='wallet_page'))

    dp.add_handler(CallbackQueryHandler(send_main_message, pattern='send_main_message'))
    dp.add_handler(CallbackQueryHandler(buy_service, pattern='select_server'))
    dp.add_handler(CallbackQueryHandler(payment_page, pattern=r'service_\d+'))
    dp.add_handler(CallbackQueryHandler(payment_page_upgrade, pattern=r'service_upgrade_\d+'))

    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern=r'payment_by_wallet_\d+'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern=r'payment_by_crypto_\d+'))
    dp.add_handler(CallbackQueryHandler(apply_card_pay, pattern=r'accept_card_pay_\d+'))
    dp.add_handler(CallbackQueryHandler(apply_card_pay, pattern=r'refuse_card_pay_\d+'))
    dp.add_handler(CallbackQueryHandler(apply_card_pay, pattern=r'ok_card_pay_accept_\d+'))
    dp.add_handler(CallbackQueryHandler(apply_card_pay, pattern=r'ok_card_pay_refuse_\d+'))
    dp.add_handler(CallbackQueryHandler(apply_card_pay, pattern='cancel_pay'))

    dp.add_handler(CallbackQueryHandler(apply_card_pay_lu, pattern=r'accept_card_pay_lu_\d+'))
    dp.add_handler(CallbackQueryHandler(apply_card_pay_lu, pattern=r'refuse_card_pay_lu_\d+'))
    dp.add_handler(CallbackQueryHandler(apply_card_pay_lu, pattern=r'ok_card_pay_lu_accept_\d+'))
    dp.add_handler(CallbackQueryHandler(apply_card_pay_lu, pattern=r'ok_card_pay_lu_refuse_\d+'))
    dp.add_handler(CallbackQueryHandler(apply_card_pay_lu, pattern='cancel_pay'))
    dp.add_handler(CallbackQueryHandler(get_free_service, pattern='get_free_service'))

    dp.add_handler(CallbackQueryHandler(apply_card_pay_credit, pattern='accept_card_pay_credit_'))
    dp.add_handler(CallbackQueryHandler(apply_card_pay_credit, pattern='refuse_card_pay_credit_'))
    dp.add_handler(CallbackQueryHandler(apply_card_pay_credit, pattern='ok_card_pay_credit_'))
    dp.add_handler(CallbackQueryHandler(apply_card_pay_credit, pattern='ok_card_pay_credit_accept_'))
    dp.add_handler(CallbackQueryHandler(apply_card_pay_credit, pattern='ok_card_pay_credit_refuse_'))


    dp.add_handler(CallbackQueryHandler(server_detail_customer, pattern=r'view_service_(.*)'))
    dp.add_handler(CallbackQueryHandler(show_help, pattern=r'(.*)_help'))

    dp.add_handler(CallbackQueryHandler(create_file_and_return, pattern=r'create_txt_file'))
    dp.add_handler(CallbackQueryHandler(personalization_service_lu, pattern=r'personalization_service_lu_\d+'))
    dp.add_handler(CallbackQueryHandler(personalization_service, pattern=r'personalization_service_\d+'))
    dp.add_handler(CallbackQueryHandler(personalization_service, pattern='accept_personalization'))

    dp.add_handler(CallbackQueryHandler(personalization_service, pattern='traffic_low_\d+'))
    dp.add_handler(CallbackQueryHandler(personalization_service, pattern='traffic_high_\d+'))
    dp.add_handler(CallbackQueryHandler(personalization_service, pattern='period_low_\d+'))
    dp.add_handler(CallbackQueryHandler(personalization_service, pattern='period_high_\d+'))

    dp.add_handler(CallbackQueryHandler(personalization_service_lu, pattern=r'traffic_low_lu_\d+'))
    dp.add_handler(CallbackQueryHandler(personalization_service_lu, pattern=r'traffic_high_lu_\d+'))
    dp.add_handler(CallbackQueryHandler(personalization_service_lu, pattern=r'period_low_lu_\d+'))
    dp.add_handler(CallbackQueryHandler(personalization_service_lu, pattern=r'period_high_lu_\d+'))

    dp.add_handler(CallbackQueryHandler(buy_credit_volume, pattern='buy_credit_volume'))
    dp.add_handler(CallbackQueryHandler(buy_credit_volume, pattern=r'value_low_\d+'))
    dp.add_handler(CallbackQueryHandler(buy_credit_volume, pattern=r'value_high_\d+'))
    dp.add_handler(CallbackQueryHandler(buy_credit_volume, pattern=r'set_credit_\d+'))
    dp.add_handler(CallbackQueryHandler(pay_way_for_credit, pattern='pay_way_for_credit_\d+'))

    dp.add_handler(CallbackQueryHandler(change_notif, pattern=r'notif_traffic_low_\d+'))
    dp.add_handler(CallbackQueryHandler(change_notif, pattern=r'notif_traffic_high_\d+'))
    dp.add_handler(CallbackQueryHandler(change_notif, pattern=r'notif_day_low_\d+'))
    dp.add_handler(CallbackQueryHandler(change_notif, pattern=r'notif_day_high_\d+'))
    dp.add_handler(CallbackQueryHandler(change_notif, pattern=r'notif_wallet_low_\d+'))
    dp.add_handler(CallbackQueryHandler(change_notif, pattern=r'notif_wallet_high_\d+'))


    dp.add_handler(CallbackQueryHandler(my_service, pattern='my_service'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='settings'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='get_test_service'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='guidance'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='support'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='not_ready_yet'))
    dp.add_handler(CallbackQueryHandler(all_query_handler))

    job = updater.job_queue
    job.run_repeating(check_all_configs, interval=300, first=0)
    job.run_repeating(pay_per_use_calculator, interval=500, first=0)

    updater.start_polling(0)
    updater.idle()


if __name__ == '__main__':
    main()
