import sqlite3
from telegram.ext import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from Other import what_lang


def set_birthday_ways(update, context):
    keyboard_2 = [[InlineKeyboardButton("Text", callback_data="1set_birthday_text"),
                   InlineKeyboardButton("Video", callback_data="2set_birthday_video")],
                  [InlineKeyboardButton("Back", callback_data="choose")]]
    keyboard_fa_2 = [[InlineKeyboardButton("متن", callback_data="1set_birthday_text"),
                      InlineKeyboardButton("ویدیو", callback_data="2set_birthday_video")],
                     [InlineKeyboardButton("برگشت", callback_data="choose")]]

    query = update.callback_query
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    key = keyboard_2
    text = "• Learn how to set birth:"

    if lan == "fa":
        text = "• یاد بگیرید چگونه تولد ثبت کنید:"
        key = keyboard_fa_2

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='markdown')


def set_birthday_text(update, context):
    keyboard_3 = [[InlineKeyboardButton("Back", callback_data="set_birthday")]]
    keyboard_fa_3 = [[InlineKeyboardButton("برگشت", callback_data="set_birthday")]]

    query = update.callback_query
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    key_2 = keyboard_3

    if query.message.chat.type == "private":
        text = """
Use this command to register a birth:

‣ `set name username day month`

+ name:
- The name of the person
+ username:
- user name of person-can be anything
+ day:
- Person's birth day
+ month:
- Person's birth month (1-12)

• date must be Gregorian
• The bot clock is UTC +3:30
• bot remind you at 12AM that day
• To delete, view etc., you can
• go to the See Births section
• if user does not have a username,
• you can put name again in this field

*Go to settings to change modes and options*
"""
    else:
        text = """
In groups, you can register birth in two ways.

First way:

reply to user and Use this command:

‣ `set day month`

Second Way:

Use this command to register a birth:

‣ `set name username day month`

Guide:

+ name:
- The name of the person
+ username:
- user name of person-can be anything
+ day:
- Person's birth day
+ month:
- Person's birth month (1-12)

• date must be Gregorian
• The bot clock is UTC +3:30
• bot remind you at 12AM that day
• To delete, view etc., you can
• go to the See Births section
• if user does not have a username,
• you can put name again in this field

"""

    if lan == "fa":
        if query.message.chat.type == "private":
            text = """
از این دستور برای ثبت تولد استفاده کنید:

‣ `set name username day month`

+ نام (name):
- نام شخص مورد نظر
+ یوزنیم (username):
- یوزرنیم شخص - میتواند هرچیزی باشد
+ روز (day):
- روز تولد شخص
+ ماه (month):
- ماه تولد شخص (1-12)

• تاریخ باید میلادی باشد
• ساعت ربات UTC +3:30 است
• ربات در ساعت 00:00 آن روز
• تولد را به شما یادآوری میکند
• برای مشاهده و حذف، میتوانید
• به بخش "مشاهده تولد ها" بروید
• اگر کاربر یوزرنیم ندارد میتوانید
• همان اسم را در این فیلد بگذارید

*می‌توانید برای تغییر قابلیت ها و گزینه های بیشتر به "تنظیمات" بروید*
"""
        else:
            text = """
در گروه ها میتوانید با دو روش تولد ثبت کنید

راه اول:

روی کاربر مورد نظر دستور زیر را ریپلای کنید:

‣ `set day month`

راه دوم:

از این دستور برای ثبت تولد استفاده کنید:

‣ `set name username day month`

راهنما:

+ نام (name):
- نام شخص مورد نظر
+ یوزنیم (username):
- یوزرنیم شخص - میتواند هرچیزی باشد
+ روز (day):
- روز تولد شخص
+ ماه (month):
- ماه تولد شخص (1-12)

• تاریخ باید میلادی باشد
• ساعت ربات UTC +3:30 است
• ربات در ساعت 00:00 آن روز
• تولد را به شما یادآوری میکند
• برای مشاهده و حذف، میتوانید
• به بخش "مشاهده تولد ها" بروید
• اگر کاربر یوزرنیم ندارد میتوانید
• همان اسم را در این فیلد بگذارید

*می‌توانید برای تغییر قابلیت ها و گزینه های بیشتر به "تنظیمات" بروید*
"""
        key_2 = keyboard_fa_3

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key_2), parse_mode='markdown')


