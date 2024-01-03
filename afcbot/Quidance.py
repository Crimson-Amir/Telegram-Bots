import sqlite3
from telegram.ext import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from Other import what_lang


def permissions(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    query.answer()

    lan = what_lang(chat_id)

    keyboard_back = [[InlineKeyboardButton("Back", callback_data="guidance")]]
    keyboard_back_fa = [[InlineKeyboardButton("برگشت", callback_data="guidance")]]

    key = keyboard_back
    text = """
• Birth registration permission:

+ `add special` (reply)
- Add special user

+ `remove special` (reply)
- Remove special user

+ `special list`
- get special list

+ `per special` 
- Only special user can register
- births and use bot commands

+ `per everyone`
- Everyone can use bot commands

+ `per admin`
- just group manager can use bot
"""

    if lan == "fa":
        key = keyboard_back_fa
        text = """
• مشخص کنید چه کسانی به ثبت تولد دسترسی داشته باشند:

+ `اضافه کردن ویژه`
- کاربر ویژه اضافه کنید

+ `حذف ویژه`
- کاربر ویژه را حذف کنید

+ `لیست کاربران ویژه`
- کاربران ویژه را مشاهده کنید

+ `مجوز ویژه` 
- فقط کاربران ویژه میتوانند تولد
- ثبت کنند و از ربات استفاده کنند

+ `مجوز همه`
- همه میتوانند از ربات استفاده کنند

+ `مجوز ادمین`
- فقط ادمین ها میتوانند تولد ثبت کنند
"""

    reply_markup = InlineKeyboardMarkup(key)
    try:
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='markdown')
    except:
        pass
