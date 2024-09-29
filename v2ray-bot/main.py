from database import create_database
create_database('./v2ray.db')
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import bot_start, tasks, utilities, admin_task, statistics, private, logging
import cryptomus.BotcryptoPayment as BotCryptomus
import API.zarinPalBOT as ZarinPal

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    updater = Updater(private.telegram_bot_token)
    dp = updater.dispatcher

    commands = {
        'start': bot_start,
        'help': bot_start,
        'check_all_configs': tasks.check_all_configs,
        'add_service': admin_task.add_service,
        'del_service': admin_task.del_service,
        'run_in_system': admin_task.run_in_system,
        'say_to_every_one': admin_task.say_to_every_one,
        'message_to_user': utilities.message_to_user,
        'clear_depleted_service': admin_task.clear_depleted_service,
        'add_credit_to_customer': admin_task.add_credit_to_customer,
    }

    for key, value in commands.items():
        dp.add_handler(CommandHandler(key, value))

    dp.add_handler(tasks.tickect_by_user)
    dp.add_handler(tasks.reply_ticket)
    dp.add_handler(tasks.upgrade_service_by_card_conv)
    dp.add_handler(tasks.get_service_con)
    dp.add_handler(tasks.credit_charge)
    dp.add_handler(tasks.change_service_ownership_conver)

    dp.add_handler(CallbackQueryHandler(tasks.get_pay_file, pattern='get_pay_file'))
    dp.add_handler(CallbackQueryHandler(tasks.report_problem_by_user, pattern=r'say_to_admin_(.*)'))
    dp.add_handler(CallbackQueryHandler(tasks.all_services, pattern=r'adm_check_all_conf(.*)'))

    dp.add_handler(CallbackQueryHandler(bot_start.send_check_new_user_request_to_admin, pattern='send_joining_request'))
    dp.add_handler(CallbackQueryHandler(bot_start.check_new_user_request_by_admin, pattern=r'accept_user_(.*)'))
    dp.add_handler(CallbackQueryHandler(bot_start.check_new_user_request_by_admin, pattern=r'deny_user_(.*)'))

    dp.add_handler(CallbackQueryHandler(ZarinPal.zarinpall_page_wallet, pattern=r'zarinpall_page_wallet_\d+'))
    dp.add_handler(CallbackQueryHandler(ZarinPal.zarinpall_page_buy, pattern=r'zarinpall_page_buy_\d+'))
    dp.add_handler(CallbackQueryHandler(ZarinPal.zarinpall_page_upgrade, pattern=r'zarinpall_page_upgrade_\d+'))

    dp.add_handler(CallbackQueryHandler(tasks.get_ticket_priority, pattern=r'get_ticket_priority'))
    dp.add_handler(CallbackQueryHandler(tasks.delete_message, pattern=r'delete_message'))
    dp.add_handler(CallbackQueryHandler(tasks.change_ticket_status, pattern=r'change_ticket_status_'))

    dp.add_handler(CallbackQueryHandler(tasks.service_advanced_option, pattern=r'advanced_option_(.*)'))
    dp.add_handler(CallbackQueryHandler(tasks.service_advanced_option, pattern=r'change_auto_renewal_status_(.*)'))
    dp.add_handler(CallbackQueryHandler(tasks.service_advanced_option, pattern=r'change_config_shematic_(.*)'))

    dp.add_handler(CallbackQueryHandler(tasks.show_servers, pattern='select_server'))

    dp.add_handler(CallbackQueryHandler(BotCryptomus.cryptomus_page_upgrade, pattern='cryptomus_page_upgrade_\d+'))
    dp.add_handler(CallbackQueryHandler(BotCryptomus.check_cryptomus_payment_upgrade, pattern=r'check_cryptomus_payment_upgrade_(.*)'))
    dp.add_handler(CallbackQueryHandler(BotCryptomus.cryptomus_page_wallet, pattern='cryptomus_page_wallet_\d+'))
    dp.add_handler(CallbackQueryHandler(BotCryptomus.check_cryptomus_payment_wallet, pattern=r'check_cryptomus_payment_wallet_(.*)'))
    dp.add_handler(CallbackQueryHandler(BotCryptomus.cryptomus_page, pattern='cryptomus_page_\d+'))
    dp.add_handler(CallbackQueryHandler(BotCryptomus.check_cryptomus_payment, pattern=r'check_cryptomus_payment_(.*)'))

    dp.add_handler(CallbackQueryHandler(tasks.service_statistics, pattern=r'service_statistics_(.*)'))
    dp.add_handler(CallbackQueryHandler(tasks.my_service, pattern=r'my_service(.*)'))

    dp.add_handler(CallbackQueryHandler(BotCryptomus.check_cryptomus_payment, pattern=r'check_cryptomus_payment_(.*)'))
    dp.add_handler(CallbackQueryHandler(tasks.remove_service_from_db, pattern=r'remove_service_from_db_(.*)'))
    dp.add_handler(CallbackQueryHandler(tasks.pay_from_wallet, pattern=r'accept_wallet_upgrade_pay_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.pay_from_wallet, pattern=r'payment_by_wallet_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.pay_from_wallet, pattern=r'accept_wallet_pay_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.pay_from_wallet, pattern=r'payment_by_wallet_upgrade_service_\d+'))

    dp.add_handler(CallbackQueryHandler(statistics.report_section, pattern=r'statistics_(.*)'))
    dp.add_handler(CallbackQueryHandler(statistics.radar_section, pattern=r'radar_section'))
    dp.add_handler(CallbackQueryHandler(tasks.remove_service, pattern=r'remove_service_(.*)'))
    dp.add_handler(CallbackQueryHandler(tasks.remove_service, pattern=r'accept_rm_ser_(.*)'))

    dp.add_handler(CallbackQueryHandler(tasks.change_notif, pattern='service_notification'))
    dp.add_handler(CallbackQueryHandler(utilities.not_for_depleted_service, pattern='not_for_depleted_service'))
    dp.add_handler(CallbackQueryHandler(tasks.change_notif, pattern='wallet_notification'))

    dp.add_handler(CallbackQueryHandler(bot_start.main_menu, pattern='main_menu'))
    dp.add_handler(CallbackQueryHandler(bot_start.main_menu_delete_main_message, pattern='menu_delete_main_message'))
    dp.add_handler(CallbackQueryHandler(utilities.alredy_have_show, pattern='alredy_have_show'))
    dp.add_handler(CallbackQueryHandler(tasks.subcategory, pattern='subcategory'))
    dp.add_handler(CallbackQueryHandler(tasks.hide_buttons, pattern='hide_buttons'))
    dp.add_handler(CallbackQueryHandler(utilities.just_for_show, pattern='just_for_show'))
    dp.add_handler(CallbackQueryHandler(bot_start.main_menu, pattern='main_menu_in_new_message'))
    dp.add_handler(CallbackQueryHandler(tasks.guidance, pattern='guidance'))
    dp.add_handler(CallbackQueryHandler(tasks.setting, pattern='setting'))
    dp.add_handler(CallbackQueryHandler(tasks.financial_transactions_wallet, pattern='financial_transactions_wallet'))
    dp.add_handler(CallbackQueryHandler(tasks.wallet_page, pattern='wallet_page'))

    dp.add_handler(CallbackQueryHandler(bot_start.send_main_message, pattern='send_main_message'))
    dp.add_handler(CallbackQueryHandler(tasks.payment_page, pattern=r'service_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.payment_page_upgrade, pattern=r'service_upgrade_\d+'))

    dp.add_handler(CallbackQueryHandler(utilities.not_ready_yet, pattern=r'payment_by_wallet_\d+'))
    dp.add_handler(CallbackQueryHandler(utilities.not_ready_yet, pattern=r'payment_by_crypto_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.apply_card_pay, pattern=r'accept_card_pay_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.apply_card_pay, pattern=r'refuse_card_pay_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.apply_card_pay, pattern=r'ok_card_pay_accept_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.apply_card_pay, pattern=r'ok_card_pay_refuse_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.apply_card_pay, pattern='cancel_pay'))

    dp.add_handler(CallbackQueryHandler(tasks.apply_card_pay_lu, pattern=r'accept_card_pay_lu_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.apply_card_pay_lu, pattern=r'refuse_card_pay_lu_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.apply_card_pay_lu, pattern=r'ok_card_pay_lu_accept_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.apply_card_pay_lu, pattern=r'ok_card_pay_lu_refuse_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.apply_card_pay_lu, pattern='cancel_pay'))
    dp.add_handler(CallbackQueryHandler(tasks.get_free_service, pattern='get_free_service'))

    dp.add_handler(CallbackQueryHandler(tasks.apply_card_pay_credit, pattern='accept_card_pay_credit_'))
    dp.add_handler(CallbackQueryHandler(tasks.apply_card_pay_credit, pattern='refuse_card_pay_credit_'))
    dp.add_handler(CallbackQueryHandler(tasks.apply_card_pay_credit, pattern='ok_card_pay_credit_'))
    dp.add_handler(CallbackQueryHandler(tasks.apply_card_pay_credit, pattern='ok_card_pay_credit_accept_'))
    dp.add_handler(CallbackQueryHandler(tasks.apply_card_pay_credit, pattern='ok_card_pay_credit_refuse_'))


    dp.add_handler(CallbackQueryHandler(tasks.server_detail_customer, pattern=r'view_service_(.*)'))
    dp.add_handler(CallbackQueryHandler(tasks.show_help, pattern=r'(.*)_help'))

    dp.add_handler(CallbackQueryHandler(tasks.personalization_service_lu, pattern=r'upgrade_service_customize_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.personalization_service, pattern=r'personalization_service_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.personalization_service, pattern='accept_personalization'))

    dp.add_handler(CallbackQueryHandler(tasks.personalization_service, pattern='traffic_low_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.personalization_service, pattern='traffic_high_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.personalization_service, pattern='period_low_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.personalization_service, pattern='period_high_\d+'))

    dp.add_handler(CallbackQueryHandler(tasks.personalization_service_lu, pattern=r'traffic_low_lu_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.personalization_service_lu, pattern=r'traffic_high_lu_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.personalization_service_lu, pattern=r'period_low_lu_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.personalization_service_lu, pattern=r'period_high_lu_\d+'))

    dp.add_handler(CallbackQueryHandler(tasks.buy_credit_volume, pattern='buy_credit_volume'))
    dp.add_handler(CallbackQueryHandler(tasks.buy_credit_volume, pattern=r'value_low_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.buy_credit_volume, pattern=r'value_high_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.buy_credit_volume, pattern=r'set_credit_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.pay_way_for_credit, pattern='pay_way_for_credit_\d+'))

    dp.add_handler(CallbackQueryHandler(tasks.change_notif, pattern=r'notif_traffic_low_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.change_notif, pattern=r'notif_traffic_high_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.change_notif, pattern=r'notif_day_low_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.change_notif, pattern=r'notif_day_high_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.change_notif, pattern=r'notif_wallet_low_\d+'))
    dp.add_handler(CallbackQueryHandler(tasks.change_notif, pattern=r'notif_wallet_high_\d+'))

    dp.add_handler(CallbackQueryHandler(utilities.not_ready_yet, pattern='not_ready_yet'))
    dp.add_handler(CallbackQueryHandler(tasks.get_service_of_server))

    job = updater.job_queue
    job.run_repeating(tasks.check_all_configs, interval=100)
    job.run_repeating(tasks.refresh_login, interval=1800)
    job.run_repeating(statistics.statistics_timer, interval=statistics.STATISTICS_TIMER_HORSE * 3600)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