def set_birthday_video(update, context):
    keyboard_3 = [[InlineKeyboardButton("Back", callback_data="set_birthday")]]
    keyboard_fa_3 = [[InlineKeyboardButton("برگشت", callback_data="set_birthday")]]

    query = update.callback_query
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    text = 'video send for you <3'
    key_2 = keyboard_3
    if lan == 'fa':
        key_2 = keyboard_fa_3
        text = 'ویدیو برای شما ارسال شد.'

    context.bot.send_video(chat_id, video=open('HowSetBirth.mp4', 'rb'), supports_streaming=True)
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key_2), parse_mode='markdown')


def see_birthday(update, context):
    query = update.callback_query
    chat_id = str(query.message.chat_id)

    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()

    c.execute("SELECT * FROM BirthDays WHERE chat_id={0}".format(chat_id))
    text = c.fetchall()

    lan = what_lang(chat_id)

    conn.commit()
    conn.close()

    keyboard_4 = [[InlineKeyboardButton("Back", callback_data="choose")],
                  [InlineKeyboardButton("Clear Data ⟳", callback_data="clear_data")]]
    keyboard_fa_4 = [[InlineKeyboardButton("برگشت", callback_data="choose")],
                     [InlineKeyboardButton("پاک کردن تولد ها ⟳", callback_data="clear_data")]]

    reply_markup = InlineKeyboardMarkup(keyboard_4)
    no_birthday = 'There is no birthday!'

    if lan == "fa":
        reply_markup = InlineKeyboardMarkup(keyboard_fa_4)
        no_birthday = "تولدی وجود ندارد!"

    result = ""

    try:
        num = 0
        for i in text:
            res = text[num]
            name = res[0]
            username = res[1]
            day = res[2]
            month = res[3]
            result += f"Name: {name} | U_Name: {username}\nDay: {day} | Month: {month}\n ----------------------\n\n"
            num += 1
        if num != 0:
            if lan == "fa":
                result += "\n\n• برای جلوگیری از سوتفاهم، تاریخ ها به صورت میلادی نمایش داده میشوند."
            else:
                result += '\n\n• To avoid misunderstanding, the dates are displayed in Gregorian format.'

        query.edit_message_text(text=result, reply_markup=reply_markup)

    except:
        if query.data == 'see_birthday':
            query.answer(text=no_birthday, show_alert=True)


def support(update, context):
    query = update.callback_query
    query.answer()
    chat_id = str(query.message.chat_id)

    lan = what_lang(chat_id)

    keyboard_3 = [[InlineKeyboardButton("Privet 👤", url="t.me/Amir03727")],
                  [InlineKeyboardButton("GitHub 💻 ", url="github.com/AmirHosein03727"),
                   InlineKeyboardButton("Group 👥", url="t.me/Birthday_Bot2")],
                  [InlineKeyboardButton("Email 📧", url="amirhosein03727@gmail.com"),
                   InlineKeyboardButton("More 📜", url="t.me/Projects37")],
                  [InlineKeyboardButton("Back", callback_data="choose")]]

    keyboard_fa_3 = [[InlineKeyboardButton("پرایوت 👤", url="t.me/Amir03727")],
                     [InlineKeyboardButton("گیت هاب 💻 ", url="github.com/AmirHosein03727"),
                      InlineKeyboardButton("گروه 👥", url="t.me/Birthday_Bot2")],
                     [InlineKeyboardButton("ایمیل 📧", url="amirhosein03727@gmail.com"),
                      InlineKeyboardButton("بیشتر 📜", url="t.me/Projects37")],
                     [InlineKeyboardButton("برگشت", callback_data="choose")]]

    key = keyboard_3
    text = """
To Contact The Developer:

help > support
"""
    if lan == "fa":
        text = """
برای ارتباط با توسعه دهنده:

راهنما > پشتیبانی
"""
        key = keyboard_fa_3

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key))


