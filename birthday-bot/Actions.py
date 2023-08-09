import random
import sqlite3
from telegram.ext import *
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from dateutil.relativedelta import relativedelta
from datetime import datetime, time
from datetime import date as date_1
import pytz
from Other import what_lang
import openai
from khayyam import *
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from khayyam import *
import random
import arabic_reshaper
from bidi.algorithm import get_display
import locale
import speech_recognition as sr
import os

openai.api_key = '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'


def reg_birth_code(update, user_message, chat_id, lan):
    text = user_message.split(" ")
    t = ""
    for i in text:
        t = t + i + " "
    a = t.replace('set ', '').split()  # [amir, amir, 23, 2], [23, 2]

    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()
    c.execute("SELECT id FROM BirthDays WHERE chat_id={0}".format(chat_id))
    text = c.fetchall()
    c.execute("SELECT remind FROM Details WHERE chat_id={0}".format(chat_id))
    text_remind = c.fetchall()
    c.execute("SELECT status FROM Jalali WHERE chat_id={0}".format(chat_id))
    jalali = c.fetchall()

    conn.commit()

    num = 0
    my_list = []

    done = "Done Successfully, I gotch it✅"
    exists = "This username already exists❌"
    problem = "Something Has Problem❌"

    if lan == "fa":
        done = "تولد با موفقیت ثبت شد ✅"
        exists = "یوزرنیم از قبل وجود دارد ❌"
        problem = "مشکلی وجود دارد ❌"

    for i in text:
        num_2 = text[num]
        my_list.append(str(num_2[0]))
        num += 1

    try:
        rep = str(update.message.reply_to_message.from_user['id'])
    except:
        rep = ""

    try:
        if str(a[1]) not in my_list and rep not in my_list:

            try:
                if jalali[0][0] == "True":
                    j = JalaliDate(1402, a[3], a[2]).todate()

                    a[3] = j.month
                    a[2] = j.day

                rem_date = date_1(year=1, month=int(a[3]), day=int(a[2])) - relativedelta(days=int(text_remind[0][0]))

                c.execute("INSERT INTO BirthDays VALUES( ?, ?, ?, ?, ?, ?, ?)",
                          (a[0], a[1], int(a[2]), int(a[3]), int(rem_date.day), int(rem_date.month), chat_id))
            except:

                if jalali[0][0] == "True":
                    j = JalaliDate(1402, a[3], a[2]).todate()

                    a[1] = j.month
                    a[0] = j.day

                rem_date = date_1(year=1, month=int(a[1]), day=int(a[0])) - relativedelta(days=int(text_remind[0][0]))

                reply = update.message.reply_to_message.from_user

                c.execute("INSERT INTO BirthDays VALUES( ?, ?, ?, ?, ?, ?, ?)",
                          (reply['first_name'], reply['id'], int(a[0]), int(a[1]), int(rem_date.day), int(rem_date.month), chat_id))
            update.message.reply_text(done)

        elif (a[1] in my_list) and (type(int(a[2])) == int) and (type(int(a[3]) == int)):
            update.message.reply_text(exists)
        elif rep in my_list:
            update.message.reply_text(exists)

        conn.commit()
        conn.close()

    except:
        update.message.reply_text(problem)
        conn.close()


