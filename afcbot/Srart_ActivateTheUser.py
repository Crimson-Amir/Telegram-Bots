import sqlite3
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import *
from datetime import datetime
import pytz
from keyboards import keyboard, keyboard_fa, lang_key
from Other import what_lang


def get_data(name, limit=1):
    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()
    c.execute("SELECT * FROM {0} ORDER BY id DESC LIMIT {1}".format(name, limit))
    if limit != 1:
        info = c.fetchall()
    else:
        info = c.fetchone()
    conn.commit()
    conn.close()
    return info


def button(update, context):
    query = update.callback_query

    if query.data == 'start_bot':
        context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        select_lang(update, context)


def restrict_to_channel_members(func):
    def wrapper(update, context):
        chat_id = "@FcMobile_Everlasting"
        bot = context.bot
        t = get_data('Join_Text')
        try:
            lan = what_lang(update.message.chat_id)
            user_id = update.message.from_user
            chid = update.message.chat_id
            sn = update.message.reply_text
        except:
            query = update.callback_query
            lan = what_lang(query.message.chat_id)
            user_id = query.from_user
            chid = query.message.chat_id
            sn = query.edit_message_text

        # try:
        member = bot.get_chat_member(chat_id, user_id.id)
        if member.status in ["left", "kicked"]:
            text = f"""سلام <a href="tg://user?id={str(user_id['id'])}">{user_id['first_name']}</a> عزیز، {t}"""
            join = [[InlineKeyboardButton("عضویت در کانال | Join Channel", url="https://t.me/FcMobile_Everlasting")],
                    [InlineKeyboardButton("بررسی عضویت | Check", callback_data='start_bot')]]
            sn(text=text, reply_markup=InlineKeyboardMarkup(join), parse_mode="html")
        else:
            return func(update, context)
        # except Exception as e:
        #     print(e)
        #     query.edit_message_text(text="An error occurred.")

    return wrapper


def bot_start(update, context):
    query = update.callback_query
    user = query.from_user
    date = str(datetime.now().strftime("UTC-%H:%M:%S-%Y/%m/%d"))
    chat_id = str(query.message.chat_id)
    ct = query.message.chat.type
    chat_info = context.bot.get_chat(chat_id)
    member_count = context.bot.get_chat_member_count(chat_id)
    print(date + query.data)
    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()

    c.execute("INSERT INTO Languages VALUES(?,?)", (query.data, chat_id))
    conn.commit()

    lan = what_lang(chat_id)
    start_text = get_data('Bot_Main_Text')

    if ct == "private":

        # user_text = f"""Hello, dear <a href="tg://user?id={user['id']}">{user['first_name']}</a>. {start_text[2]}"""
        user_text = "Coming Soon"
        key = keyboard
        if lan == "fa":
            user_text = f"""سلام، <a href="tg://user?id={str(user['id'])}">{user['first_name']}</a> عزیز. {start_text[1]}"""
            key = keyboard_fa

        text = f"""New Start Bot In <B>Privet Chat</B>\n\nName: {user['first_name']}\nUserName: @{user['username']}\nID: <a href="tg://user?id={user['id']}">{user['id']}</a>\nDate: {date}\nLanguages: {lan}"""

        query.edit_message_text(text=user_text, reply_markup=InlineKeyboardMarkup(key), parse_mode='HTML')
        context.bot.send_message(chat_id=5820447488, text=text, parse_mode='HTML')

    if ct == "group" or ct == "supergroup" or ct == "channel":

        text_2 = f"""Coming Soon"""
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
        context.bot.send_message(chat_id=5820447488, text=text, parse_mode='HTML')

    c.execute("INSERT INTO Per VALUES(?, ?)", ("All", chat_id))
    conn.commit()
    conn.close()


@restrict_to_channel_members
def select_lang(update, context):
    try:
        user = update.message.from_user
        chat_id = str(update.message.chat_id)
        chat_type = update.message.chat.type
        chat_memebers = update.message.new_chat_members
        ch_ty = update.message.chat.type
    except:
        query = update.callback_query
        print(query.data)
        user = query.from_user
        chat_id = str(query.message.chat_id)
        chat_type = query.message.chat.type
        chat_memebers = query.message.new_chat_members
        ch_ty = query.message.chat.type

    date = str(datetime.now(pytz.timezone('Asia/Tehran')).strftime("+3:30-%H:%M:%S-%Y/%m/%d"))
    chat_info = context.bot.get_chat(chat_id)
    member_count = context.bot.get_chat_member_count(chat_id)

    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()

    c.execute("SELECT lang FROM Languages WHERE chat_id = {0}".format(chat_id))
    text = c.fetchall()

    start_text = get_data('Bot_Main_Text')

    if len(text) == 0:
        text = "• Choose your language:\n• زبان خود را انتخاب کنید:"
        key = [[InlineKeyboardButton("English 🇺🇸", callback_data='en'),
                InlineKeyboardButton("️Persian 🇮🇷", callback_data='fa')]]

        if chat_type == "private":
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

        if chat_type == "private":
            context.bot.send_message(chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
            c.execute("INSERT INTO Pv_Data VALUES(?,?,?,?)",
                      (user["first_name"], user["username"], user["id"], str(date)))
            conn.commit()
        for member in chat_memebers:
            if member.id == context.bot.id:
                c.execute("INSERT INTO GroupData VALUES(?,?,?,?,?,?)",
                          (chat_info["title"], chat_info["username"], chat_info["id"], user["id"], str(date),
                           member_count))
                conn.commit()

                context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))

    elif len(text) != 0:
        lan = text[0][0]
        key = ""
        user_text = ""
        text_2 = ""
        start_text = get_data('Bot_Main_Text')
        if ch_ty == "private":

            if lan == "en":
                user_text = "Coming Soon"
                key = keyboard
            elif lan == "fa":
                user_text = f"""سلام، <a href="tg://user?id={str(user['id'])}">{user['first_name']}</a> عزیز. {start_text[1]}"""
                key = keyboard_fa
            context.bot.send_message(text=user_text, reply_markup=InlineKeyboardMarkup(key), parse_mode='HTML', chat_id=chat_id)

        if ch_ty == "group" or ch_ty == "supergroup" or ch_ty == "channel":
            for member in chat_memebers:
                if member.id == context.bot.id:
                    if lan == "en":
                        text_2 = "Coming Soon"
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

    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()

    lan = what_lang(chat_id)
    start_text = get_data('Bot_Choice_Text')
    text = "Coming Soon"
    key = keyboard

    if lan == "fa":
        text = f"""سلام، <a href="tg://user?id={str(user['id'])}">{user['first_name']}</a> عزیز. {start_text[1]}"""
        key = keyboard_fa

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='HTML')
    conn.close()


@restrict_to_channel_members
def help_bot(update, context):
    user = update.message.from_user
    chat_id = update.message.chat_id

    lan = what_lang(chat_id)
    start_text = get_data('Bot_Choice_Text')

    text = "Coming Soon"
    key = keyboard

    if lan == "fa":
        text = f"""سلام، <a href="tg://user?id={str(user['id'])}">{user['first_name']}</a> عزیز. {start_text[1]}"""
        key = keyboard_fa

    update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='HTML')
