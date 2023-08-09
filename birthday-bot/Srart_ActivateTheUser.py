import sqlite3
from telegram import InlineKeyboardMarkup
from telegram.ext import *
from datetime import datetime
import pytz
from keyboards import keyboard, keyboard_fa, lang_key
from Other import what_lang


def bot_start(update, context):
    query = update.callback_query
    user = query.from_user
    date = str(datetime.now().strftime("UTC-%H:%M:%S-%Y/%m/%d"))
    chat_id = str(query.message.chat_id)
    ct = query.message.chat.type
    chat_info = context.bot.get_chat(chat_id)
    member_count = context.bot.get_chat_member_count(chat_id)

    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()

    if query.data == "en":
        c.execute("INSERT INTO Languages VALUES(?,?)", (query.data, chat_id))
        c.execute("INSERT INTO Jalali VALUES(?, ?)",
                  ("False", chat_id))
        conn.commit()
    if query.data == "fa":
        c.execute("INSERT INTO Languages VALUES(?,?)", (query.data, chat_id))
        c.execute("INSERT INTO Jalali VALUES(?, ?)",
                  ("True", chat_id))
        conn.commit()

    c.execute("INSERT INTO Details VALUES(?, ?, ?, ?)",
              ("7", "All", "True", chat_id))
    conn.commit()

    lan = what_lang(chat_id)

    if ct == "private":

        user_text = f"""
Hello, dear <a href="tg://user?id={str(user['id'])}">{user['first_name']}</a>.
\n‣ Some features are for group
‣ For Full Use Bot Must Be Admin
\n<B>• Select the desired section:</B>
"""
        key = keyboard
        if lan == "fa":
            user_text = f"""
سلام، <a href="tg://user?id={str(user['id'])}">{user['first_name']}</a> عزیز.

◂ بعضی ویژگی ها برای گروه ها است
◂ برای استفاده کامل، ربات باید مدیر باشد

<B>• بخش مورد نظر خود را انتخاب کنید:</B>
"""
            key = keyboard_fa

        text = f"""New Start Bot In <B>Privet Chat</B>\n\nName: {user['first_name']}\nUserName: @{user['username']}\nID: <a href="tg://user?id={user['id']}">{user['id']}</a>\nDate: {date}\nLanguages: {lan}"""

        query.edit_message_text(text=user_text, reply_markup=InlineKeyboardMarkup(key), parse_mode='HTML')
        context.bot.send_message(chat_id="6010442497", text=text, parse_mode='HTML')

    if ct == "group" or ct == "supergroup" or ct == "channel":

        text_2 = f"""
Bot Activated Successfully✅
\n<b>‣ Select the desired section:</b>
"""
        key = keyboard
        if lan == "fa":
            text_2 = f"""
            ربات با موفقیت فعال شد ✅
            \n<B>◂ بخش مورد نظر خود را انتخاب کنید:</B>
            """
            key = keyboard_fa

        c.execute("SELECT user_id FROM GroupData WHERE chat_id = {0}".format(chat_id))
        text_id = c.fetchall()

        text = f"""New Start Bot In <B>{query.message.chat.type}</B>\n\nName: {chat_info['title']}\nUserName: @{chat_info['username']}\nID: {str(chat_info['id'])}\nDate: {date}\n\nBot Adder ID: <a href="tg://user?id={text_id[0][0]}">{text_id[0][0]}</a>\nmember count: {member_count}\nLanguages: {lan}"""

        query.edit_message_text(text=text_2, reply_markup=InlineKeyboardMarkup(key), parse_mode="HTML")
        context.bot.send_message(chat_id="6010442497", text=text, parse_mode='HTML')

    conn.close()


