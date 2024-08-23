import datetime
import pytz
import sqlite3
from telegram import InlineKeyboardMarkup
from private import ADMIN_CHAT_ID
from keyboard import main_key as key
from ranking import rank_access
from utilities import message_to_user, init_name, sqlite_manager, ranking_manage
from telegram import InlineKeyboardButton
from telegram import Update

RANK_PER_INVITE = 50
class UsersStartData:
    proccess_users = set()
    deny_users = set()
    accept_users = set()
    UserData = {}

    def add_user_to_proccess_list(self, user_id):
        self.proccess_users.add(user_id)

    def remove_user_from_proccess_list(self, user_id):
        self.proccess_users.discard(user_id)

    def add_user_to_deny_users(self, user_id):
        self.remove_user_from_proccess_list(user_id)
        self.accept_users.discard(user_id)
        self.deny_users.add(user_id)

    def add_user_to_accept_users(self, user_id):
        self.remove_user_from_proccess_list(user_id)
        self.deny_users.discard(user_id)
        self.accept_users.add(user_id)

    def is_user_available_in_deny_list(self, user_id):
        if user_id in self.deny_users: return True
        return False

    def is_user_available_in_accept_list(self, user_id):
        if user_id in self.accept_users: return True
        return False

    def is_user_available_in_any_of_lists(self, user_id):
        if user_id in self.proccess_users or user_id in self.deny_users or user_id in self.deny_users: return True
        return False


user_lists_instance = UsersStartData()

def create_user(context, user, invited_by):
    print(user)
    rank_name_ = next(iter(rank_access))
    level = 0
    date = str(datetime.datetime.now(pytz.timezone('Asia/Tehran')).strftime("%H:%M:%S-%Y/%m/%d"))

    photos = context.bot.get_user_profile_photos(user_id=user.id)

    start_text_notif = (f'👤 New Start IN Bot\n\n'
                        f'User Name: {user.first_name} {user.last_name}\n'
                        f'User ID: <a href=\"tg://user?id={user.id}\">{user.id}</a>\n'
                        f'UserName: @{user.username}\n'
                        f'User Language: {user.language_code}\n'
                        f'Is User Premium: {user.is_premium}\n'
                        f'Is User BOT: {user.is_bot}\n')

    sqlite_manager.custom(f"""INSERT INTO Rank (name,user_name,chat_id,level,rank_name)
                              VALUES ("{init_name(user.first_name)}","{user.username}",{user.id},{level},"{rank_name_}")""")

    ranking_manage.rank_up(RANK_PER_INVITE, user['id'])

    start_text_notif += f"\nInvited By: <a href=\"tg://user?id={invited_by}\">{invited_by}</a>" if invited_by else ''

    sqlite_manager.custom(f"""
        INSERT INTO User (name, user_name, chat_id, date, traffic, period, free_service, notification_gb, notification_day, wallet, invited_by) 
        VALUES ("{init_name(user.first_name)}", "{user.username}", {user.id}, "{str(date)}", 10, 7, 0, 85, 2, 0, {invited_by})
    """)

    if photos.total_count > 0:
        photo_file_id = photos.photos[0][-1].file_id
        context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo_file_id, caption=start_text_notif, parse_mode='HTML')
    else:
        context.bot.send_message(chat_id=ADMIN_CHAT_ID,
                                 text=start_text_notif + '\n\n• Without Profile Picture (or not public)', parse_mode='HTML')


    user_text = f"<b>درود <a href='tg://user?id={user.id}'>{user.first_name}</a> عزیز، به FreeByte خوش آمدید.\nبرای ادامه بخش مورد نظر خودتون رو انتخاب کنید:\n</b>"
    context.bot.send_message(chat_id=user.id, text=user_text, reply_markup=InlineKeyboardMarkup(key), parse_mode='HTML')


