import sqlite3
from telegram.ext import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from Other import what_lang


def greeting_code(chat_id, query, text_3, lan):
    status = "⚠️"
    button = "⚠️"

    try:
        if text_3[0][0] == "True":
            if lan == "en":
                status = "• It is active now🎉"
                button = "Disable ✗"

            elif lan == "fa":
                status = "• فعال است🎉"
                button = "غیر فعال کردن ✗"

        elif text_3[0][0] == "False":
            if lan == "en":
                status = "• It is inactive now❌"
                button = "Enable ✓"
            elif lan == "fa":
                status = "• غیر فعال است❌"
                button = "فعال کردن ✓"
    except:
        status = "⚠️ bot has not been launched. \n⚠️ start again"

    keyboard_back = [[InlineKeyboardButton(f"{button}", callback_data="change_status")],
                     [InlineKeyboardButton("Back", callback_data="settings")]]
    keyboard_back_fa = [[InlineKeyboardButton(f"{button}", callback_data="change_status")],
                        [InlineKeyboardButton("برگشت", callback_data="settings")]]

    key = keyboard_back
    text = f"‣ By disabling this part, the bot\n‣ will not send birthday greetings:\n\n{status}"

    if lan == "fa":
        key = keyboard_back_fa
        text = f"◂ با غیر فعال کردن این قسمت\n‣ ربات تولد ها را تبریک نمیگوید:\n\n{status}"

    reply_markup = InlineKeyboardMarkup(key)
    try:
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='markdown')
    except:
        pass


def greetings(update, context):
    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()

    query = update.callback_query
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    c.execute("SELECT status FROM Details WHERE chat_id = {0}".format(chat_id))
    text_3 = c.fetchall()

    if query.message.chat.type == "private":
        greeting_code(chat_id, query, text_3, lan)

    else:
        c.execute("SELECT id FROM Specials WHERE chat_id = {0}".format(chat_id))
        text_4 = c.fetchall()  # [["12313441, 13231312312, 133132123"]]

        text_5 = text_4[0][0]
        special_list = text_5.split(", ")

        if str(query.from_user.id) in special_list:
            greeting_code(chat_id, query, text_3, lan)

        else:
            if lan == "en":
                query.answer(text="Sorry, this section only for special group members!")
            elif lan == "fa":
                query.answer(text="ببخشید، این بخش فقط برای اعضای ویژه گروه در دسترسه!")
    conn.close()


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

    conn = sqlite3.connect('Birth.db')
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


def cal_code(chat_id, query, lan, lang):
    status, button = "⚠️", "⚠️"

    try:
        if lan == "True":
            if lang == "fa":
                status = "◂ انتخاب شما: تقویم جلالی 🇮🇷"

            elif lang == "en":
                status = "‣ Chosen: jalali calendar 🇮🇷"

        elif lan == "False":

            if lang == "fa":
                status = "◂ انتخاب شما: تقویم میلادی 🇺🇸"
            elif lang == "en":
                status = "‣ Chosen: Gregorian calendar 🇺🇸"

    except:
        status = "⚠️ bot has not been launched. \n⚠️ start again"

    keyboard_back = [[InlineKeyboardButton("Jalali", callback_data="jala"),
                      InlineKeyboardButton("Gregorian", callback_data="greg")],
                     [InlineKeyboardButton("Back", callback_data="settings")]]

    keyboard_back_fa = [[InlineKeyboardButton("جلالی", callback_data="jala"),
                         InlineKeyboardButton("میلادی", callback_data="greg")],
                        [InlineKeyboardButton("برگشت", callback_data="settings")]]

    text = f"‣ Choose your calendar:\n\n{status}"
    key = keyboard_back

    if lang == "fa":
        text = f"◂ تقویم خود را انتخاب کنید:\n\n{status}"
        key = keyboard_back_fa

    reply_markup = InlineKeyboardMarkup(key)
    try:
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='markdown')
    except:
        pass