def select_lang(update, context):
    user = update.message.from_user
    chat_id = str(update.message.chat_id)
    date = str(datetime.now(pytz.timezone('Asia/Tehran')).strftime("+3:30-%H:%M:%S-%Y/%m/%d"))
    chat_info = context.bot.get_chat(chat_id)
    member_count = context.bot.get_chat_member_count(chat_id)

    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()

    c.execute("SELECT lang FROM Languages WHERE chat_id = {0}".format(chat_id))
    text = c.fetchall()

    # c.execute("DELETE FROM Languages WHERE chat_id = {0}".format(chat_id))
    # conn.commit()

    if len(text) == 0:
        text = "• Choose your language:"
        reply_markup = InlineKeyboardMarkup(lang_key)

        if update.message.chat.type == "private":
            admin_list = ""
            admin_list += str(user['id'])
        else:
            admin = context.bot.get_chat_administrators(chat_id)
            admin_list = ""
            admin_list += str(user['id'])
            for a in admin:
                if str(a.user.id) not in admin_list:
                    admin_list += f", {str(a.user.id)}"

        c.execute("INSERT INTO Specials VALUES(?,?)",
                  (admin_list, chat_id))
        conn.commit()

        if update.message.chat.type == "private":
            context.bot.send_message(chat_id, text=text, reply_markup=reply_markup)
            c.execute("INSERT INTO Pv_Data VALUES(?,?,?,?)",
                      (user["first_name"], user["username"], user["id"], str(date)))
            conn.commit()
        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                c.execute("INSERT INTO GroupData VALUES(?,?,?,?,?,?)",
                          (chat_info["title"], chat_info["username"], chat_info["id"], user["id"], str(date),
                           member_count))
                conn.commit()

                context.bot.send_message(chat_id, text=text, reply_markup=reply_markup)


    elif len(text) != 0:
        lan = text[0][0]
        key = ""
        user_text = ""
        text_2 = ""

        if update.message.chat.type == "private":

            if lan == "en":
                user_text = f"""
Hello, dear <a href="tg://user?id={str(user['id'])}">{user['first_name']}</a>.
\n‣ Some features are for group
‣ For Full Use Bot Must Be Admin
\n<B>• Select the desired section:</B>
"""
                key = keyboard
            elif lan == "fa":
                user_text = f"""
سلام، <a href="tg://user?id={str(user['id'])}">{user['first_name']}</a> عزیز.

◂ بعضی ویژگی ها برای گروه ها است
◂ برای استفاده کامل، ربات باید مدیر باشد

<B>• بخش مورد نظر خود را انتخاب کنید:</B>
"""
                key = keyboard_fa
            update.message.reply_text(text=user_text, reply_markup=InlineKeyboardMarkup(key), parse_mode='HTML')

        if update.message.chat.type == "group" or update.message.chat.type == "supergroup" or update.message.chat.type == "channel":
            for member in update.message.new_chat_members:
                if member.id == context.bot.id:
                    if lan == "en":
                        text_2 = f"""
                Bot Activated Successfully✅
                \n<b>‣ Select the desired section:</b>
                """
                        key = keyboard
                    elif lan == "fa":
                        text_2 = f"""
                            ربات با موفقیت فعال شد ✅
                            \n<B>◂ بخش مورد نظر خود را انتخاب کنید:</B>
                            """
                        key = keyboard_fa
                    context.bot.send_message(chat_id=chat_id, text=text_2, reply_markup=InlineKeyboardMarkup(key),
                                             parse_mode="HTML")

    conn.close()


def choose(update, context):
    query = update.callback_query
    query.answer()
    chat_id = str(query.message.chat_id)
    user = query.from_user

    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()

    lan = what_lang(chat_id)

    text = f"""Hello, dear <a href="tg://user?id={user['id']}">{user['first_name']}</a>.\n\n<B>‣ Select the desired section:</B>"""
    key = keyboard

    if lan == "fa":
        text = f"""سلام، <a href="tg://user?id={str(user['id'])}">{user['first_name']}</a> عزیز.\n\n<B>◂ بخش مورد نظر خود را انتخاب کنید:</B>"""
        key = keyboard_fa

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='HTML')
    conn.close()


def help_bot(update, context):
    user = update.message.from_user
    chat_id = update.message.chat_id

    lan = what_lang(chat_id)

    text = f"""Hello, dear <a href="tg://user?id={str(user['id'])}">{user['first_name']}</a>.\n\n<b>‣ Select the desired section:</b>"""
    key = keyboard

    if lan == "fa":
        text = f"""سلام، <a href="tg://user?id={str(user['id'])}">{user['first_name']}</a> عزیز.\n\n<B>• بخش مورد نظر خود را انتخاب کنید:</B>"""
        key = keyboard_fa

    update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='HTML')