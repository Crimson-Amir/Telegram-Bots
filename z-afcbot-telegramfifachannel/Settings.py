import sqlite3
from telegram.ext import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from Other import what_lang


def langueg_code(chat_id, query, lan):
    status, button = "⚠️", "⚠️"

    try:
        if lan == "fa":
            status = "◂ انتخاب شما: فارسی 🇮🇷"

        elif lan == "en":
            status = "‣ Chosen: english 🇺🇸"

    except:
        status = "⚠️ bot has not been launched. \n⚠️ start again"

    keyboard_back = [[InlineKeyboardButton("🇮🇷", callback_data="ir"),
                      InlineKeyboardButton("🇺🇸", callback_data="us")],
                     [InlineKeyboardButton("Back", callback_data="settings")]]
    keyboard_back_fa = [[InlineKeyboardButton("🇮🇷", callback_data="ir"),
                         InlineKeyboardButton("🇺🇸", callback_data="us")],
                        [InlineKeyboardButton("برگشت", callback_data="settings")]]
    text = f"‣ Choose your language:\n\n{status}"
    key = keyboard_back

    if lan == "fa":
        text = f"◂ زبان خود را انتخاب کنید:\n\n{status}"
        key = keyboard_back_fa

    reply_markup = InlineKeyboardMarkup(key)
    try:
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='markdown')
    except:
        pass


def language(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id

    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()

    lan = what_lang(chat_id)

    ct = query.message.chat.type

    if ct == "private":
        langueg_code(chat_id, query, lan)

    else:

        c.execute("SELECT id FROM Specials WHERE chat_id = {0}".format(chat_id))
        text_4 = c.fetchall()  # [["12313441, 13231312312, 133132123"]]

        text_5 = text_4[0][0]
        special_list = text_5.split(", ")

        if str(query.from_user.id) in special_list:
            langueg_code(chat_id, query, lan)

        else:

            if lan == "en":
                query.answer(text="Sorry, this section only for special group members!")
            elif lan == "fa":
                query.answer(text="ببخشید، این بخش فقط برای اعضای ویژه گروه در دسترسه!")
    conn.close()


def status_permission_code(chat_id, query, text, lan):
    status = "⚠️"
    button = "⚠️"

    try:

        if text[0][0] == "All":
            status = "All - Everyone can"
            if lan == "fa": status = "همه - همه میتوانند"

        elif text[0][0] == "Special":
            status = "Special - Special users only"
            if lan == "fa": status = "ویژه - فقط کاربران ویژه"

        elif text[0][0] == "Admins":
            status = "Admin - Group Admins only"
            if lan == "fa": status = "ادمین - فقط ادمین ها"

    except:
        status = "⚠️ bot has not been launched. \n⚠️ start again"

    keyboard_back = [[InlineKeyboardButton("All", callback_data="all"),
                      InlineKeyboardButton("Special", callback_data="spec")],
                     [InlineKeyboardButton("Admins", callback_data="admin"),
                      InlineKeyboardButton("Back", callback_data="settings")]]

    keyboard_back_fa = [[InlineKeyboardButton("همه", callback_data="all"),
                         InlineKeyboardButton("ویژه ها", callback_data="spec")],
                        [InlineKeyboardButton("ادمین ها", callback_data="admin"),
                         InlineKeyboardButton("برگشت", callback_data="settings")]]
    text = f"‣ Determine who can use the bot \n\n• Permission to use only for:• \n{status}"
    key = keyboard_back

    if lan == "fa":
        text = f"◂ مشخص کنید چه کسانی از ربات استفاده کنند \n\n• اجازه دسترسی فقط برای: \n{status}"
        key = keyboard_back_fa

    reply_markup = InlineKeyboardMarkup(key)
    try:
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='markdown')
    except:
        pass


