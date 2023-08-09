from telegram.ext import *
from telegram import InlineKeyboardButton

keyboard = [
    [InlineKeyboardButton("Set BirthDay ❤️", callback_data='set_birthday')],

    [InlineKeyboardButton("Settings ⚙️", callback_data='settings'),
     InlineKeyboardButton("Add to Group", url='t.me/Birthday_Reminder2_Bot?startgroup=new')],

    [InlineKeyboardButton("See Births 🎂", callback_data='see_birthday')],

    [InlineKeyboardButton("Support 👥", callback_data='support'),
     InlineKeyboardButton("Guidance 📚", callback_data='guidance')],
]

keyboard_fa = [
    [InlineKeyboardButton("ثبت تولد ❤️", callback_data='set_birthday')],

    [InlineKeyboardButton("اضافه کردن به گروه", url='t.me/Birthday_Reminder2_Bot?startgroup=new'),
     InlineKeyboardButton("تنظیمات ⚙️", callback_data='settings')],

    [InlineKeyboardButton("مشاهده تولد ها 🎂", callback_data='see_birthday')],

    [InlineKeyboardButton("راهنما 📚", callback_data='guidance'),
     InlineKeyboardButton("پشتیبانی 👥", callback_data='support')],
]

lang_key = [[InlineKeyboardButton("English 🇺🇸", callback_data='en'),
             InlineKeyboardButton("️Persian 🇮🇷", callback_data='fa')]]