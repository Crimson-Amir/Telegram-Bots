import logging, crud
from utilities_reFactore import FindText, UserNotFound, handle_error, message_token
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import setting

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, in_new_message=False):
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
        if update.callback_query and "start_in_new_message" not in update.callback_query.data and not in_new_message:
            return await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(main_keyboard), parse_mode='html')
        return await context.bot.send_message(chat_id=user_detail.id, text=text, reply_markup=InlineKeyboardMarkup(main_keyboard), parse_mode='html')

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
                        f'Selected Language: {selected_language}\n'
                        f"\nInvited By: <a href=\"tg://user?id={inviter_chat_id}\">{inviter_chat_id}</a>")

    if photos.total_count > 0:
        photo_file_id = photos.photos[0][-1].file_id
        await context.bot.send_photo(chat_id=setting.ADMIN_CHAT_IDs[0], photo=photo_file_id, caption=start_text_notif, parse_mode='HTML', message_thread_id=setting.new_user_thread_id)
    else:
        await context.bot.send_message(chat_id=setting.ADMIN_CHAT_IDs[0], text=start_text_notif + '\n\n• Without profile picture (or not public)', parse_mode='HTML', message_thread_id=setting.new_user_thread_id)

    return await start(update, context)


async def just_for_show(update, context):
    query = update.callback_query
    ft_instance = FindText(update, context, notify_user=False)
    await query.answer(text=await ft_instance.find_text('just_for_show'))