def bot_start(update, context):
    user = update.message.from_user
    chat_id = update.message.chat_id

    user_is_available = sqlite_manager.custom(f'SELECT id FROM User WHERE chat_id = {chat_id}')

    def check_invite_link():
        if context.args:
            get_user_id = context.args[0].split('_')[1]
            get_user = sqlite_manager.select(table='User', where=f'id = {get_user_id}')

            if not get_user:
                return

            ranking_manage.rank_up(RANK_PER_INVITE, get_user[0][3])

            message_to_user(update, context,
                            message=f'کاربر {user["first_name"]} با لینک دعوت شما ربات رو استارت کرد.\nتبریک، +50 رتبه دریافت کردید!',
                            chat_id=get_user[0][3])

            return get_user[0][3]

    invited_by = check_invite_link()

    if len(user_is_available):
        user_text = f"<b>درود <a href='tg://user?id={user['id']}'>{user['first_name']}</a> عزیز، به FreeByte خوش آمدید.\nبرای ادامه بخش مورد نظر خودتون رو انتخاب کنید:\n</b>"
        return update.message.reply_text(text=user_text, reply_markup=InlineKeyboardMarkup(key), parse_mode='HTML')

    elif len(user_is_available) == 0 and invited_by:
        create_user(context, user, invited_by)

    else:
        if user_lists_instance.is_user_available_in_any_of_lists(chat_id):
            text = ('• شما از قبل درخواست ارسال کردید و نمیتوانید دوباره این کار را انجام بدید!'
                    '\n• وضعیت درخواست: ')

            if user_lists_instance.is_user_available_in_deny_list(chat_id):
                text += 'متاسفانه درخواست شما رد شده، اما هنوز میتوانید از طریق لینک دعوت به ربات بپیوندید.'
            elif user_lists_instance.is_user_available_in_accept_list(chat_id):
                text += 'درخواست شما قبول شده و در ربات عضو هستید.'
            else:
                text += 'درخواست شما درحال بررسی است.'

            return update.message.reply_text(text=text, parse_mode='HTML')


        anonymous_key = [
            [InlineKeyboardButton("ارسال درخواست عضویت ⤒", callback_data=f'send_joining_request')],
        ]

        user_lists_instance.add_user_to_proccess_list(chat_id)

        user_text = (f"<b>• این ربات خصوصی است و برای عضویت، نیاز به لینک دعوت از یکی از اعضای فعلی دارید.</b>"
                     f"\n<b>• لینک دعوت را می‌توانید در بخش تنظیمات ربات پیدا کنید..</b>"
                     f"\n<b>• همچنین می‌توانید با استفاده از دکمه زیر، درخواست عضویت خود را به ادمین ارسال کنید.</b>"
                     f"\n<b>- نکته: با ارسال درخواست، اطلاعات عمومی حساب شما برای ادمین فرستاده میشود </b>")
        update.message.reply_text(text=user_text, reply_markup=InlineKeyboardMarkup(anonymous_key), parse_mode='HTML')

def send_check_new_user_request_to_admin(update: Update, context):
    query = update.callback_query
    user = query.from_user
    photos = context.bot.get_user_profile_photos(user_id=user.id)
    text = (f'👤 User Request to join the BOT\n\n'
            f'User Name: {user.first_name} {user.last_name}\n'
            f'User ID: {user.id}\n'
            f'UserName: @{user.username}\n'
            f'User Language: {user.language_code}\n'
            f'Is User Premium: {user.is_premium}\n'
            f'Is User BOT: {user.is_bot}\n')

    admin_keyboard = [
        [InlineKeyboardButton("Accept User✅", callback_data=f'accept_user_{user.id}'),
         InlineKeyboardButton("Deny User❌", callback_data=f'deny_user_{user.id}')],
    ]

    user_lists_instance.UserData[user.id] = user

    if photos.total_count > 0:
        photo_file_id = photos.photos[0][-1].file_id
        context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo_file_id, caption=text,
                               reply_markup=InlineKeyboardMarkup(admin_keyboard))
    else:
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text + '\n• Without Profile Picture (or not public)',
                                 reply_markup=InlineKeyboardMarkup(admin_keyboard))

    query.answer('درخواست عضویت شما ارسال شد✅')
    query.edit_message_text(text='• ما درخواست شمارو بررسی میکنیم و نتیجه رو از طریق همین ربات اعلام میکنیم، متشکریم!', reply_markup=InlineKeyboardMarkup([]))


def check_new_user_request_by_admin(update: Update, context):
    query = update.callback_query
    chat_id = int(query.data.replace('accept_user_', '').replace('accept_user_', ''))
    user = user_lists_instance.UserData.get(chat_id)

    if 'accept_user_' in query.data:
        create_user(context, user, 'null')
        user_lists_instance.add_user_to_accept_users(user.id)
    else:
        user_lists_instance.add_user_to_deny_users(user.id)

    query.answer('Done ✅')
    query.edit_message_reply_markup(InlineKeyboardMarkup([]))


def main_menu(update, context, send_message=False):
    query = update.callback_query
    user = query.from_user
    data = query.data

    user_text = f"<b>درود <a href='tg://user?id={user['id']}'>{user['first_name']}</a> عزیز، به FreeByte خوش آمدید.\nبرای ادامه بخش مورد نظر خودتون رو انتخاب کنید:\n</b>"
    if not send_message and data == "main_menu":
        query.edit_message_text(text=user_text, reply_markup=InlineKeyboardMarkup(key), parse_mode='HTML')
    else:
        context.bot.send_message(text=user_text, reply_markup=InlineKeyboardMarkup(key), parse_mode='HTML', chat_id=query.message.chat_id)
        query.answer(text="در یک پیام جدید ارسال شد!", show_alert=False)


def main_menu_delete_main_message(update, context):
    query = update.callback_query
    user = query.from_user

    user_text = f"<b>درود <a href='tg://user?id={user['id']}'>{user['first_name']}</a> عزیز، به FreeByte خوش آمدید.\nبرای ادامه بخش مورد نظر خودتون رو انتخاب کنید:\n</b>"
    query.delete_message()
    context.bot.send_message(text=user_text, reply_markup=InlineKeyboardMarkup(key), parse_mode='HTML',
                             chat_id=query.message.chat_id)


def send_main_message(update, context):
    main_menu(update, context, send_message=True)