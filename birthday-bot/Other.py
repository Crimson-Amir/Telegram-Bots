import sqlite3

def create_database():
    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS BirthDays(Name text, id text, day number, month number, remind_day number, remind_month number, chat_id text)')
    c.execute('CREATE TABLE IF NOT EXISTS Details(remind text, permission text, status text, chat_id text)')
    c.execute('CREATE TABLE IF NOT EXISTS GroupData(G_Name text, user_name text, chat_id text, user_id text, data text, Member number)')
    c.execute('CREATE TABLE IF NOT EXISTS Pv_Data(U_Name text, user_name text, id text,Data text)')
    c.execute('CREATE TABLE IF NOT EXISTS Languages(lang text, chat_id text)')
    c.execute('CREATE TABLE IF NOT EXISTS Specials(id text, chat_id text)')
    c.execute('CREATE TABLE IF NOT EXISTS Jalali(status text, chat_id text)')
    c.execute('CREATE TABLE IF NOT EXISTS game(text_me text)')

    conn.commit()
    conn.close()


def what_lang(chat_id):
    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()

    c.execute("SELECT lang FROM Languages WHERE chat_id = {0}".format(chat_id))
    text_2 = c.fetchall()

    try:
        lan = text_2[0][0]
    except:
        lan = "en"

    conn.commit()
    conn.close()

    return lan


def all_births(update, context):
    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()
    c.execute("SELECT * FROM BirthDays")
    text = c.fetchall()
    conn.commit()
    conn.close()
    update.message.reply_text(text)


def delete_birth(update, context):
    chat_id = update.message.chat_id
    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()
    c.execute("DELETE FROM Languages WHERE chat_id = {0}".format(chat_id))
    c.execute("DELETE FROM Specials WHERE chat_id = {0}".format(chat_id))
    c.execute("DELETE FROM Details WHERE chat_id = {0}".format(chat_id))
    conn.commit()
    conn.close()


def say_update(update, context):
    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()
    c.execute("SELECT chat_id FROM Languages")
    text = c.fetchall()

    num = 0
    for i in text:
        res = text[num]
        chat_id = int(res[0])
        num += 1
        lan = what_lang(chat_id)

        text_2 = """
+ 2.2.1 update of the robot has been released.

1- Now the robot supports Jalali (solar) calendar.
• Go to the bot settings with the /help command
• And in the calendar section, put it on Jalali.

⚠️ Due to the update of the robot, the database was cleared.
• Re-enter the /start command in Private.
• Remove and re-add the robot in the group.     
"""
        if lan == "fa": text_2 = """
+ آپدیت 2.2.1 ربات منتشر شد.

1- اکنون ربات از تقویم جلالی (شمسی) پشتیبانی میکند.
• با دستور /help به تنظیمات ربات بروید
• و در قسمت تقویم، آن را روی جلالی قرار دهید.

⚠️ به دلیل آپدیت شدن ربات، دیتابیس پاکسازی شد.
• در پرایوت دستور /start را دوباره وارد کنید.
• در گروه ربات را حذف و دوباره اضافه کنید.

        """

        try:
            context.bot.send_message(chat_id=chat_id, text=text_2, parse_mode='HTML')
        except:
            pass
    conn.commit()
    conn.close()


def cs(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id

    query.answer()

    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()

    c.execute("SELECT text_me FROM game")
    text_4 = c.fetchall()
    id_ = query.from_user
    text_4 = str(text_4[0][0])
    name = str(id_['first_name'])
    keyboard_back_fa = [[InlineKeyboardButton("قطعا نیستم ❌", callback_data="cs_1")],
                        [InlineKeyboardButton("احتمال کم هستم 🎗", callback_data="cs_2")],
                        [InlineKeyboardButton("شاید باشم 🔰", callback_data="cs_3")],
                        [InlineKeyboardButton("احتمال زیاد هستم ♻️", callback_data="cs_4")],
                        [InlineKeyboardButton("حتما هستم ✅", callback_data="cs_5")],
                        [InlineKeyboardButton("اگر بچه ها باشن هستم 🎲", callback_data="cs_6")]]

    if name not in text_4:
        if query.data == "cs_1":

            me = f"{id_['first_name']}: ❌ (قطعا نیستم 0)"

            res = f"{text_4} \n {me}"

            c.execute('UPDATE game SET text_me =  (?) ', [res])
            conn.commit()

        elif query.data == "cs_2":
            me = f"{id_['first_name']}: 🎗 (احتمال کم هستم 25)"

            res = f"{text_4} \n {me}"

            c.execute('UPDATE game SET text_me =  (?) ', [res])
            conn.commit()

        elif query.data == "cs_3":
            me = f"{id_['first_name']}: 🔰 (شاید بیام 50)"

            res = f"{text_4} \n {me}"

            c.execute('UPDATE game SET text_me =  (?) ', [res])
            conn.commit()

        elif query.data == "cs_4":
            me = f"{id_['first_name']}: ♻️ (احتمال زیاد هستم 75)"

            res = f"{text_4} \n {me}"

            c.execute('UPDATE game SET text_me = (?) ', [res])
            conn.commit()
        elif query.data == "cs_5":
            me = f"{id_['first_name']} : ✅ (حتما هستم 100)"

            res = f"{text_4} \n {me}"

            c.execute('UPDATE game SET text_me =  (?) ', [res])
            conn.commit()
        elif query.data == "cs_6":
            me = f"{id_['first_name']} : 🎲 (اگر بچه ها باشن هستم)"

            res = f"{text_4} \n {me}"

            c.execute('UPDATE game SET text_me =  (?) ', [res])
            conn.commit()

        c.execute("SELECT text_me FROM game")
        text_4 = c.fetchall()

        conn.close()

        query.edit_message_text(text=str(text_4[0][0]), parse_mode="html", reply_markup=InlineKeyboardMarkup(keyboard_back_fa))