def cal(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id

    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()

    c.execute("SELECT status FROM Jalali WHERE chat_id = {0}".format(chat_id))
    calc = c.fetchall()

    ct = query.message.chat.type
    lang = what_lang(chat_id)

    if ct == "private":
        cal_code(chat_id, query, calc[0][0], lang)

    else:

        c.execute("SELECT id FROM Specials WHERE chat_id = {0}".format(chat_id))
        text_4 = c.fetchall()  # [["12313441, 13231312312, 133132123"]]

        text_5 = text_4[0][0]
        special_list = text_5.split(", ")

        if str(query.from_user.id) in special_list:
            cal_code(chat_id, query, calc, lang)

        else:

            if lan == "en":
                query.answer(text="Sorry, this section only for special group members!")
            elif lan == "fa":
                query.answer(text="ببخشید، این بخش فقط برای اعضای ویژه گروه در دسترسه!")
    conn.close()


def reminder_code(chat_id, query, text, lan):
    status = "⚠️"
    button = "⚠️"

    keyboard_back = [[InlineKeyboardButton("Disable ✗", callback_data="ch_remind")],
                     [InlineKeyboardButton("⊲", callback_data="fewer"),
                      InlineKeyboardButton("⊳", callback_data="more")],
                     [InlineKeyboardButton("Back", callback_data="settings")]]

    try:
        if int(text[0][0]) != 0:
            if lan == "en":
                status = f"• The reminder is on✅\n• {text[0][0]} day befor birthday"

                keyboard_back = [[InlineKeyboardButton("Disable ✗", callback_data="ch_remind")],
                                 [InlineKeyboardButton("⊲", callback_data="fewer"),
                                  InlineKeyboardButton("⊳", callback_data="more")],
                                 [InlineKeyboardButton("Back", callback_data="settings")]]
            elif lan == "fa":
                status = f"• یادآوری فعال است✅\n• {text[0][0]} روز قبل از تولد"

                keyboard_back = [[InlineKeyboardButton("غیر فعال کردن ✗", callback_data="ch_remind")],
                                 [InlineKeyboardButton("⊲", callback_data="fewer"),
                                  InlineKeyboardButton("⊳", callback_data="more")],
                                 [InlineKeyboardButton("برگشت", callback_data="settings")]]

        elif int(text[0][0]) == 0:
            if lan == "en":
                status = "• The reminder is off❌"
                keyboard_back = [[InlineKeyboardButton("Enable ✓", callback_data="ch_remind")],
                                 [InlineKeyboardButton("Back", callback_data="settings")]]

            elif lan == "fa":
                status = "• یادآوری غیرفعال است❌"
                keyboard_back = [[InlineKeyboardButton("فعال کردن ✓", callback_data="ch_remind")],
                                 [InlineKeyboardButton("برگشت", callback_data="settings")]]
    except:
        status = "⚠️ bot has not been launched. \n⚠️ start again"

    text = f"‣ If this section is on, bot\n‣ remind you before birthdays:\n\n{status}"

    if lan == "fa":
        text = f"◂ اگر این بخش روشن باشد ربات قبل\n ◂ از تولدها به شما یادآوری میکند:\n\n{status}"

    reply_markup = InlineKeyboardMarkup(keyboard_back)
    try:
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='markdown')
    except:
        pass


def reminder(update, context):
    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()

    query = update.callback_query
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    c.execute("SELECT remind FROM Details WHERE chat_id = {0}".format(chat_id))
    text = c.fetchall()

    if query.message.chat.type == "private":
        reminder_code(chat_id, query, text, lan)

    else:
        c.execute("SELECT id FROM Specials WHERE chat_id = {0}".format(chat_id))
        text_4 = c.fetchall()  # [["12313441, 13231312312, 133132123"]]

        text_5 = text_4[0][0]
        special_list = text_5.split(", ")

        if str(query.from_user.id) in special_list:
            reminder_code(chat_id, query, text, lan)

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
    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()

    query = update.callback_query
    chat_id = query.message.chat_id

    c.execute("SELECT permission FROM Details WHERE chat_id = {0}".format(chat_id))
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


