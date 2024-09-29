import logging, sys, crud
from utilities_reFactore import FindText, UserNotFound, handle_error, message_token
from database_sqlalchemy import SessionLocal
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
import private, wallet_reFactore
from vpn_service import start as vpn_start, buy_and_upgrade_service


# Base.metadata.create_all(bind=engine)

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)',
    handlers=[
        logging.FileHandler("freebyte.log"),
        logging.StreamHandler()
    ]
)

def log_uncaught_exceptions(exctype, value, tb):
    logging.error("Uncaught exception", exc_info=(exctype, value, tb))

sys.excepthook = log_uncaught_exceptions

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_detail = update.effective_chat

    try:
        ft_instance = FindText(update, context, notify_user=False)
        text = await ft_instance.find_text('start_menu')
        main_keyboard = [
            [InlineKeyboardButton(await ft_instance.find_keyboard('menu_services'), callback_data='menu_services')],

            [InlineKeyboardButton(await ft_instance.find_keyboard('wallet'), callback_data='wallet_page'),
             InlineKeyboardButton(await ft_instance.find_keyboard('ranking'), callback_data='ranking')],

            [InlineKeyboardButton(await ft_instance.find_keyboard('setting'), callback_data='setting'),
             InlineKeyboardButton(await ft_instance.find_keyboard('invite'), callback_data='invite')],

            [InlineKeyboardButton(await ft_instance.find_keyboard('help_button'), callback_data='help_button')],
        ]
        if update.callback_query:
            return await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(main_keyboard), parse_mode='html')
        await context.bot.send_message(chat_id=user_detail.id, text=text, reply_markup=InlineKeyboardMarkup(main_keyboard), parse_mode='html')

    except UserNotFound:
        text = ('<b>• زبان خود را انتخاب کنید:'
                '\n• Please choose your language:</b>')
        context.user_data['inviter_chat_id'] = context.args[0] if context.args else None
        keyboard = [[InlineKeyboardButton('English🇺🇲', callback_data='register_user_en'),
                     InlineKeyboardButton('Persian🇮🇷', callback_data='register_user_fa')]]
        new_select = await context.bot.send_message(chat_id=user_detail.id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
        message_token.set_message_time(new_select.message_id)

    except Exception as e:
        logging.error(f'error in send start message! \n{e}')
        await context.bot.send_message(chat_id=user_detail.id, text='<b>Sorry, somthing went wrong!</b>', parse_mode='html')

@handle_error.handle_functions_error
@message_token.check_token
async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_detail = update.effective_chat
    query = update.callback_query
    selected_language = query.data.replace('register_user_', '')
    inviter_chat_id = context.user_data.get('inviter_chat_id')

    crud.create_user(user_detail, inviter_chat_id, selected_language)
    photos = await context.bot.get_user_profile_photos(user_id=user_detail.id)

    start_text_notif = (f'👤 New Start IN Bot\n\n'
                        f'User Name: {user_detail.first_name} {user_detail.last_name}\n'
                        f'User ID: <a href=\"tg://user?id={user_detail.id}\">{user_detail.id}</a>\n'
                        f'UserName: @{user_detail.username}\n'
                        f'User Language: {selected_language}\n'
                        f"\nInvited By: <a href=\"tg://user?id={inviter_chat_id}\">{inviter_chat_id}</a>")

    if photos.total_count > 0:
        photo_file_id = photos.photos[0][-1].file_id
        await context.bot.send_photo(chat_id=private.ADMIN_CHAT_IDs[0], photo=photo_file_id, caption=start_text_notif, parse_mode='HTML')
    else:
        await context.bot.send_message(chat_id=private.ADMIN_CHAT_IDs[0], text=start_text_notif + '\n\n• Without profile picture (or not public)', parse_mode='HTML')

    return await start(update, context)

@message_token.check_token
async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_detail = update.effective_chat
    ft_instance = FindText(update, context)
    with SessionLocal() as session:
        user = crud.get_user(session, user_detail.id)

        level_access = {
            1: [],
            private.vpn_level: [[InlineKeyboardButton(await ft_instance.find_keyboard('buy_vpn_service'), callback_data='vpn_main_menu')]]
        }

        try:
            text = await ft_instance.find_text('select_section')
            main_keyboard = []
            for level in range(1, user.user_level + 1):
                main_keyboard.extend(level_access.get(level, level_access.get(1)))
            main_keyboard.append([InlineKeyboardButton(await ft_instance.find_keyboard('back_button'), callback_data='start')])
            return await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(main_keyboard), parse_mode='html')

        except Exception as e:
            logging.error(f'error in services message! \n{e}')
            return await update.callback_query.answer(text=await ft_instance.find_text('error_message'))


if __name__ == '__main__':
    application = ApplicationBuilder().token(private.telegram_bot_token).build()

    # Commands
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('vpn_start', start))

    # Bot Main Menu
    application.add_handler(CallbackQueryHandler(start, pattern='start'))
    application.add_handler(CallbackQueryHandler(register_user, pattern='register_user_(.*)'))
    application.add_handler(CallbackQueryHandler(services, pattern='menu_services'))

    # Wallet
    application.add_handler(CallbackQueryHandler(wallet_reFactore.wallet_page, pattern='wallet_page'))
    application.add_handler(CallbackQueryHandler(wallet_reFactore.financial_transactions_wallet, pattern='financial_transactions_wallet'))
    application.add_handler(CallbackQueryHandler(wallet_reFactore.buy_credit_volume, pattern='buy_credit_volume'))
    application.add_handler(CallbackQueryHandler(wallet_reFactore.create_invoice, pattern='create_invoice__(.*)'))
    application.add_handler(CallbackQueryHandler(wallet_reFactore.pay_by_zarinpal, pattern='pay_by_zarinpal__(.*)'))

    # VPN Section
    application.add_handler(CallbackQueryHandler(vpn_start.vpn_main_menu, pattern='vpn_main_menu'))
    application.add_handler(CallbackQueryHandler(buy_and_upgrade_service.buy_custom_service, pattern='vpn_set_period_traffic__(.*)'))



    application.run_polling()
