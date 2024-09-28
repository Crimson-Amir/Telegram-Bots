from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utilities_reFactore import FindText, message_token, handle_error
from database_sqlalchemy import SessionLocal
import private, crud

@handle_error.handle_functions_error
async def vpn_main_menu(update, context):
    user = update.effective_chat
    ft_instance = FindText(update, context, notify_user=False)

    with SessionLocal() as session:
        user = crud.get_user(session, user.id)

        keyboard = [
            [InlineKeyboardButton(await ft_instance.find_keyboard('vpn_buy_vpn'), callback_data='vpn_set_period_traffic__30_40')],
            [InlineKeyboardButton(await ft_instance.find_keyboard('vpn_reports'), callback_data='statistics_week_all_hide'),
             InlineKeyboardButton(await ft_instance.find_keyboard('vpn_my_services'), callback_data='my_service')],
            [InlineKeyboardButton(await ft_instance.find_keyboard('vpn_test_service'), callback_data='service_1')],
            [InlineKeyboardButton(await ft_instance.find_keyboard('setting'), callback_data='settings'),
             InlineKeyboardButton(await ft_instance.find_keyboard('help_button'), callback_data='guidance')],
            [InlineKeyboardButton(await ft_instance.find_keyboard('back_button'), callback_data='menu_services')]
        ]

        text = f"{await ft_instance.find_text('vpn_welcome')}\n\n{await ft_instance.find_text('select_section')}"

        if user.user_level < private.vpn_level:
            text = await ft_instance.find_keyboard('not_enogh_rank')
            keyboard = [[InlineKeyboardButton(await ft_instance.find_keyboard('back_button'), callback_data='menu_services')]]

        if update.callback_query:
            return await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
        await context.bot.send_message(chat_id=user.id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
