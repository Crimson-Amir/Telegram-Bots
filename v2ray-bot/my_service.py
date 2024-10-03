from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from utilities_reFactore import FindText, message_token, handle_error
from vpn_service import vpn_crud
from database_sqlalchemy import SessionLocal

@handle_error.handle_functions_error
@message_token.check_token
async def my_services(update, context):
    query = update.callback_query
    ft_instance = FindText(update, context)
    user_detail = update.effective_chat

    with SessionLocal() as session:
        with session.begin():
            purchases = vpn_crud.get_first_purchase_by_chat_id(session, user_detail.id)
            numbers = None

            if not purchases and not numbers:
                return await query.answer(await ft_instance.find_text('no_service_available'), show_alert=True)

            keyboard = []
            if purchases:
                keyboard.append([InlineKeyboardButton(await ft_instance.find_keyboard('vpn_services_lable'), callback_data='vpn_my_services')])

            keyboard.append([InlineKeyboardButton(await ft_instance.find_keyboard('back_button'), callback_data='start')])

            text = f"<b>{await ft_instance.find_text('select_service_category')}</b>"
            if update.callback_query:
                return await query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))
            return await context.bot.send_message(chat_id=user_detail.id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
