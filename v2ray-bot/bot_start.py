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

        context.bot.send_message(ADMIN_CHAT_ID, text=start_text_notif)
        c.execute("INSERT INTO User VALUES(?,?,?,?)",
                  (user["first_name"], user["username"], int(user["id"]), str(date)))
        conn.commit()

    user_text = f"سلام، <a href='tg://user?id={user['id']}'>{user['first_name']}</a> عزیز.\n• بخش مورد نظر خود را انتخاب کنید:"
    update.message.reply_text(text=user_text, reply_markup=InlineKeyboardMarkup(key), parse_mode='HTML')
    conn.close()
