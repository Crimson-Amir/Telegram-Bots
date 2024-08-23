from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler)
from private import telegram_bot_token, ADMIN_CHAT_ID

from database import create_database
create_database('./v2ray.db')

from bot_start import (bot_start, main_menu, send_main_message, main_menu_delete_main_message,
                       send_check_new_user_request_to_admin, check_new_user_request_by_admin)
from tasks import (show_servers, get_service_of_server, payment_page, get_service_con, apply_card_pay,
                   my_service, create_file_and_return, server_detail_customer, personalization_service,
                   personalization_service_lu, apply_card_pay_lu, upgrade_service_by_card_conv, get_free_service, guidance,
                   show_help, support, setting, change_notif, start_timer, financial_transactions,
                   wallet_page, financial_transactions_wallet, payment_page_upgrade, buy_credit_volume,
                   pay_way_for_credit, credit_charge, apply_card_pay_credit, pay_from_wallet, remove_service,
                   check_all_configs, remove_service_from_db, rate_service, get_pay_file,
                   admin_reserve_service, people_ask, pay_per_use, pay_per_use_calculator, change_infiniti_service_status,
                   report_problem_by_user, tickect_by_user, service_advanced_option, rank_page, subcategory,
                   change_service_ownership_conver, hide_buttons, admin_all_config, all_services, admin_server_detail,
                   service_statistics, daily_gift, daily_gift_message, delete_message, get_ticket_priority, reply_ticket,
                   change_ticket_status, refresh_login)

from utilities import not_ready_yet, just_for_show, message_to_user, alredy_have_show, not_for_depleted_service

from admin_task import (admin_add_update_inbound, add_service, all_service, del_service, run_in_system,
                        say_to_every_one, clear_depleted_service, say_to_customer_of_server,
                        add_credit_to_server_customer_wallet, add_credit_to_customer, admin_rank_up)

import logging, requests
from statistics import statistics_timer, STATISTICS_TIMER_HORSE, report_section, radar_section
from cryptomus.BotcryptoPayment import (cryptomus_page, check_cryptomus_payment,cryptomus_page_upgrade,
                                        check_cryptomus_payment_upgrade, cryptomus_page_wallet, check_cryptomus_payment_wallet)

from zarinPal.zarinPalBOT import zarinpall_page_buy, zarinpall_page_upgrade, zarinpall_page_wallet


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

telegram_bot_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
requests.post(telegram_bot_url, data={'chat_id': ADMIN_CHAT_ID, 'text':'🟠 THE BOT STARTED'})

# def bot_start(update, context):
#     update.message.reply_text('ربات به دلیل آپدیت تا 2024-06-15 02:31:18 غیرفعال میباشد.\nآیدی پشتیبانی: @FreeByte_Support')


