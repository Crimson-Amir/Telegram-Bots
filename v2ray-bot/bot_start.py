import datetime
import pytz
import sqlite3
from telegram import InlineKeyboardMarkup
from private import ADMIN_CHAT_ID
from keyboard import main_key as key


def bot_start(update, context):
    user = update.message.from_user
    chat_id = update.message.chat_id
    date = str(datetime.datetime.now(pytz.timezone('Asia/Tehran')).strftime("%H:%M:%S-%Y/%m/%d"))
    start_text_notif = (f"New Start Bot In <B>{update.message.chat.type}</B>\n\nName: {user['first_name']}\n"
                        f"UserName: @{user['username']}\nID: <a href=\"tg://user?id={user['id']}\">{user['id']}</a>"
                        f"\nDate: {date}")

    conn = sqlite3.connect('v2ray.db')
    c = conn.cursor()

    c.execute("SELECT id FROM User WHERE chat_id = {0}".format(chat_id))
    user_is_available = c.fetchall()

    if len(user_is_available) == 0:
        context.bot.send_message(ADMIN_CHAT_ID, text=start_text_notif, parse_mode="HTML")
        c.execute("INSERT INTO User (name,user_name,chat_id,date,traffic,period,free_service) VALUES (?,?,?,?,?,?,?)",
                  (user["first_name"], user["username"], int(user["id"]), str(date), 10, 7, 0))
        conn.commit()

    user_text = f"<b>سلام <a href='tg://user?id={user['id']}'>{user['first_name']}</a> عزیز، به FreeByte خوش آمدید.\nبرای ادامه بخش مورد نظر خودتون رو انتخاب کنید:\n</b>"
    update.message.reply_text(text=user_text, reply_markup=InlineKeyboardMarkup(key), parse_mode='HTML')
    conn.close()


def main_menu(update, context, send_message=False):
    query = update.callback_query
    user = query.from_user

    user_text = f"<b>سلام <a href='tg://user?id={user['id']}'>{user['first_name']}</a> عزیز، به FreeByte خوش آمدید.\nبرای ادامه بخش مورد نظر خودتون رو انتخاب کنید:\n</b>"
    if not send_message:
        query.edit_message_text(text=user_text, reply_markup=InlineKeyboardMarkup(key), parse_mode='HTML')
    else:
        context.bot.send_message(text=user_text, reply_markup=InlineKeyboardMarkup(key), parse_mode='HTML', chat_id=query.message.chat_id)
        query.answer(text="در یک پیام جدید فرستادم!", show_alert=False)

def send_main_message(update, context):
    main_menu(update, context, send_message=True)