def filter_words(update, context):
    user = update.message.from_user
    chat_id = str(update.message.chat_id)
    message = update.message
    user_message = str(message.text).lower()

    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()
    c.execute("SELECT permission FROM Details WHERE chat_id={0}".format(chat_id))
    text2 = c.fetchall()

    conn.commit()

    lan = what_lang(chat_id)

    if message.voice:
        voice = message.voice
        file_id = voice.file_id
        file = context.bot.get_file(file_id)
        file.download('yo.oga')

        os.system('ffmpeg -i yo.oga yo.wav')

        r = sr.Recognizer()
        audio_file = "yo.wav"
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)

        try:
            q = "تبدیل صدا به متن:\n" + r.recognize_google(audio_data, language='fa-IR')
        except sr.UnknownValueError:
            q = "متاسفانه متوجه نشدم"
        except sr.RequestError as e:
            q = "نمی توان به گوگل ریکوئست ارسال کرد; {0}".format(e)

        update.message.reply_text(q)
        os.remove('yo.wav')

    else:
        if ("start daily" in user_message) and (user['id'] == 6010442497):
            context.job_queue.run_daily(happy_birthday,
                                        days=(0, 1, 2, 3, 4, 5, 6),
                                        time=time(hour=1, minute=00, tzinfo=pytz.timezone("Asia/Tehran")),
                                        context=chat_id)
            update.message.reply_text('Done✅')


        elif "# " in user_message:
            context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
            message = user_message.replace('#', '')

            messages = [{"role": "system", "content":
                "You are a intelligent assistant."}]

            if message:
                messages.append(
                    {"role": "user", "content": message},
                )
                chat = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo", messages=messages
                )
            reply = chat.choices[0].message.content
            messages.append({"role": "assistant", "content": reply})

            # update.message.reply_text(reply, action=ChatAction.TYPING)

            update.message.reply_text(reply)

        elif "make fake " in user_message:

            locale.setlocale(locale.LC_ALL, '')

            def fa(number):
                farsi_num = {
                    '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴', '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹',
                }

                for one, b in farsi_num.items():
                    number = str(number).replace(one, b)

                return number

            def separate_with_commas(num):
                num_str = str(num)
                num_len = len(num_str)
                if num_len <= 3:
                    return num_str
                else:
                    return separate_with_commas(num_str[:-3]) + ',' + num_str[-3:]

            a = user_message.replace('make fake', '').split(",")

            recipient_name = a[0]
            recipient_cart = a[1]
            price = a[2]
            date = JalaliDatetime.now()
            date_now = date.strftime("%Y/%m/%d")
            time = date.strftime("%H:%M")
            transmitter_name = a[3]
            r = list(a[4])
            transmitter_cart = f"{r[0]}{r[1]}{r[2]}{r[3]} {r[4]}{r[5]}** **** {r[6]}{r[7]}{r[8]}{r[9]}"
            random_number = random.randint(1000000000, 9999999999)

            img = Image.open('blue-ready.jpg')
            i1 = ImageDraw.Draw(img)

            myFont = ImageFont.truetype('Yekan.ttf', 25)
            text = recipient_name
            i1.text((195, 298), text, font=myFont, fill=(0, 0, 0))

            myFont = ImageFont.truetype('Yekan.ttf', 25)
            text = recipient_cart
            x = 180
            for i in text:
                i1.text((x, 333), fa(i), font=myFont, fill=(87, 87, 87))
                x += 13

            myFont = ImageFont.truetype('Shabnam.ttf', 45)
            # text = fa(price)
            text = separate_with_commas(price)
            text = text.replace(" ", '')

            if text[0] == ",":
                text = text[1:]

            x = 235

            for o in text:
                if o != ",":
                    x += 15
                else:
                    x += 17

                i1.text((x, 380), fa(o), font=myFont, fill=(0, 0, 0))

                if o == ",":
                    x -= 7

            myFont = ImageFont.truetype('Shabnam.ttf', 23)
            text = fa(date_now)
            i1.text((30, 605), text, font=myFont, fill=(0, 0, 0))

            myFont = ImageFont.truetype('Shabnam.ttf', 23)
            text = fa(time)
            i1.text((140, 605), text, font=myFont, fill=(0, 0, 0))

            myFont = ImageFont.truetype('Yekan.ttf', 23)
            text = transmitter_name
            i1.text((30, 675), text, font=myFont, fill=(0, 0, 0))

            myFont = ImageFont.truetype('Shabnam.ttf', 23)
            text = fa(transmitter_cart)
            i1.text((30, 833), text, font=myFont, fill=(0, 0, 0))

            myFont = ImageFont.truetype('Shabnam.ttf', 23)
            text = fa(random_number)
            i1.text((36, 907), text, font=myFont, fill=(0, 0, 0))

            img.save("blue-ready-res.png")

            context.bot.send_photo(chat_id, photo=open('blue-ready-res.png', 'rb'))

        # make fake امیرحسین نجفی, 6037998236124532, 1000000, کیان مهر کریم پور, 037274369

        #     elif ("tag game" in user_message) or ("تگ گیم" in user_message) and (update.message.chat_id == -1001585609981):
        #
        #         result = user_message.replace('tag game', '')
        #         result = result.replace("تگ گیم", "")
        #         if len(result) == 0:
        #             ss = """
        # <a href='tg://user?id=599439425'>kian</a>
        # @NobodyInfact
        # @Sina_Abds
        # <a href='tg://user?id=2006273041'>ˢᴬᴶᴶᴬᴰ </a>
        # @immasan
        # <a href='tg://user?id=981725506'>Amir</a>
        # @Amir03727
        # <a href='tg://user?id=1380134238'>Erfan</a>
        # """
        #             update.message.reply_text(ss, parse_mode='html')
        #
        #     elif (("tag cs" in user_message) or ("تگ کانتر" in user_message)) or (update.message.chat_id == -1001585609981):
        #
        #         result = user_message.replace('tag cs', '')
        #         result = result.replace("تگ کانتر", "")
        #
        #         keyboard_back_fa = [[InlineKeyboardButton("قطعا نیستم ❌", callback_data="cs_1")],
        #                             [InlineKeyboardButton("احتمال کم هستم 🎗", callback_data="cs_2")],
        #                             [InlineKeyboardButton("شاید باشم 🔰", callback_data="cs_3")],
        #                             [InlineKeyboardButton("احتمال زیاد هستم ♻️", callback_data="cs_4")],
        #                             [InlineKeyboardButton("حتما هستم ✅", callback_data="cs_5")],
        #                             [InlineKeyboardButton("اگر بچه ها باشن هستم 🎲", callback_data="cs_6")]]
        #
        #         if len(result) == 0:
        #             conn = sqlite3.connect('Birth.db')
        #             c = conn.cursor()
        #
        #             ss = """
        # دوست دارید کانتر بازی کنیم؟🎈
        #
        # <a href='tg://user?id=599439425'>KianMehr</a> ❅ <a href='tg://user?id=5211714122'>Mohamad</a> ❅ <a href='tg://user?id=503042034'>Siena</a>
        # <a href='tg://user?id=2006273041'>Sajjad </a> ❅ <a href='tg://user?id=5659281560'>Masan</a> ❅ <a href='tg://user?id=981725506'>MohamdHasan</a>
        # <a href='tg://user?id=6010442497'>AmirH</a> ❅ <a href='tg://user?id=1380134238'>Eerfan</a>
        #
        # -----------------------------
        #                     """
        #             c.execute('UPDATE game SET text_me = (?) ', [ss])
        #             conn.commit()
        #             conn.close()
        #
        #             update.message.reply_text(ss, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard_back_fa))

        elif "set " in user_message:
            if update.message.chat.type == "privete":
                reg_birth_code(update, user_message, chat_id, lan)
            else:
                if text2[0][0] == "All":
                    reg_birth_code(update, user_message, chat_id, lan)

                elif text2[0][0] == "Admins":
                    admins = context.bot.get_chat_administrators(chat_id)
                    admin_list = []
                    for admin in admins:
                        user_name = admin.user.id
                        admin_list.append(user_name)
                    if update.message.from_user.id in admin_list:
                        reg_birth_code(update, user_message, chat_id, lan)
                    else:
                        if lan == "en":
                            update.message.reply_text(text="You are not Permission to set birthday❌\n\nset allowed for: Admins 👮🏻‍♂️")
                        elif lan == "fa":
                            update.message.reply_text(text="شما اجازه تنظیم تاریخ تولد را ندارید❌\n\nاجازه ثبت فقط برای: ادمین ها 👮🏻‍♂️")

                elif text2[0][0] == "ُSpecial":

                    c.execute("SELECT id FROM Specials WHERE chat_id = {0}".format(chat_id))

                    text = c.fetchall()  # [["12313441, 13231312312, 133132123"]]
                    text_2 = text[0][0]
                    special_list = text_2.split(", ")

                    if str(update.message.from_user.id) in special_list:
                        reg_birth_code(update, user_message, chat_id, lan)

                    else:
                        if lan == "en":
                            update.message.reply_text(text="You are not Permission to set birthday❌\n\nset allowed for: special members 👨🏻‍💼")
                        elif lan == "fa":
                            update.message.reply_text(text="شما اجازه تنظیم تاریخ تولد را ندارید❌\n\nاجازه ثبت فقط برای: اعضای ویژه👨🏻‍💼")

        elif "تتلو" in user_message:
            context.bot.ban_chat_member(chat_id, user['id'])
            update.message.reply_text("کاربر به دلیل ارسال کلمه تتلو از گروه بن شد🚫")

        elif ("reminder for" in user_message) or ("یادآور برای" in user_message):

            result = user_message.replace('reminder for ', '')
            result = result.replace("یادآور برای ", "")

            result = result.split(" ")

            if (int(result[1]) <= 30) and (int(result[1]) > 0):

                try:

                    c.execute("SELECT day, month FROM BirthDays WHERE id = (?) and chat_id = {0}".format(chat_id),
                              [str(result[0])])
                    text2 = c.fetchall()

                    rem_date = date_1(year=1, month=int(text2[0][1]), day=int(text2[0][0])) - relativedelta(days=int(result[1]))

                    c.execute("Update BirthDays set remind_day = {1} where chat_id = {0} and id = (?)".format(chat_id, int(rem_date.day)), [str(result[0])])
                    c.execute("Update BirthDays set remind_month = {1} where chat_id = {0} and id = (?)".format(chat_id, int(rem_date.month)), [str(result[0])])
                    conn.commit()

                    text = f"The birthday reminder {result[1]} day set for {result[0]} ✅"

                    if lan == "fa": text = f"یادآور تولد برای {result[0]} تنظیم شد روی {result[1]} روز✅"

                    update.message.reply_text(text)

                    c.execute("SELECT remind_day, remind_month FROM BirthDays WHERE id = (?) and chat_id = {0}".format(chat_id),
                              [str(result[0])])
                    text2 = c.fetchall()


                except:
                    text_eror = "something has problem❌\nMake sure that the user's registered username is the same"
                    if lan == "fa": text_eror = "مشکلی وجود دارد❌\n مطمئن شوید یوزرنیم ثبت شده کاربر همین باشد"
                    update.message.reply_text(text_eror)
            else:
                text = "The entered number is incorrect❌\n\nMinimum 1 and maximum 30"
                if lan == "fa": text = "عدد وارد شده نادرست است❌\n\nباید حداقل 1 و حداکثر 30 باشد"
                update.message.reply_text(text)

        elif ("reminder list" in user_message) or ("لیست یادآور" in user_message):

            result = user_message.replace('reminder list', '')
            result = result.replace("لیست یادآور", "")

            if len(result) == 0:

                try:
                    c.execute("SELECT * FROM BirthDays WHERE chat_id = {0}".format(chat_id))

                    text_data = c.fetchall()
                    text = ""
                    text_fa = ""

                    i = 0
                    for num in text_data:
                        rem_date = date_1(year=2021, month=int(text_data[i][3]), day=int(text_data[i][2])) - relativedelta(month=int(text_data[i][5]), days=int(text_data[i][4]))
                        if lan == "en":
                            text += f"Name: {text_data[i][0]} id: {text_data[i][1]}\nbirth: {text_data[i][2]}-{text_data[i][3]}\nremind {rem_date.day} day befor birthday \n\n"
                        elif lan == "fa":
                            text_fa += f"اسم: {text_data[i][0]} آیدی: {text_data[i][1]}\nتولد: {text_data[i][2]}-{text_data[i][3]}\nیادآوری میشود {rem_date.day} روز قبل از تولد" + "\n\n"
                        i += 1

                    if lan == "fa": text = text_fa

                    update.message.reply_text(text)

                except:
                    text_eror = "something has problem❌"
                    if lan == "fa": text_eror = "مشکلی وجود دارد❌"
                    update.message.reply_text(text_eror)

        elif ("id" in user_message) or ("آیدی" in user_message):

            result = user_message.replace('id', '')
            result = result.replace("آیدی", "")

            if len(result) == 0:

                id_2 = update.message.reply_to_message.from_user.id

                text = f"ID of the person you replied to:\n- `{id_2}`"
                if lan == "fa": text = "آیدی کسی که روی آن ریپلای کردید:\n" + f"- `{id_2}`"
                update.message.reply_text(text, parse_mode='markdown')

        elif ("chat id" in user_message) or ("آیدی چت" in user_message):

            result = user_message.replace('chat id', '')
            result = result.replace("آیدی چت", "")

            if len(result) == 0:

                id_2 = update.message.chat_id

                text = f"chat id:\n- `{id_2}`"
                if lan == "fa": text = "آیدی چت:\n" + f"- `{id_2}`"
                update.message.reply_text(text, parse_mode='markdown')

        elif ("message id" in user_message) or ("آیدی پیام" in user_message):

            result = user_message.replace('message id', '')
            result = result.replace("آیدی پیام", "")

            if len(result) == 0:

                id_2 = update.message.reply_to_message.message_id

                text = f"id of message you replied to:\n- `{id_2}`"
                if lan == "fa": text = "آیدی یام ریپلای شده:\n" + f"- `{id_2}`"
                update.message.reply_text(text, parse_mode='markdown')

        elif ("chat info" in user_message) or ("اطلاعات چت" in user_message):

            result = user_message.replace('chat info', '')
            result = result.replace("اطلاعات چت", "")

            if len(result) == 0:

                info = context.bot.get_chat(chat_id)

                text = f"information of chat:\n- name: {info['first_name']} \n- bio: {info['bio']} \n- username: {info['username']} \n- id: `{info['id']}` \n- type: {info['type']}"
                if lan == "fa": text = f"اطلاعات چت:\n- نام: {info['first_name']} \n- بیو: {info['bio']} \n- یوزرنیم: {info['username']} \n- آیدی: `{info['id']}` \n- نوع چت: {info['type']}"
                update.message.reply_text(text, parse_mode='markdown')

        elif ("me info" in user_message) or ("اطلاعات من" in user_message):

            result = user_message.replace('me info', '')
            result = result.replace("اطلاعات من", "")

            if len(result) == 0:

                info = update.message.from_user

                text = f"your info:\n- first name: {info['first_name']} \n- last name: {info['last_name']}\n- bio: {info['bio']} \n- username: {info['username']} \n- id: `{info['id']}`"
                if lan == "fa": text = f"اطلاعات شما:\n- نام اول: {info['first_name']} \n- نام خانوادگی: {info['last_name']}\n- بیو: {info['bio']} \n- یوزرنیم: {info['username']} \n- آیدی: `{info['id']}`"
                update.message.reply_text(text, parse_mode='markdown')

        elif ("time" in user_message) or ("زمان" in user_message):

            result = user_message.replace('time', '')
            result = result.replace("زمان", "")

            if len(result) == 0:

                time_iran = date = datetime.now(pytz.timezone('Asia/Tehran'))
                time_2 = date = datetime.now()

                text = f'utc time: {time_2.strftime("%H:%M")}\ndate: {time_2.strftime("%Y-%m-%d")}'
                if lan == "fa": text = f'ساعت ایران: {time_iran.strftime("%H:%M")}\nتاریخ ایران: {time_iran.strftime("%Y-%m-%d")}'
                update.message.reply_text(text, parse_mode='markdown')

        elif ("info" in user_message) or ("اطلاعات" in user_message):

            result = user_message.replace('info', '')
            result = result.replace("اطلاعات", "")

            if len(result) == 0:

                info = update.message.reply_to_message.from_user

                text = f"Information about who you have replied to:\n- first name: {info['first_name']} \n- last name: {info['last_name']}\n- bio: {info['bio']} \n- username: {info['username']} \n- id: `{info['id']}`"
                if lan == "fa": text = f"اطلاعات کسی که روی آن ریپلای کردید:\n- نام اول: {info['first_name']} \n- نام خانوادگی: {info['last_name']}\n- بیو: {info['bio']} \n- یوزرنیم: {info['username']} \n- آیدی: `{info['id']}`"
                update.message.reply_text(text, parse_mode='markdown')

        elif ("status" in user_message) or ("وضعیت" in user_message):

            result = user_message.replace('status', '')
            result = result.replace("وضعیت", "")

            if len(result) == 0:
                text = 'Bot is active ✅'
                if lan == "fa": text = 'ربات فعال است ✅'
                update.message.reply_text(text, parse_mode='markdown')

        text_5, special_list, admin_list = "", "", []

        try:
            c.execute("SELECT id FROM Specials WHERE chat_id = {0}".format(chat_id))
            text_4 = c.fetchall()

            text_5 = text_4[0][0]
            special_list = text_5.split(", ")

            admin = context.bot.get_chat_administrators(chat_id)
            admin_list = []
            for a in admin: admin_list.append(str(a.user.id))
        except:
            pass

        if (str(update.message.from_user.id) in special_list) or (str(update.message.from_user.id) in admin_list):

            if ("reg reminder" in user_message) or ("تنظیم یادآور" in user_message):

                day_1 = user_message.replace('reg reminder ', '')
                day = day_1.replace("تنظیم یادآور ", "")

                if (int(day) <= 30) and (int(day) > 0):

                    try:
                        c.execute("Update Details set remind = {0} where chat_id = {1}".format(int(day), chat_id))
                        conn.commit()

                        text = f"The birthday reminder set for {day} days✅"

                        if lan == "fa": text = f"یادآور تولد روی {day} روز تنظیم شد✅"

                        update.message.reply_text(text)

                    except:
                        text_eror = "something has problem❌"
                        if lan == "fa": text_eror = "مشکلی وجود دارد❌"
                        update.message.reply_text()
                else:
                    text = "The entered number is incorrect❌\n\nMinimum 1 and maximum 30"
                    if lan == "fa": text = "عدد وارد شده نادرست است❌\n\nباید حداقل 1 و حداکثر 30 باشد"
                    update.message.reply_text(text)

            elif ("reminder off" in user_message) or ("یادآور خاموش" in user_message):
                result = user_message.replace('reminder off', '')
                result = result.replace("یادآور خاموش", "")

                if len(result) == 0:

                    try:

                        c.execute("Update Details set remind = '0' where chat_id = {0}".format(chat_id))
                        conn.commit()

                        text = "The birthday reminder is off now✅"

                        if lan == "fa": text = "یادآور تولد خاموش شد✅"

                        update.message.reply_text(text)

                    except:
                        text_eror = "something has problem❌"
                        if lan == "fa": text_eror = "مشکلی وجود دارد❌"
                        update.message.reply_text()

            elif ("happy on" in user_message) or ("تبریک روشن" in user_message):

                result = user_message.replace('happy on', '')
                result = result.replace("تبریک روشن", "")

                if len(result) == 0:

                    try:

                        c.execute("Update Details set status = 'True' where chat_id = {0}".format(chat_id))
                        conn.commit()

                        text = "The bot now wishes happy birthdays✅"

                        if lan == "fa": text = "ربات اکنون تولد هارا در زمان مشخص شده تبریک می گوید✅"

                        update.message.reply_text(text)

                    except:
                        text_eror = "something has problem❌"
                        if lan == "fa": text_eror = "مشکلی وجود دارد❌"
                        update.message.reply_text()

            elif ("happy off" in user_message) or ("تبریک خاموش" in user_message):

                result = user_message.replace('happy off', '')
                result = result.replace("تبریک خاموش", "")

                if len(result) == 0:

                    try:

                        c.execute("Update Details set status = 'False' where chat_id = {0}".format(chat_id))
                        conn.commit()

                        text = "The bot no longer wishes happy birthday✅"

                        if lan == "fa": text = "ربات دیگر تولد هارا تبریک نمیگوید✅"

                        update.message.reply_text(text)

                    except:
                        text_eror = "something has problem❌"
                        if lan == "fa": text_eror = "مشکلی وجود دارد❌"
                        update.message.reply_text()

            elif ("clear births" in user_message) or ("پاک کردن تولدها" in user_message):

                result = user_message.replace('clear births', '')
                result = result.replace("پاک کردن تولدها", "")

                if len(result) == 0:

                    try:

                        c.execute("DELETE FROM BirthDays WHERE chat_id = {0}".format(chat_id))
                        conn.commit()

                        text = "All births were deleted✅"

                        if lan == "fa": text = "همه تولد ها پاک شدند✅"

                        update.message.reply_text(text)

                    except:
                        text_eror = "something has problem❌"
                        if lan == "fa": text_eror = "مشکلی وجود دارد❌"
                        update.message.reply_text()

            elif ("remove birth" in user_message) or ("حذف تولد" in user_message):

                birth = user_message.replace('remove birth ', '')
                birth = birth.replace('remove birth', '')
                birth = birth.replace('حذف تولد', '')
                birth = birth.replace("حذف تولد ", "")

                if len(birth) != 0:

                    c.execute("SELECT id,chat_id FROM BirthDays WHERE id = (?) and chat_id = {0}".format(chat_id), [str(birth)])
                    text2 = c.fetchall()

                    if len(text2) != 0:
                        try:

                            c.execute("DELETE FROM BirthDays WHERE id = (?) and chat_id = {0}".format(chat_id), [str(birth)])
                            conn.commit()

                            text = f"{birth} birthday removed from list✅"

                            if lan == "fa": text = f"تولد {birth} از لیست پاک شد✅"

                            update.message.reply_text(text)

                        except:
                            text_eror = "somthing has problem❌"
                            update.message.reply_text(text_eror)
                    else:

                        text_eror = "something has problem❌\n\nThe username entered must be the one you entered during registration. You can check from the 'see birthday' section in the help menu of the bot"
                        if lan == "fa": text_eror = "مشکلی وجود دارد❌" + "\n\n" + 'یوزرنیم وارد شده، باید همانی باشد که موقع ثبت وارد کردید.\n میتوانید از قسمت "مشاهده تولد ها" در منوی راهنمای ربات، چک کنید.'
                        update.message.reply_text(text_eror)

                elif len(birth) == 0:

                    replyed = update.message.reply_to_message.from_user.id

                    c.execute("SELECT id,chat_id FROM BirthDays WHERE id = (?) and chat_id = {0}".format(chat_id), [str(replyed)])
                    text2 = c.fetchall()

                    if len(text2) != 0:

                        try:

                            c.execute("DELETE FROM BirthDays WHERE id = (?) and chat_id = {0}".format(chat_id), [str(replyed)])
                            conn.commit()

                            text = f"id {replyed} birthday removed from list✅"

                            if lan == "fa": text = f"تولد {replyed} از لیست پاک شد✅"

                            update.message.reply_text(text)

                        except:
                            text_eror = "somthing has problem❌"
                            update.message.reply_text(text_eror)
                    else:
                        text_eror = "something has problem❌\n\nThe username entered must be the one you entered during registration. You can check from the 'see birthday' section in the help menu of the bot"
                        if lan == "fa": text_eror = "مشکلی وجود دارد❌" + "\n\n" + 'یوزرنیم وارد شده، باید همانی باشد که موقع ثبت وارد کردید.\n میتوانید از قسمت "مشاهده تولد ها" در منوی راهنمای ربات، چک کنید.'
                        update.message.reply_text(text_eror)

            if update.message.chat.type == "groupe" or update.message.chat.type == "supergroup":

                if ("add special" in user_message) or ("اضافه کردن ویژه" in user_message):
                    result = user_message.replace('add special', '')
                    result = result.replace("اضافه کردن ویژه", "")

                    if len(result) == 0:
                        id_ = update.message.reply_to_message.from_user
                        text = "⚠️"

                        user_special = f"""<a href="tg://user?id={str(id_['id'])}">{id_['first_name']}</a>"""

                        if str(id_['id']) in special_list:

                            text = f'{user_special} already in special list'
                            if lan == "fa": text = f'کاربر {user_special} در لیست ویژه وجود دارد '

                        elif id_ not in special_list:
                            text = f'{user_special} added to the special list ✅'
                            if lan == "fa": text = f'کاربر {user_special} به لیست ویژه اضافه شد ✅'
                            text_6 = text_5 + f", {id_['id']}"

                            c.execute("Update Specials set id = (?) where chat_id = {0}".format(str(chat_id)), [str(text_6)])
                            conn.commit()

                        update.message.reply_text(text, parse_mode='html')

                elif ("remove special" in user_message) or ("حذف ویژه" in user_message):

                    result = user_message.replace('remove special', '')
                    result = result.replace("حذف ویژه", "")

                    if len(result) == 0:

                        id_2 = update.message.reply_to_message.from_user
                        text = '⚠️'
                        user_special = f"""<a href="tg://user?id={str(id_2['id'])}">{id_2['first_name']}</a>"""

                        if str(id_2['id']) in admin_list:
                            text = 'You cannot delete admins from the special list❌'
                            if lan == "fa": text = 'شما نمیتوانید ادمین های گروه را از لیست ویژه حذف کنید❌'

                        elif (str(id_2['id']) not in admin_list) and (str(id_2['id']) in special_list):
                            text = f'{id_2[user_special]} remove from special list ✅'
                            if lan == "fa": text = f'کاربر {id_2[user_special]} از لیست  ویژه ها حذف شد ✅'
                            text_2 = text_5.replace(f", {id_2['id']}", "")
                            c.execute("Update Specials set id = (?) where chat_id = {0}".format(str(chat_id)), [str(text_2)])
                            conn.commit()

                        update.message.reply_text(text, parse_mode='markdown')

                elif ("special list" in user_message) or ("لیست اعضای ویژه" in user_message):

                    result = user_message.replace('special list', '')
                    result = result.replace("لیست اعضای ویژه", "")

                    if len(result) == 0:

                        text = ""
                        for i in special_list:
                            users = f"""<a href="tg://user?id={str(i)}">{i}</a>"""
                            text += f"{users} \n"
                        text_2 = f"list of group special list:\n {text}"
                        if lan == "fa": text_2 = f"لیست اعضای ویژه: \n{text}"
                        update.message.reply_text(text_2, parse_mode='html')

                elif ("per special" in user_message) or ("مجوز ویژه" in user_message):

                    result = user_message.replace('per special', '')
                    result = result.replace("مجوز ویژه", "")

                    if len(result) == 0:

                        c.execute("Update Details set permission = 'Special' where chat_id = {0}".format(str(chat_id)))
                        conn.commit()

                        text = "Now only special members can register births ✅"
                        if lan == "fa": text = 'اکنون فقط اعضای ویژه میتوانند تولد ثبت کنند ✅'
                        update.message.reply_text(text, parse_mode='markdown')

                elif ("per everyone" in user_message) or ("مجوز همه" in user_message):

                    result = user_message.replace('per everyone', '')
                    result = result.replace("مجوز همه", "")

                    if len(result) == 0:

                        c.execute("Update Details set permission = 'All' where chat_id = {0}".format(str(chat_id)))
                        conn.commit()

                        text = "Now All members can register births ✅"
                        if lan == "fa": text = 'اکنون همه اعضا میتوانند تولد ثبت کنند ✅'
                        update.message.reply_text(text, parse_mode='markdown')

                elif ("per admin" in user_message) or ("مجوز ادمین" in user_message):

                    result = user_message.replace('per admin', '')
                    result = result.replace("مجوز ادمین", "")

                    if len(result) == 0:

                        c.execute("Update Details set permission = 'Admins' where chat_id = {0}".format(str(chat_id)))
                        conn.commit()

                        text = "Now only Admin of group can register births ✅"
                        if lan == "fa": text = 'اکنون فقط ادمین ها میتوانند تولد ثبت کنند ✅'
                        update.message.reply_text(text, parse_mode='markdown')

    conn.close()


