import sqlite3
from telegram.ext import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from Other import what_lang


def birth_orders(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    query.answer()

    lan = what_lang(chat_id)

    keyboard_back = [[InlineKeyboardButton("Back", callback_data="guidance")]]
    keyboard_back_fa = [[InlineKeyboardButton("برگشت", callback_data="guidance")]]
    text = """
• BirthDay commands and options:

+ `reg reminder` day
- register reminders for birthdays
- day: How many days before
- the birthday, be reminded?

+ `reminder for` username day
- Specify the birthday reminder
- for each person as desired

+ `reminder list`
- See the list of users for whom
- you registered different reminders

+ `reminder off`
- Turn off reminder mode

+ `happy on`
- Enable birthday greetings

+ `happy off`
- Disable birthday greetings

+ `clear births`
- all births are deleted

+ `remove birth` username
- Delete someone's birthday
- If you set birth with Reply
- reply command to the user
"""
    key = keyboard_back

    if lan == "fa":
        text = """
• دستورات و ویژگی های تبریک تولد:

+ `تنظیم یادآور` روز
- برای تولد ها یادآوری ثبت کنید
- روز: چند روز قبل از تولد
- به شما یادآوری شود؟

+ `یادآور برای` یوزرنیم روز
- برای هر شخص به صورت دلخواه
- یادآور ثبت کنید

+ `لیست یادآور`
- لیست کاربرانی که برای آنها یادآور
- های مختلف ثبت کردید را ببینید

+ `یادآور خاموش`
- یادآوری تولد را خاموش کنید

+ `تبریک روشن`
- ربات تولد ها را تبریک میگوید

+ `تبریک خاموش`
- ربات تولد ها را تبریک نمیگوید

+ `پاک کردن تولدها`
- لیست تولد ها خالی میشود

+ `حذف تولد` یوزرنیم
- تولد شخصی را از لیست پاک کنید
- اگر تولد را با ریپلای ثبت کردید
- دستور را روی کاربر ریپلای کنید
"""
        key = keyboard_back_fa

    reply_markup = InlineKeyboardMarkup(key)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='markdown')


def information(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    query.answer()

    keyboard_back = [[InlineKeyboardButton("Back", callback_data="guidance")]]
    keyboard_back_fa = [[InlineKeyboardButton("برگشت", callback_data="guidance")]]

    lan = what_lang(chat_id)

    text = """
• Use this commands for get info:

+ `id` (reply)
- get someone id

+ `chat id`
- get chat id

+ `message id` (reply)
- get message id

+ `chat info`
- get chat information

+ `me info`
- get your info

+ `time`
- getting time

+ `info` (reply)
- get someone info

+ `status`
- get bot status 

    """
    key = keyboard_back

    if lan == "fa":
        text = """
• از این دستورات برای گرفتن اطلاعات استفاده کنید:

+ `آیدی` (ریپلای)
- گرفتن آیدی کسی

+ `آیدی چت`
- گرفتن آیدی چت

+ `آیدی پیام` (ریپلای)
- گرفتن آیدی پیام

+ `اطلاعات چت`
- گرفتن اطلاعات چت

+ ` اطلاعات من`
- گرفتن اطلاعات خودتان

+ `زمان`
- گرفتن ساعت و زمان

+ `اطلاعات` (ریپلای)
- گرفتن اطلاعات کسی

+ `وضعیت`
- گرفتن وضعیت ربات

"""
        key = keyboard_back_fa

    reply_markup = InlineKeyboardMarkup(key)
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='markdown')


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