def guidance(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    keyboard_5 = [[InlineKeyboardButton("BirthDay Orders 🍰", callback_data="birthday_orders")],
                  [InlineKeyboardButton("Information 📑", callback_data="information"),
                   InlineKeyboardButton("permissions 🔑", callback_data="permissions")],
                  [InlineKeyboardButton("Back", callback_data="choose")]]

    keyboard_fa_5 = [[InlineKeyboardButton("دستورات تولد 🍰", callback_data="birthday_orders")],
                     [InlineKeyboardButton("اطلاعات 📑", callback_data="information"),
                      InlineKeyboardButton("مجوزها 🔑", callback_data="permissions")],
                     [InlineKeyboardButton("برگشت", callback_data="choose")]]

    key = keyboard_5
    text = "▸ The Bot Guide is Categorized\n▸ In The Following Sections:\n\n*🔰Some options work for admins*"

    if lan == "fa":
        key = keyboard_fa_5
        text = "◂ قسمت های مختلف ربات\n◂ به شرح زیر دسته بندی شده:\n\n*🔰بعضی دستور‌ها فقط برای ادمین‌ است*"

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='markdown')


def setting(update, context):
    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()
    query = update.callback_query
    query.answer()
    user = query.from_user
    chat_id = query.message.chat_id

    c.execute("SELECT lang FROM Languages WHERE chat_id = {0}".format(chat_id))
    text_2 = c.fetchall()
    c.execute("SELECT remind, permission, status FROM Details WHERE chat_id = {0}".format(chat_id))
    text_3 = c.fetchall()  # [7, special, True]
    c.execute("SELECT status FROM Jalali WHERE chat_id = {0}".format(chat_id))
    text_4 = c.fetchall()

    reminders, permission, status, languages, cal = "⚠️", "⚠️", "⚠️", "⚠️", "⚠️"

    try:
        if int(text_3[0][0]) != 0:
            reminders = "✅"  # Remind
        elif int(text_3[0][0]) == 0:
            reminders = "❌"  # Remind

        permission = text_3[0][1]

        if text_3[0][2] == "True":
            status = "✅"
        elif text_3[0][2] == "False":
            status = "❌"

        lan = text_2[0][0]
        cal = text_4[0][0]

        if cal == "True":
            cal = "Jalali 🇮🇷"
        else:
            cal = "Gregorian 🇺🇸"

        if lan == "en":
            languages = "🇺🇸"
        elif lan == "fa":
            languages = "🇮🇷"

    except:
        lan = "en"

    keyboard_fa_6 = [[InlineKeyboardButton(f"تبریک تولد {status}", callback_data="greetings"),
                      InlineKeyboardButton(f"زبان ربات {languages}", callback_data="language")],
                     [InlineKeyboardButton(f"یادآور تولد {reminders}", callback_data="reminder"),
                      InlineKeyboardButton(f"مجوز ({permission})", callback_data="status_permission")],
                     [InlineKeyboardButton(f"تقویم ({cal})", callback_data="calenders")],
                     [InlineKeyboardButton("برگشت", callback_data="choose")]]

    keyboard_6 = [[InlineKeyboardButton(f"greetings {status}", callback_data="greetings"),
                   InlineKeyboardButton(f"language {languages}", callback_data="language")],
                  [InlineKeyboardButton(f"reminder {reminders}", callback_data="reminder"),
                   InlineKeyboardButton(f"permiss ({permission})", callback_data="status_permission")],
                  [InlineKeyboardButton(f"calendar ({cal})", callback_data="calenders")],
                  [InlineKeyboardButton("Back", callback_data="choose")]]

    key = keyboard_6
    text = f"🎛 Bot configuration section:\n\nYour-ID: `{user['id']}`\nChat-ID: `{chat_id}`"

    if lan == "fa":
        key = keyboard_fa_6
        text = f"🎛 بخش پیکربندی ربات:\n\nآیدی شما: `{user['id']}`\nآیدی چت: `{chat_id}`"

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='markdown')
    conn.close()
