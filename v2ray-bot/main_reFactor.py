import logging, sys
from utilities_reFactore import FindText, message_token, handle_error
import start_reFactore, my_service
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
import setting, wallet_reFactore
from vpn_service import buy_and_upgrade_service, my_service_detail
import my_service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)',
    handlers=[
        logging.FileHandler("freebyte.log"),
        logging.StreamHandler()
    ]
)

def log_uncaught_exceptions(exctype, value, tb):
    logging.error("Uncaught exception", exc_info=(exctype, value, tb))

sys.excepthook = log_uncaught_exceptions

@handle_error.handle_functions_error
@message_token.check_token
async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ft_instance = FindText(update, context)

    text = await ft_instance.find_text('select_section')
    main_keyboard = [
        [InlineKeyboardButton(await ft_instance.find_keyboard('buy_vpn_service_lable'), callback_data='vpn_set_period_traffic__30_40')],
        [InlineKeyboardButton(await ft_instance.find_keyboard('back_button'), callback_data='start')]
    ]
    return await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(main_keyboard), parse_mode='html')


if __name__ == '__main__':
    application = ApplicationBuilder().token(setting.telegram_bot_token).build()

    # Commands
    application.add_handler(CommandHandler('start', start_reFactore.start))
    application.add_handler(CommandHandler('vpn_start', start_reFactore.start))

    # Bot Main Menu
    application.add_handler(CallbackQueryHandler(start_reFactore.start, pattern='start'))
    application.add_handler(CallbackQueryHandler(start_reFactore.start, pattern='start_in_new_message'))
    application.add_handler(CallbackQueryHandler(start_reFactore.register_user, pattern='register_user_(.*)'))
    application.add_handler(CallbackQueryHandler(services, pattern='menu_services'))
    application.add_handler(CallbackQueryHandler(start_reFactore.just_for_show, pattern='just_for_show'))
    application.add_handler(CallbackQueryHandler(my_service.my_services, pattern='my_services'))

    # Wallet
    application.add_handler(CallbackQueryHandler(wallet_reFactore.wallet_page, pattern='wallet_page'))
    application.add_handler(CallbackQueryHandler(wallet_reFactore.financial_transactions_wallet, pattern='financial_transactions_wallet'))
    application.add_handler(CallbackQueryHandler(wallet_reFactore.buy_credit_volume, pattern='buy_credit_volume'))
    application.add_handler(CallbackQueryHandler(wallet_reFactore.create_invoice, pattern='create_invoice__(.*)'))
    application.add_handler(CallbackQueryHandler(wallet_reFactore.pay_by_zarinpal, pattern='pay_by_zarinpal__(.*)'))
    application.add_handler(CallbackQueryHandler(wallet_reFactore.pay_by_cryptomus, pattern='pay_by_cryptomus__(.*)'))
    application.add_handler(CallbackQueryHandler(wallet_reFactore.pay_by_wallet, pattern='pay_by_wallet__(.*)'))

    # VPN Section
    application.add_handler(CallbackQueryHandler(buy_and_upgrade_service.buy_custom_service, pattern='vpn_set_period_traffic__(.*)'))
    application.add_handler(CallbackQueryHandler(buy_and_upgrade_service.upgrade_service, pattern='vpn_upgrade_service__(.*)'))
    application.add_handler(CallbackQueryHandler(my_service_detail.service_info, pattern='vpn_my_service_detail__(.*)'))
    application.add_handler(CallbackQueryHandler(my_service_detail.my_services, pattern='vpn_my_services(.*)'))

    application.run_polling()