def status_permission(update, context):
    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()

    query = update.callback_query
    chat_id = query.message.chat_id

    c.execute("SELECT permison FROM Per WHERE chat_id = {0}".format(chat_id))
    text = c.fetchall()

    lan = what_lang(chat_id)

    if query.message.chat.type == "private":
        if lan == "en":
            query.answer(text="This is only available for groups! 👥")
        elif lan == "fa":
            query.answer(text="این بخش فقط برای گروه ها در دسترس است! 👥")


    else:
        c.execute("SELECT id FROM Specials WHERE chat_id = {0}".format(chat_id))

        text_4 = c.fetchall()  # [["12313441, 13231312312, 133132123"]]
        text_5 = text_4[0][0]
        special_list = text_5.split(", ")

        if str(query.from_user.id) in special_list:
            status_permission_code(chat_id, query, text, lan)

        else:
            if lan == "en":
                query.answer(text="Sorry, this section only for special group members!")
            elif lan == "fa":
                query.answer(text="ببخشید، این بخش فقط برای اعضای ویژه گروه در دسترسه!")

    conn.close()


def change_language(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    status = "⚠️"

    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()

    if query.data == "us":
        c.execute("Update Languages set lang = 'en' where chat_id = {0}".format(chat_id))
        conn.commit()
        status = "‣ Chosen: english 🇺🇸"
    elif query.data == "ir":
        c.execute("Update Languages set lang = 'fa' where chat_id = {0}".format(chat_id))
        conn.commit()
        status = "◂ انتخاب شما: فارسی 🇮🇷"

    keyboard_lan_fa = [[InlineKeyboardButton("🇮🇷", callback_data="ir"),
                        InlineKeyboardButton("🇺🇸", callback_data="us")],
                       [InlineKeyboardButton("برگشت", callback_data="settings")]]
    keyboard_lan = [[InlineKeyboardButton("🇮🇷", callback_data="ir"),
                     InlineKeyboardButton("🇺🇸", callback_data="us")],
                    [InlineKeyboardButton("Back", callback_data="settings")]]

    lan = what_lang(chat_id)

    text = f"‣ Choose your language:\n\n{status}"
    key = keyboard_lan

    if lan == "fa":
        text = f"◂ زبان خود را انتخاب کنید:\n\n{status}"
        key = keyboard_lan_fa

    reply_markup = InlineKeyboardMarkup(key)
    try:
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='markdown')
    except:
        pass
    conn.close()


def change_permisson(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    status = "⚠️"

    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()

    lang = what_lang(chat_id)

    if query.data == "all":
        c.execute("Update Per set permison = 'All' where chat_id = {0}".format(chat_id))
        conn.commit()
        status = "All - Everyone can"
        if lang == "fa": status = "همه - همه میتوانند"

    elif query.data == "spec":
        c.execute("Update Per set permison = 'Special' where chat_id = {0}".format(chat_id))
        conn.commit()
        status = "Special - Special users only"
        if lang == "fa": status = "ویژه - فقط کاربران ویژه"

    elif query.data == "admin":
        c.execute("Update Per set permison = 'Admins' where chat_id = {0}".format(chat_id))
        conn.commit()
        status = "Admin - Group Admins only"
        if lang == "fa": status = "ادمین - فقط ادمین ها"

    keyboard_new_fa = [[InlineKeyboardButton("همه", callback_data="all"),
                        InlineKeyboardButton("ویژه ها", callback_data="spec")],
                       [InlineKeyboardButton("ادمین ها", callback_data="admin"),
                        InlineKeyboardButton("برگشت", callback_data="settings")]]

    keyboard_new = [[InlineKeyboardButton("All", callback_data="all"),
                     InlineKeyboardButton("Special", callback_data="spec")],
                    [InlineKeyboardButton("Admins", callback_data="admin"),
                     InlineKeyboardButton("Back", callback_data="settings")]]

    key = keyboard_new
    text2 = f"‣ Determine who can use the bot \n\n• Permission to use only for:• \n{status}"

    if lang == "fa":
        text2 = f"◂ مشخص کنید چه کسانی از ربات استفاده کنند \n\n• اجازه دسترسی فقط برای: \n{status}"
        key = keyboard_new_fa

    reply_markup = InlineKeyboardMarkup(key)
    try:
        query.edit_message_text(text=text2, reply_markup=reply_markup, parse_mode='markdown')
    except:
        pass
    conn.close()
