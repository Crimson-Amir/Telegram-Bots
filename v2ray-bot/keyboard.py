from telegram import InlineKeyboardButton

main_key = [
    [InlineKeyboardButton("🛒 خرید سرویس", callback_data='select_server')],

    [InlineKeyboardButton("⚙️ تنظیمات", callback_data='settings'),
     InlineKeyboardButton("🎛 سرویس های من", callback_data='my_service')],

    [InlineKeyboardButton("⏳ دریافت سرویس تست", callback_data='service_1')],

    [InlineKeyboardButton("📚 راهنما", callback_data='guidance'),
     InlineKeyboardButton("👥 پشتیبانی", callback_data='support')],
]