def main():
    updater = Updater(telegram_bot_token)
    dp = updater.dispatcher

    commands = {
        'start': bot_start,
        'help': bot_start,
        'add_inbound': admin_add_update_inbound,
        'check_all_configs': check_all_configs,
        'all_configs': admin_all_config,
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
        'rank_up': admin_rank_up,
        'daily_gift_message': daily_gift_message
    }

    for key, value in commands.items():
        dp.add_handler(CommandHandler(key, value))

    dp.add_handler(tickect_by_user)
    dp.add_handler(reply_ticket)
    dp.add_handler(upgrade_service_by_card_conv)
    dp.add_handler(get_service_con)
    dp.add_handler(credit_charge)
    dp.add_handler(change_service_ownership_conver)

    # dp.add_handler(CallbackQueryHandler(get_ticket_department, pattern=r'get_ticket_department'))

    dp.add_handler(CallbackQueryHandler(send_check_new_user_request_to_admin, pattern='send_joining_request'))
    dp.add_handler(CallbackQueryHandler(check_new_user_request_by_admin, pattern=r'accept_user_(.*)'))
    dp.add_handler(CallbackQueryHandler(check_new_user_request_by_admin, pattern=r'deny_user_(.*)'))



    dp.add_handler(CallbackQueryHandler(zarinpall_page_wallet, pattern=r'zarinpall_page_wallet_\d+'))
    dp.add_handler(CallbackQueryHandler(zarinpall_page_buy, pattern=r'zarinpall_page_buy_\d+'))
    dp.add_handler(CallbackQueryHandler(zarinpall_page_upgrade, pattern=r'zarinpall_page_upgrade_\d+'))

    dp.add_handler(CallbackQueryHandler(get_ticket_priority, pattern=r'get_ticket_priority'))
    dp.add_handler(CallbackQueryHandler(delete_message, pattern=r'delete_message'))
    dp.add_handler(CallbackQueryHandler(change_ticket_status, pattern=r'change_ticket_status_'))

    dp.add_handler(CallbackQueryHandler(service_advanced_option, pattern=r'active_tls_encoding_(.*)'))
    dp.add_handler(CallbackQueryHandler(service_advanced_option, pattern=r'advanced_option_(.*)'))
    dp.add_handler(CallbackQueryHandler(service_advanced_option, pattern=r'change_auto_renewal_status_(.*)'))
    dp.add_handler(CallbackQueryHandler(service_advanced_option, pattern=r'change_config_shematic_(.*)'))
    dp.add_handler(CallbackQueryHandler(service_advanced_option, pattern=r'changed_server_to_(.*)'))
    dp.add_handler(CallbackQueryHandler(service_advanced_option, pattern=r'change_server_(.*)'))

    dp.add_handler(CallbackQueryHandler(show_servers, pattern='select_server'))
    dp.add_handler(CallbackQueryHandler(daily_gift, pattern='daily_gift'))

    dp.add_handler(CallbackQueryHandler(cryptomus_page_upgrade, pattern='cryptomus_page_upgrade_\d+'))
    dp.add_handler(CallbackQueryHandler(check_cryptomus_payment_upgrade, pattern=r'check_cryptomus_payment_upgrade_(.*)'))
    dp.add_handler(CallbackQueryHandler(cryptomus_page_wallet, pattern='cryptomus_page_wallet_\d+'))
    dp.add_handler(CallbackQueryHandler(check_cryptomus_payment_wallet, pattern=r'check_cryptomus_payment_wallet_(.*)'))
    dp.add_handler(CallbackQueryHandler(cryptomus_page, pattern='cryptomus_page_\d+'))
    dp.add_handler(CallbackQueryHandler(check_cryptomus_payment, pattern=r'check_cryptomus_payment_(.*)'))

    dp.add_handler(CallbackQueryHandler(service_statistics, pattern=r'service_statistics_(.*)'))
    dp.add_handler(CallbackQueryHandler(my_service, pattern=r'my_service(.*)'))
    dp.add_handler(CallbackQueryHandler(all_services, pattern=r'adm_check_all_conf(.*)'))

    dp.add_handler(CallbackQueryHandler(check_cryptomus_payment, pattern=r'check_cryptomus_payment_(.*)'))
    dp.add_handler(CallbackQueryHandler(rate_service, pattern=r'rate_(.*)'))
    dp.add_handler(CallbackQueryHandler(people_ask, pattern=r'ask_(.*)'))
    dp.add_handler(CallbackQueryHandler(remove_service_from_db, pattern=r'remove_service_from_db_(.*)'))
    dp.add_handler(CallbackQueryHandler(pay_from_wallet, pattern=r'accept_wallet_upgrade_pay_\d+'))
    dp.add_handler(CallbackQueryHandler(pay_from_wallet, pattern=r'payment_by_wallet_\d+'))
    dp.add_handler(CallbackQueryHandler(pay_from_wallet, pattern=r'accept_wallet_pay_\d+'))
    dp.add_handler(CallbackQueryHandler(pay_from_wallet, pattern=r'payment_by_wallet_upgrade_service_\d+'))

    dp.add_handler(CallbackQueryHandler(report_section, pattern=r'statistics_(.*)'))
    dp.add_handler(CallbackQueryHandler(radar_section, pattern=r'radar_section'))
    dp.add_handler(CallbackQueryHandler(remove_service, pattern=r'remove_service_(.*)'))
    dp.add_handler(CallbackQueryHandler(remove_service, pattern=r'accept_rm_ser_(.*)'))
    dp.add_handler(CallbackQueryHandler(report_problem_by_user, pattern=r'say_to_admin_(.*)'))

    dp.add_handler(CallbackQueryHandler(change_infiniti_service_status, pattern=r'change_infiniti_service_status_(.*)'))

    dp.add_handler(CallbackQueryHandler(change_notif, pattern='service_notification'))
    dp.add_handler(CallbackQueryHandler(not_for_depleted_service, pattern='not_for_depleted_service'))
    dp.add_handler(CallbackQueryHandler(change_notif, pattern='wallet_notification'))
    dp.add_handler(CallbackQueryHandler(report_problem_by_user, pattern='report_problem_by_user'))

    dp.add_handler(CallbackQueryHandler(main_menu, pattern='main_menu'))
    dp.add_handler(CallbackQueryHandler(main_menu_delete_main_message, pattern='menu_delete_main_message'))
    dp.add_handler(CallbackQueryHandler(alredy_have_show, pattern='alredy_have_show'))
    dp.add_handler(CallbackQueryHandler(subcategory, pattern='subcategory'))
    dp.add_handler(CallbackQueryHandler(rank_page, pattern='rank_page'))
    dp.add_handler(CallbackQueryHandler(hide_buttons, pattern='hide_buttons'))
    dp.add_handler(CallbackQueryHandler(pay_per_use, pattern='pay_per_use_'))
    dp.add_handler(CallbackQueryHandler(pay_per_use, pattern=r'active_ppu_\d+'))
    dp.add_handler(CallbackQueryHandler(get_pay_file, pattern='get_pay_file'))
    dp.add_handler(CallbackQueryHandler(just_for_show, pattern='just_for_show'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='ranking_page'))
    dp.add_handler(CallbackQueryHandler(main_menu, pattern='main_menu_in_new_message'))
    dp.add_handler(CallbackQueryHandler(guidance, pattern='guidance'))
    dp.add_handler(CallbackQueryHandler(support, pattern='support'))
    dp.add_handler(CallbackQueryHandler(setting, pattern='setting'))
    dp.add_handler(CallbackQueryHandler(financial_transactions_wallet, pattern='financial_transactions_wallet'))
    dp.add_handler(CallbackQueryHandler(financial_transactions, pattern='financial_transactions'))
    dp.add_handler(CallbackQueryHandler(wallet_page, pattern='wallet_page'))

    dp.add_handler(CallbackQueryHandler(send_main_message, pattern='send_main_message'))
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
    dp.add_handler(CallbackQueryHandler(admin_server_detail, pattern=r'adm_view_service_(.*)'))
    dp.add_handler(CallbackQueryHandler(show_help, pattern=r'(.*)_help'))

    dp.add_handler(CallbackQueryHandler(create_file_and_return, pattern=r'create_txt_file_(.*)'))
    dp.add_handler(CallbackQueryHandler(personalization_service_lu, pattern=r'upgrade_service_customize_\d+'))
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

    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='settings'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='get_test_service'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='guidance'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='support'))
    dp.add_handler(CallbackQueryHandler(not_ready_yet, pattern='not_ready_yet'))

    dp.add_handler(CallbackQueryHandler(get_service_of_server))

    job = updater.job_queue
    job.run_repeating(check_all_configs, interval=100)
    job.run_repeating(refresh_login, interval=1800)
    job.run_repeating(pay_per_use_calculator, interval=3600)
    job.run_repeating(statistics_timer, interval=STATISTICS_TIMER_HORSE * 3600)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