def change_status(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    button, status, key = "⚠️", "⚠️", ""

    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()

    c.execute("SELECT status FROM Details WHERE chat_id = {0}".format(chat_id))
    text = c.fetchall()

    lan = what_lang(chat_id)

    if query.data == "change_status":
        if text[0][0] == "True":
            c.execute("Update Details set status = 'False' where chat_id = {0}".format(chat_id))
            conn.commit()

            if lan == "en":
                status = "• It is inactive now❌"
                button = "Enable ✓"
            elif lan == "fa":
                status = "• غیر فعال است❌"
                button = "فعال کردن ✓"

        elif text[0][0] == "False":
            c.execute("Update Details set status = 'True' where chat_id = {0}".format(chat_id))
            conn.commit()
            if lan == "en":
                status = "• It is active now🎉"
                button = "Disable ✗"

            elif lan == "fa":
                status = "• فعال است🎉"
                button = "غیر فعال کردن ✗"

    keyboard_status = [[InlineKeyboardButton(f"{button}", callback_data="change_status")],
                       [InlineKeyboardButton("Back", callback_data="settings")]]
    keyboard_status_fa = [[InlineKeyboardButton(f"{button}", callback_data="change_status")],
                          [InlineKeyboardButton("برگشت", callback_data="settings")]]
    text = f"‣ By disabling this part, the bot\n‣ will not sensd birthday greetings:\n\n{status}"
    key = keyboard_status

    if lan == "fa":
        key = keyboard_status_fa
        text = f"‣ با غیر فعال کردن این قسمت\n‣ ربات تولد ها را تبریک نمیگوید:\n\n{status}"

    reply_markup = InlineKeyboardMarkup(key)

    try:
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='markdown')
    except:
        pass
    conn.close()


