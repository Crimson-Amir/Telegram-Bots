from telegram import InlineKeyboardButton

main_key = [
    [InlineKeyboardButton("ثبت تولد ❤️", callback_data='set_birthday')],

    [InlineKeyboardButton("اضافه کردن به گروه", url='t.me/Birthday_Reminder2_Bot?startgroup=new'),
     InlineKeyboardButton("تنظیمات ⚙️", callback_data='settings')],

    [InlineKeyboardButton("مشاهده تولد ها 🎂", callback_data='see_birthday')],

    [InlineKeyboardButton("راهنما 📚", callback_data='guidance'),
     InlineKeyboardButton("پشتیبانی 👥", callback_data='support')],
]