def clear_data(update, context):
    query = update.callback_query
    chat_id = str(query.message.chat_id)
    query.answer()
    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()
    c.execute("DELETE FROM BirthDays WHERE chat_id = {0}".format(chat_id))
    conn.commit()

    lan = what_lang(chat_id)

    conn.close()
    text = "Cleared!✅"

    keyboard_4 = [[InlineKeyboardButton("Back", callback_data="choose")],
                  [InlineKeyboardButton("Clear Data ⟳", callback_data="clear_data")]]

    reply_markup = InlineKeyboardMarkup(keyboard_4)
    query.edit_message_text(text=text, reply_markup=reply_markup)


def happy_birthday(context):
    date = str(datetime.now(pytz.timezone('Asia/Tehran')).strftime("%H:%M in %Y/%m/%d"))
    month = str(datetime.now(pytz.timezone('Asia/Tehran')).strftime("%m"))

    if month != "10":
        month = month.strip("0")

    day = str(datetime.now(pytz.timezone('Asia/Tehran')).strftime("%d"))
    day_int = int(day)
    if day_int > 10:
        day = day.strip("0")

    happy_text = [
        "Count your life by smiles, not tears. Count your age by friends, not years. Happy birthday!",
        "Happy birthday! I hope all your birthday wishes and dreams come true.",
        "A wish for you on your birthday, whatever you ask may you receive, whatever you seek may you find, whatever you wish may it be fulfilled on your birthday and always. Happy birthday!",
        " Another adventure filled year awaits you. Welcome it by celebrating your birthday with pomp and splendor. Wishing you a very happy and fun-filled birthday",
        "May the joy that you have spread in the past come back to you on this day. Wishing you a very happy birthday!",
        "Your life is just about to pick up speed and blast off into the stratosphere. Wear a seat belt and be sure to enjoy the journey. Happy birthday!",
        "This birthday, I wish you abundant happiness and love. May all your dreams turn into reality and may lady luck visit your home today. Happy birthday to one of the sweetest people I’ve ever known.",
        "May you be gifted with life’s biggest joys and never-ending bliss. After all, you yourself are a gift to earth, so you deserve the best. Happy birthday.",
        "Count not the candles…see the lights they give. Count not the years, but the life you live. Wishing you a wonderful time ahead. Happy birthday.",
        "Forget the past; look forward to the future, for the best things are yet to come.",
        "Birthdays are a new start, a fresh beginning and a time to pursue new endeavors with new goals. Move forward with confidence and courage. You are a very special person. May today and all of your days be amazing!",
        "Your birthday is the first day of another 365-day journey. Be the shining thread in the beautiful tapestry of the world to make this year the best ever. Enjoy the ride.",
        "Be happy! Today is the day you were brought into this world to be a blessing and inspiration to the people around you! You are a wonderful person! May you be given more birthdays to fulfill all of your dreams!",
        "Just wanted to be the first one to wish you happy birthday so I can feel superior to your other well-wishers. So, happy",
        "As you get older three things happen. The first is your memory goes, and I can’t remember the other two. Happy birthday!",
        "Cheers on your birthday. One step closer to adult underpants",
        "As you get older three things happen. The first is your memory goes, and I can’t remember the other two. Happy birthday!",
        "It’s birthday time again, and wow! You’re a whole year older now! So clown around and have some fun to make this birthday your best one. Happy birthday!",
        "When the little kids ask how old you are at your party, you should go ahead and tell them. While they’re distracted trying to count that high, you can steal a bite of their cake! Happy birthday!",
        "To quote Shakespeare: ‘Party thine ass off, Happy Birthday!"
    ]
    happy_text_fa = [
        "زندگی خود را با لبخند بشمار نه اشک. سنت را با دوستان بشمار نه سالها. تولدت مبارک!",
        "تولدت مبارک! امیدوارم همه آرزوها و رویاهای تولدت محقق شوند.",
        "یک آرزو برای تو در روز تولدت، هر چه خواستی دریافت کنی، هر چه می خواهی پیدا کنی، هر آرزویی که در روز تولدت برآورده شود. تولدت مبارک!",
        "یک سال پر ماجراجویی دیگر در انتظار شماست. با جشن تولد با شکوه از آن استقبال کنید. با آرزوی تولدی بسیار شاد و مفرح",
        "امیدوارم شادی که در گذشته گسترش داده اید در این روز به شما بازگردد. تولد شما را بسیار تبریک می گویم!",
        "زندگی شما به سرعت در حال افزایش است و به استراتوسفر می رود. کمربند ایمنی ببندید و مطمئن شوید که از سفر لذت خواهید برد. تولدت مبارک!",
        "در این تولد، برای شما شادی و عشق فراوان آرزو می کنم. باشد که همه رویاهای شما به واقعیت تبدیل شوند و خانم شانس امروز به خانه شما بیاید. تولد یکی از شیرین ترین افرادی که تا به حال شناخته ام مبارک باشد.",
        "ممکن است بزرگترین شادی های زندگی و سعادت بی پایان نصیب شما شود. بالاخره شما خودتان هدیه ای به زمین هستید، پس لایق بهترین ها هستید. تولدت مبارک.",
        "شمع‌ها را نشمارید... نورهایی را که می‌دهند ببینید. سال‌ها را حساب نکنید، بلکه لذت هایی که دارید را بشمارید. پیشاپیش لحظات فوق‌العاده‌ای را برای شما آرزو می‌کنم. تولدت مبارک.",
        "گذشته را فراموش کن، به آینده نگاه کن، زیرا بهترین چیزها هنوز در راه است.",
        "تولد یک شروع جدید، یک شروع تازه و زمانی برای پیگیری تلاش های جدید با اهداف جدید است. با اعتماد به نفس و شجاعت به جلو حرکت کنید. شما یک فرد بسیار خاص هستید. باشد که امروز و همه روزهای شما شگفت انگیز باشد!",
        "تولد شما اولین روز یک سفر 365 روزه دیگر است. نخ درخشانی در ملیله های زیبای جهان باشید تا امسال را بهترین سال کنید. لذت ببرید.",
        "خوشحال باشید! امروز روزی است که شما را به این دنیا آورده اند تا یک برکت و الهام برای مردم اطراف خود باشید! شما یک فرد فوق العاده هستید! باشد که تولدهای بیشتری به شما داده شود تا تمام رویاهای خود را برآورده کنید!",
        "فقط می‌خواستم اولین کسی باشم که تولدت را تبریک می‌گویم تا بتوانم نسبت به سایر دوستانت احساس برتری کنم. پس خوشحالم",
        "با بزرگتر شدن سه اتفاق می افتد. اولی این است که فراموشی میگیری، و من نمی توانم دو مورد دیگر را به یاد بیاورم. تولدت مبارک!",
        "تولدت به سلامتی. یک قدم به زیر شلواری پیرمردها نزدیک تر شدی",
        "دوباره زمان تولد است، و وای! تو الان یک سال بزرگتر شدی! پس کمی دلقک باش و کمی لذت ببر تا این تولد را به بهترین شکل تبدیل کنی. تولدت مبارک!",
        "وقتی بچه های کوچک در مهمانی می پرسند چند ساله هستید، باید جلو بروید و به آنها بگویید. در حالی که حواسشان پرت می شود و سعی می کنند بشمارند، شما می توانید لقمه ای از کیک آنها را بدزدید! تولدت مبارک!",
        "به نقل از شکسپیر: جشن واقعی در باسن شما اتفاق می افتد. تولدت مبارک!",
        "به نقل از شکسپیر: جشن واقعی در باسن شما اتفاق می افتد. تولدت مبارک!"
    ]

    conn = sqlite3.connect('Birth.db')
    c = conn.cursor()

    c.execute("SELECT * FROM BirthDays WHERE month = {0} AND day = {1}".format(month, day))
    text = c.fetchall()

    c.execute("SELECT * FROM BirthDays WHERE remind_month = {0} AND remind_day = {1}".format(month, day))
    text_2 = c.fetchall()

    if len(text) != 0:
        num = 0
        for i in text:
            res = text[num]
            name = res[0]
            username = res[1]
            chat_id = int(res[6])

            lan = what_lang(chat_id)

            c.execute("SELECT remind, status FROM Details WHERE chat_id = {0}".format(chat_id))
            text_24 = c.fetchall()
            text_24 = text_24[num][1]
            if text_24 == "True":
                if "@" in username:
                    username_2 = f"t.me/{username.replace('@', '')}"
                else:
                    username_2 = f"tg://user?id={username}"

                name_link = f"""<a href="{username_2}">{name.capitalize()}</a>"""
                rand = random.randint(0, 19)
                my_text = f"Everyone, today is {name_link} Day🎉\n\n{happy_text[rand]}🎂\n\n{date}"

                if lan == "fa":
                    my_text = f"امروز برای {name_link} است🎉\n\n{happy_text_fa[rand]}🎂\n\n{date} (کصمادر ایران)"
                message = context.bot.send_message(text=my_text, chat_id=chat_id, parse_mode='HTML',
                                                   disable_web_page_preview='True')
                try:
                    context.bot.pin_chat_message(chat_id, message.message_id)
                except:
                    pass
                num += 1
        else:
            pass
    if len(text_2) != 0:
        num_1 = 0
        for i in text_2:
            res = text_2[num_1]
            name = res[0]
            username = res[1]
            chat_id = int(res[6])

            lan = what_lang(chat_id)

            rem_date = date_1(year=2021, month=int(text_2[num_1][3]), day=int(text_2[num_1][2])) - relativedelta(month=int(text_2[num_1][5]), days=int(text_2[num_1][4]))

            if int(rem_date.day) != 0:

                if "@" in username:
                    username_2 = f"t.me/{username.replace('@', '')}"
                else:
                    username_2 = f"tg://user?id={username}"

                name_link = f"""<a href="{username_2}">{name.capitalize()}</a>"""

                my_text = f"Birthday reminder🎊:\n\n There are {rem_date.day} days left until {name_link} birthday"

                if lan == "fa":
                    my_text = f"یادآور تولد🎊:\n\n{rem_date.day} روز باقی مانده است تا تولد {name_link}"
                message = context.bot.send_message(text=my_text, chat_id=chat_id, parse_mode='HTML',
                                                   disable_web_page_preview='True')

                num_1 += 1
        else:
            pass

    conn.commit()
    conn.close()
