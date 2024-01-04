from telegram import InlineKeyboardButton

main_key = [
    [InlineKeyboardButton("🛒 خرید سرویس", callback_data='buy_service')],

    [InlineKeyboardButton("⚙️ تنظیمات", callback_data='settings'),
     InlineKeyboardButton("🎛 سرویس های من", callback_data='my_service')],

    [InlineKeyboardButton("⏳ دریافت سرویس تست", callback_data='get_test_service')],

    [InlineKeyboardButton("📚 راهنما", callback_data='guidance'),
     InlineKeyboardButton("👥 پشتیبانی", callback_data='support')],
]