def change_language(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    status = "⚠️"

    conn = sqlite3.connect('Birth.db')
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


def change_cal(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    status = "⚠️"

    keyboard_lan = [[InlineKeyboardButton("Jalali", callback_data="jala"),
                     InlineKeyboardButton("Gregorian", callback_data="greg")],
                    [InlineKeyboardButton("Back", callback_data="settings")]]

    keyboard_lan_fa = [[InlineKeyboardButton("جلالی", callback_data="jala"),
                        InlineKeyboardButton("میلادی", callback_data="greg")],
                       [InlineKeyboardButton("برگشت", callback_data="settings")]]

    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()

    lan = what_lang(chat_id)

    if query.data == "greg":
        c.execute("Update Jalali set status = 'False' where chat_id = {0}".format(chat_id))
        conn.commit()
        status = "‣ Chosen: Gregorian calendar 🇺🇸"
        if lan == "fa":
            status = "◂ انتخاب شما: تقویم میلادی 🇺🇸"

    elif query.data == "jala":
        c.execute("Update Jalali set status = 'True' where chat_id = {0}".format(chat_id))
        conn.commit()
        status = "‣ Chosen: jalali calendar 🇮🇷"
        if lan == "fa":
            status = "◂ انتخاب شما: تقویم جلالی 🇮🇷"

    text = f"‣ Choose your calendar:\n\n{status}"
    key = keyboard_lan

    if lan == "fa":
        text = f"◂ تقویم خود را انتخاب کنید:\n\n{status}"
        key = keyboard_lan_fa

    reply_markup = InlineKeyboardMarkup(key)
    try:
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='markdown')
    except:
        pass
    conn.close()


def change_reminder(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    status = "⚠️"

    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()

    lan = what_lang(chat_id)

    c.execute("SELECT remind FROM Details WHERE chat_id = {0}".format(chat_id))
    text = c.fetchall()

    keyboard_back = [[InlineKeyboardButton("Disable ✗", callback_data="ch_remind")],
                     [InlineKeyboardButton("⊲", callback_data="fewer"),
                      InlineKeyboardButton("⊳", callback_data="more")],
                     [InlineKeyboardButton("Back", callback_data="settings")]]
    keyboard_back_2 = [[InlineKeyboardButton("Enable ✓", callback_data="ch_remind")],
                       [InlineKeyboardButton("Back", callback_data="settings")]]
    keyboard_back_fa = [[InlineKeyboardButton("غیر فعال کردن ✗", callback_data="ch_remind")],
                        [InlineKeyboardButton("⊲", callback_data="fewer"),
                         InlineKeyboardButton("⊳", callback_data="more")],
                        [InlineKeyboardButton("برگشت", callback_data="settings")]]
    keyboard_back_2_fa = [[InlineKeyboardButton("فعال کردن ✓", callback_data="ch_remind")],
                          [InlineKeyboardButton("برگشت", callback_data="settings")]]

    key = keyboard_back

    if query.data == "ch_remind":
        if int(text[0][0]) == 0:
            c.execute("Update Details set remind = '7' where chat_id = {0}".format(chat_id))
            conn.commit()

            status = f"• The reminder is on✅\n• 7 day befor birthday"

            if lan == "fa":
                status = f"• یادآوری فعال است✅\n• 7 روز قبل از تولد"
                key = keyboard_back_fa

        elif int(text[0][0]) != 0:

            c.execute("Update Details set remind = '0' where chat_id = {0}".format(chat_id))
            conn.commit()

            status = "• The reminder is off❌"
            key = keyboard_back_2

            if lan == "fa":
                status = "• یادآوری غیرفعال است❌"
                key = keyboard_back_2_fa

    elif query.data == "fewer":

        if int(text[0][0]) != 0 and int(text[0][0]) > 1:
            number_1 = int(text[0][0])
            number_2 = number_1 - 1
            number_3 = str(number_2)

            status = f"• The reminder is on✅\n• {number_2} day befor birthday"

            c.execute("Update Details set remind = {0} where chat_id = {1}".format(number_3, chat_id))
            conn.commit()

            if lan == "fa":
                status = f"• یادآوری فعال است✅\n• {number_2} روز قبل از تولد"

                key = keyboard_back_fa

        elif int(text[0][0]) <= 1:
            if lan == "en":
                status = f'• The reminder is on✅\n• 1 day befor birthday'
                query.answer(text="It cannot be lower!")

            elif lan == "fa":
                status = f"• یادآوری فعال است✅\n• 1 روز قبل از تولد"
                key = keyboard_back_fa
                query.answer(text="کمتر از این نمیشه!")

    elif query.data == "more":

        if int(text[0][0]) != 0 and int(text[0][0]) < 30:
            number_1 = int(text[0][0])
            number_2 = number_1 + 1
            number_3 = str(number_2)

            status = f"• The reminder is on✅\n• {number_2} day befor birthday"

            if lan == "fa":
                status = f"• یادآوری فعال است✅\n• {number_2} روز قبل از تولد"

                key = keyboard_back_fa

            c.execute("Update Details set remind = {0} where chat_id = {1}".format(number_3, chat_id))
            conn.commit()

        elif int(text[0][0]) >= 30:
            if lan == "en":
                status = f"• The reminder is on✅\n• 30 day befor birthday"
                query.answer(text="It cannot be more!")

            if lan == "fa":
                status = f"• یادآوری فعال است✅\n• 30 روز قبل از تولد"
                key = keyboard_back_fa
                query.answer(text="بیشتر از این نمیشه!")

    text = f"‣ If this section is on, bot\n‣ remind you before birthdays:\n\n{status}"

    if lan == "fa":
        text = f"◂ اگر این بخش روشن باشد ربات قبل از\n ◂ تولدها به شما یادآوری میکند:\n\n{status}"

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

    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()

    lang = what_lang(chat_id)

    if query.data == "all":
        c.execute("Update Details set permission = 'All' where chat_id = {0}".format(chat_id))
        conn.commit()
        status = "All - Everyone can"
        if lang == "fa": status = "همه - همه میتوانند"

    elif query.data == "spec":
        c.execute("Update Details set permission = 'Special' where chat_id = {0}".format(chat_id))
        conn.commit()
        status = "Special - Special users only"
        if lang == "fa": status = "ویژه - فقط کاربران ویژه"

    elif query.data == "admin":
        c.execute("Update Details set permission = 'Admins' where chat_id = {0}".format(chat_id))
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

    query = update.callback_query
    chat_id = query.message.chat_id

    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()

    if query.data == "cs_1":
        text = """

"""