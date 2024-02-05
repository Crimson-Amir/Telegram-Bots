from telegram import InlineKeyboardButton

main_key = [
    [InlineKeyboardButton("🛒 خرید سرویس", callback_data='select_server')],

    [InlineKeyboardButton("👝 کیف پول", callback_data='wallet_page'),
     InlineKeyboardButton("🎛 سرویس‌های ‌من", callback_data='my_service')],

    [InlineKeyboardButton("⏳ دریافت سرویس تست", callback_data='service_1')],

    [InlineKeyboardButton("⚙️ تنظیمات", callback_data='settings'),
     InlineKeyboardButton("🔰 رتبه‌بندی", callback_data='rank_page')],

    [InlineKeyboardButton("📚 راهنمایی و پشتیبانی", callback_data='guidance')]
]
