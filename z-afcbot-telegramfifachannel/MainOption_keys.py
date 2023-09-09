import os
import sqlite3
from telegram.ext import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultPhoto
from Other import what_lang
import requests

PHOTO, STEP1, STEP2, STEP3, STEP4, STEP5, STEP6, STEP7, STEP8 = range(9)


def get_data(name, limit=1):
    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()
    c.execute("SELECT * FROM {0} ORDER BY id DESC LIMIT {1}".format(name, limit))
    if limit != 1:
        info = c.fetchall()
    else:
        info = c.fetchone()
    conn.commit()
    conn.close()
    return info


def check_ivents(update, context):
    query = update.callback_query
    query.answer()
    chat_id = str(query.message.chat_id)

    lan = what_lang(chat_id)
    data = get_data('Main_text_Event')
    urls = get_data('Event', 30)
    key = []
    for x in range(0, len(urls), 6):
        row = []
        for url in urls[x:x + 6]:
            row.append(InlineKeyboardButton(url[1], url=url[2]))
        key.append(row)

    text = data[2]
    if lan == "fa":
        text = data[1]
        key.append([InlineKeyboardButton("برگشت", callback_data="choose")])
    else:
        key.append([InlineKeyboardButton("Back", callback_data="choose")])

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode="html")


def support(update, context):
    query = update.callback_query
    query.answer()
    chat_id = str(query.message.chat_id)

    lan = what_lang(chat_id)
    main_text = get_data('Help_text_Support')
    telegram_ = get_data('Telgram_id_support')
    email = get_data('Email_supoort')

    key = [[InlineKeyboardButton("Telegram 🚀", url=f"{telegram_[1]}"),
            InlineKeyboardButton("Email 📧", url=f"{email[1]}")],
           [InlineKeyboardButton("contact with developer 👤", url="t.me/Amir037274")],
           [InlineKeyboardButton("Back", callback_data="choose")]]

    text = main_text[2]
    if lan == "fa":
        text = main_text[1]
        key = [[InlineKeyboardButton("تلگرام 🚀", url=f"{telegram_[1]}"),
                InlineKeyboardButton("ایمیل 📧", url=f"{email[1]}")],
               [InlineKeyboardButton("ارتباط با توسعه دهنده ربات 👤", url="mailto:amirhosein03727@gmail.com")],
               [InlineKeyboardButton("برگشت", callback_data="choose")]]

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key))


def quid_help(update, context):
    query = update.callback_query
    query.answer()
    chat_id = str(query.message.chat_id)

    lan = what_lang(chat_id)

    text_main = get_data('Help_text_main')

    key = [[InlineKeyboardButton("Region ⚽", callback_data="region")],
           [InlineKeyboardButton("Account Protection 🔐", callback_data="account_protection"),
            InlineKeyboardButton("Ural calculation formula 🏎️", callback_data="ural_formula")],
           [InlineKeyboardButton("How to Have a Good Team? 👥", callback_data="good_team")],
           [InlineKeyboardButton("Back", callback_data="choose")]]

    text = text_main[2]
    if lan == "fa":
        text = text_main[1]
        key = [[InlineKeyboardButton("ترجمه آمار 📊", callback_data="statistics"),
                InlineKeyboardButton("توضیحات ریجن ⚽", callback_data="region")],
               [InlineKeyboardButton("کد دو مرحله ای 🔐", callback_data="account_protection"),
                InlineKeyboardButton("فرمول محاسبه اورال 🏎️", callback_data="ural_formula")],
               [InlineKeyboardButton("کشورهای هر ریجن 👥", callback_data="good_team")],
               [InlineKeyboardButton("برگشت", callback_data="choose")]]

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='html')


def best_cart(update, context):
    query = update.callback_query
    query.answer()
    chat_id = str(query.message.chat_id)

    lan = what_lang(chat_id)
    text_main = get_data('Help_text_BestCart')

    keyboard_3 = [[InlineKeyboardButton("The Best Players 💯", callback_data="best_player")],
                  [InlineKeyboardButton("Cheap Players 🎖", callback_data="cheap_best")],
                  [InlineKeyboardButton("Back", callback_data="choose")]]

    keyboard_fa_3 = [[InlineKeyboardButton("بهترین بازیکنان 💯", callback_data="best_player")],
                     [InlineKeyboardButton("بازیکنان به صرفه 🎖", callback_data="cheap_best")],
                     [InlineKeyboardButton("برگشت", callback_data="choose")]]

    key = keyboard_3
    text = text_main[2]
    if lan == "fa":
        text = text_main[1]
        key = keyboard_fa_3

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode="HTML")


def help_link(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)
    text_main = get_data('help_link_main_text')

    keyboard_5 = [[InlineKeyboardButton("Everlasting world 🌍", callback_data="everlasting_world"),
                   InlineKeyboardButton("FIFA Mobile ⚽", callback_data="fifa_mobile")],
                  [InlineKeyboardButton("Download and update 🔃", callback_data="download_update"),
                   InlineKeyboardButton("Help sites 📘", callback_data="helpful_site")],
                  [InlineKeyboardButton("Back", callback_data="choose")]]

    keyboard_fa_5 = [[InlineKeyboardButton("جهان اورلستینگ 🌍", callback_data="everlasting-world"),
                      InlineKeyboardButton("فیفا موبایل ⚽", callback_data="fifa_mobile")],
                     [InlineKeyboardButton("دانلود و اپدیت 🔃", callback_data="download_update"),
                      InlineKeyboardButton("سایت های کمکی 📘", callback_data="helpful_site")],
                     [InlineKeyboardButton("برگشت", callback_data="choose")]]

    key = keyboard_5
    text = text_main[2]

    if lan == "fa":
        key = keyboard_fa_5
        text = text_main[1]

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='markdown')


def set_league(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)
    main_text = get_data('Help_text_REG_LIG')

    key = [[InlineKeyboardButton("Register New League", callback_data="reg_leg")],
           [InlineKeyboardButton("Back", callback_data="choose")]]

    text = main_text[2]

    if lan == "fa":
        key = [[InlineKeyboardButton("ثبت لیگ جدید", callback_data="reg_leg")],
               [InlineKeyboardButton("برگشت", callback_data="choose")]]
        text = main_text[1]

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='markdown')


def setting(update, context):
    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()
    query = update.callback_query
    query.answer()
    user = query.from_user
    chat_id = query.message.chat_id

    c.execute("SELECT lang FROM Languages WHERE chat_id = {0}".format(chat_id))
    text_2 = c.fetchall()
    c.execute("SELECT permison FROM Per WHERE chat_id = {0}".format(chat_id))
    text_3 = c.fetchall()

    permission, languages = "⚠️", "⚠️"

    try:
        lan = text_2[0][0]

        if lan == "en":
            languages = "🇺🇸"
        elif lan == "fa":
            languages = "🇮🇷"

        permission = text_3[0][0]

    except:
        lan = "en"

    keyboard_fa_6 = [[InlineKeyboardButton(f"زبان ربات {languages}", callback_data="language"),
                      InlineKeyboardButton(f"مجوز ({permission})", callback_data="status_permission")],
                     [InlineKeyboardButton("برگشت", callback_data="choose")]]

    keyboard_6 = [[InlineKeyboardButton(f"language {languages}", callback_data="language"),
                   InlineKeyboardButton(f"permiss ({permission})", callback_data="status_permission")],
                  [InlineKeyboardButton("Back", callback_data="choose")]]

    key = keyboard_6
    text = f"🎛 Bot configuration section:\n\nYour-ID: `{user['id']}`\nChat-ID: `{chat_id}`"

    if lan == "fa":
        key = keyboard_fa_6
        text = f"🎛 بخش پیکربندی ربات:\n\nآیدی شما: `{user['id']}`\nآیدی چت: `{chat_id}`"

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='markdown')
    conn.close()


# ----------------------------------------------------------------------------------------------------


def insert_and_select_image(dowhat, file_pass=None, image=None, name=None):
    if dowhat == "insert":
        with open(file_pass, 'rb') as file:
            img = file.read()
        return img

    else:
        with open(f'{name}.jpg', 'wb') as file:
            img = file.write(image)


def statistics(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    chat_id = query.message.chat_id

    image = get_data('Translation_of_statistics')
    insert_and_select_image("select", image=image[1], name="statistics")

    lan = what_lang(chat_id)

    key = [[InlineKeyboardButton("Back", callback_data="help_bot")]]
    text = """• The photo has been sent to you."""
    caption = """⚽️ @FcMobile_Everlasting"""
    key_3 = [[InlineKeyboardButton("Share 🔗", switch_inline_query='Translation_of_statistics')]]
    if lan == "fa":
        key = [[InlineKeyboardButton("برگشت", callback_data="help_bot")]]
        key_3 = [[InlineKeyboardButton("اشتراک گذاری 🔗", switch_inline_query='Translation_of_statistics')]]
        text = """• عکس برای شما ارسال شد."""

    context.bot.send_photo(chat_id=chat_id, photo=open('statistics.jpg', 'rb'),
                           caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key))


def regions_fun(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    chat_id = query.message.chat_id

    region = get_data('Regions')
    insert_and_select_image("select", image=region[2], name="region")

    text = region[1]
    key = [[InlineKeyboardButton("برگشت", callback_data="help_bot")]]

    context.bot.send_photo(chat_id=chat_id, photo=open('region.jpg', 'rb'), caption=text)
    query.edit_message_text(text="عکس برای شما ارسال شد.", reply_markup=InlineKeyboardMarkup(key))


def account_protection_fun(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    chat_id = query.message.chat_id

    ap = get_data('Account_protection')

    with open('ap.mp4', 'wb') as file:
        img = file.write(ap[2])

    text = ap[1]
    key = [[InlineKeyboardButton("برگشت", callback_data="help_bot")]]
    context.bot.send_video(chat_id=chat_id, video=open('ap.mp4', 'rb'), caption=text)
    query.edit_message_text(text='ویدیو ارسال شد.', reply_markup=InlineKeyboardMarkup(key))


def good_team(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    chat_id = query.message.chat_id

    gt = get_data('Good_team_en')
    key = [[InlineKeyboardButton("برگشت", callback_data="help_bot")]]
    text = gt[1]

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key))


def ural_calculation_formula_fun(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    chat_id = query.message.chat_id

    ural = get_data('Ural_calculation_formula')

    caption = ural[2]
    insert_and_select_image("select", image=ural[3], name="ural_calculation")
    lan = what_lang(chat_id)

    key = [[InlineKeyboardButton("Back", callback_data="help_bot")]]
    text = """• The photo has been sent to you."""
    key_3 = [[InlineKeyboardButton("Share 🔗", switch_inline_query='Ural_calculation_formula')]]
    if lan == "fa":
        key = [[InlineKeyboardButton("برگشت", callback_data="help_bot")]]
        text = """• عکس برای شما ارسال شد."""
        key_3 = [[InlineKeyboardButton("اشتراک گذاری 🔗", switch_inline_query='Ural_calculation_formula')]]
        caption = ural[1]

    context.bot.send_photo(chat_id=chat_id, photo=open('ural_calculation.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key))


# -----------------------------------------------------------------------------------------------------------


def ew_wor_show(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    chat_id = query.message.chat_id

    ew_text = get_data('Everlasting_world')

    lan = what_lang(chat_id)

    keyboard_5 = [[InlineKeyboardButton("Back", callback_data="help_bot")]]
    keyboard_fa_5 = [[InlineKeyboardButton("برگشت", callback_data="help_bot")]]

    key = keyboard_5
    text = ew_text[2]

    if lan == "fa":
        key = keyboard_fa_5
        text = ew_text[1]

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key))


def fifa_mobile_social_show(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    info = get_data('FIFA_Mobile_Social')

    twiter = info[1]
    twich = info[2]
    discord = info[3]
    instagram = info[4]
    youtube = info[5]
    facebook = info[6]
    website = info[7]

    key = [[InlineKeyboardButton("Twitter 🐦", url=twiter),
            InlineKeyboardButton("Twitch 🟪", url=twich)],
           [InlineKeyboardButton("Discord 👾", url=discord),
            InlineKeyboardButton("Instagram 👥", url=instagram)],
           [InlineKeyboardButton("YouTube 🎈", url=youtube),
            InlineKeyboardButton("Facebook 🎭", url=facebook)],
           [InlineKeyboardButton("website 🌎", url=website),
            InlineKeyboardButton("Back", callback_data="help_link")]]

    text = "<b>• Select the desired option:</b>"

    if lan == "fa":
        text = "<b>• گزینه مورد نظر را انتخاب کنید:</b>"
        key = [[InlineKeyboardButton("توییتر 🐦", url=twiter),
                InlineKeyboardButton("توییچ 🟪", url=twich)],
               [InlineKeyboardButton("دیسکورد 👾", url=discord),
                InlineKeyboardButton("اینستاگرام 👥", url=instagram)],
               [InlineKeyboardButton("یوتیوب 🎈", url=youtube),
                InlineKeyboardButton("فیسبوک 🎭", url=facebook)],
               [InlineKeyboardButton("وبسایت 🌎", url=website),
                InlineKeyboardButton("برگشت", callback_data="help_link")]]

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode="HTML")


def fifa_mobile_social_show_now(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    info = get_data("Download_and_update")

    google_play = info[1]
    micet = info[2]
    appstore = info[3]
    farsroid = info[4]
    APKPURE = info[5]
    tinroid = info[6]

    key = [[InlineKeyboardButton("Google Play 🔹", url=google_play),
            InlineKeyboardButton("micet 🛒", url=micet)],
           [InlineKeyboardButton("App Store 🍎", url=appstore),
            InlineKeyboardButton("farsroid 🧩", url=farsroid)],
           [InlineKeyboardButton("APK Pure 🎈", url=APKPURE),
            InlineKeyboardButton("tinroid 🎮", url=tinroid)],
           [InlineKeyboardButton("back", callback_data="help_link")]]
    text = "<b>• Select the desired option:</b>"

    if lan == "fa":
        key = [[InlineKeyboardButton("گوگل پلی 🔹", url=google_play),
                InlineKeyboardButton("مایکت 🛒", url=micet)],
               [InlineKeyboardButton("اپ استور 🍎", url=appstore),
                InlineKeyboardButton("فارسروید 🧩", url=farsroid)],
               [InlineKeyboardButton("ای پی کی پیور 🎈", url=APKPURE),
                InlineKeyboardButton("تینروید 🎮", url=tinroid)],
               [InlineKeyboardButton("برگشت", callback_data="help_link")]]
        text = "<b>• گزینه مورد نظر را انتخاب کنید:</b>"

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key))


def helps_sites_realy(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    keyboard_5 = [[InlineKeyboardButton("Fifa prizee 🏆", callback_data="fifa_prizee")],
                  [InlineKeyboardButton("Fifa renders 🥇", callback_data="fifa_renders")],
                  [InlineKeyboardButton("Futbin ⚽", callback_data="futbin")]]

    text = "<b>• Click on the desired section</b>"

    if lan == "fa":
        keyboard_5.append([InlineKeyboardButton("برگشت", callback_data="help_link")])
        text = "<B>• روی بخش مورد نظر کلیک کنید</B>"
    else:
        keyboard_5.append([InlineKeyboardButton("Back", callback_data="help_link")])

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard_5), parse_mode="html")


def fifa_prizee(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    info = get_data('Fifa_prizee')

    main_text = info[1]
    main_text_en = info[2]
    site = info[3]
    android_app = info[4]

    key = [[InlineKeyboardButton("Web Site 🌏", url=site),
            InlineKeyboardButton("Android App 💠", url=android_app)],
           [InlineKeyboardButton("Back", callback_data="helpful_site")]]
    text = main_text_en

    if lan == "fa":
        key = [[InlineKeyboardButton("وب سایت 🌏", url=site),
                InlineKeyboardButton("برنامه اندروید 💠", url=android_app)],
               [InlineKeyboardButton("برگشت", callback_data="helpful_site")]]
        text = main_text

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key))


def fifa_renders(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    info = get_data('Fifa_renders')

    main_text = info[1]
    main_text_en = info[2]
    site = info[3]

    key = [[InlineKeyboardButton("Web Site 🌏", url=site)],
           [InlineKeyboardButton("Back", callback_data="helpful_site")]]

    text = main_text_en

    if lan == "fa":
        key = [[InlineKeyboardButton("وب سایت 🌏", url=site)],
               [InlineKeyboardButton("برگشت", callback_data="helpful_site")]]
        text = main_text

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key))


def futbin(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    info = get_data('Futbin')

    main_text = info[1]
    main_text_en = info[2]
    site = info[3]
    android_app = info[4]

    key = [[InlineKeyboardButton("Web Site 🌏", url=site),
            InlineKeyboardButton("Android App 💠", url=android_app)],
           [InlineKeyboardButton("Back", callback_data="helpful_site")]]
    text = main_text_en

    if lan == "fa":
        key = [[InlineKeyboardButton("وب سایت 🌏", url=site),
                InlineKeyboardButton("برنامه اندروید 💠", url=android_app)],
               [InlineKeyboardButton("برگشت", callback_data="helpful_site")]]
        text = main_text

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key))


# ------------------------------------------------------------------------------------------------------------


def best_player_show(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    keyboard_kld = [
        [
            InlineKeyboardButton("GK", callback_data="seb_gk"),
            InlineKeyboardButton("CB", callback_data="seb_cb"),
            InlineKeyboardButton("LB", callback_data="seb_lb"),
            InlineKeyboardButton("RB", callback_data="seb_rb"),
            InlineKeyboardButton("CM", callback_data="seb_cm")
        ],
        [
            InlineKeyboardButton("LM", callback_data="seb_lm"),
            InlineKeyboardButton("RM", callback_data="seb_rm"),
            InlineKeyboardButton("CAM", callback_data="seb_cam"),
            InlineKeyboardButton("CDM", callback_data="seb_cdm"),
            InlineKeyboardButton("RW", callback_data="seb_rw")
        ],
        [
            InlineKeyboardButton("LW", callback_data="seb_lw"),
            InlineKeyboardButton("ST", callback_data="seb_st"),
            InlineKeyboardButton("CF", callback_data="seb_cf")
        ]
    ]

    text = 'Select the desired post.'

    if lan == "fa":
        keyboard_kld.append([InlineKeyboardButton("برگشت", callback_data="best_cart")])
        text = 'پست مورد نظر را انتخاب کنید.'
    else:
        keyboard_kld.append([InlineKeyboardButton("Back", callback_data="best_cart")])

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard_kld))


def send_player_image(update, context):
    query = update.callback_query.data
    chat_id = update.callback_query.message.chat_id

    info = get_data('The_Best_player')
    caption = "⚽️ @FcMobile_Everlasting"
    lan = what_lang(chat_id)
    swich = str(query).replace('seb', 'up')
    key_3 = [[InlineKeyboardButton("Share 🔗", switch_inline_query=swich)]]
    if lan == "fa":
        key_3 = [[InlineKeyboardButton("اشتراک گذاری 🔗", switch_inline_query=swich)]]
    if query == "seb_gk":
        GK = info[1]
        insert_and_select_image("select", image=GK, name="GK_Best")
        context.bot.send_photo(chat_id=chat_id, photo=open('GK_Best.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "seb_cb":
        CB = info[2]
        insert_and_select_image("select", image=CB, name="CB_Best")
        context.bot.send_photo(chat_id=chat_id, photo=open('CB_Best.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "seb_lb":
        LB = info[3]
        insert_and_select_image("select", image=LB, name="LB_Best")
        context.bot.send_photo(chat_id=chat_id, photo=open('LB_Best.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "seb_rb":
        RB = info[4]
        insert_and_select_image("select", image=RB, name="RB_Best")
        context.bot.send_photo(chat_id=chat_id, photo=open('RB_Best.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "seb_cm":
        CM = info[5]
        insert_and_select_image("select", image=CM, name="CM_Best")
        context.bot.send_photo(chat_id=chat_id, photo=open('CM_Best.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "seb_lm":
        LM = info[6]
        insert_and_select_image("select", image=LM, name="LM_Best")
        context.bot.send_photo(chat_id=chat_id, photo=open('LM_Best.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "seb_rm":
        RM = info[7]
        insert_and_select_image("select", image=RM, name="RM_Best")
        context.bot.send_photo(chat_id=chat_id, photo=open('RM_Best.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "seb_cam":
        CAM = info[8]
        insert_and_select_image("select", image=CAM, name="CAM_Best")
        context.bot.send_photo(chat_id=chat_id, photo=open('CAM_Best.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "seb_cdm":
        CDM = info[9]
        insert_and_select_image("select", image=CDM, name="CDM_Best")
        context.bot.send_photo(chat_id=chat_id, photo=open('CDM_Best.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "seb_rw":
        RW = info[10]
        insert_and_select_image("select", image=RW, name="RW_Best")
        context.bot.send_photo(chat_id=chat_id, photo=open('RW_Best.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "seb_lw":
        LW = info[11]
        insert_and_select_image("select", image=LW, name="LW_Best")
        context.bot.send_photo(chat_id=chat_id, photo=open('LW_Best.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "seb_st":
        ST = info[12]
        insert_and_select_image("select", image=ST, name="ST_Best")
        context.bot.send_photo(chat_id=chat_id, photo=open('ST_Best.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "seb_cf":
        CF = info[13]
        insert_and_select_image("select", image=CF, name="CF_Best")
        context.bot.send_photo(chat_id=chat_id, photo=open('CF_Best.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))


def send_best_player_cheap(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    keyboard_main = [
        [
            InlineKeyboardButton("GK", callback_data="sec_gk"),
            InlineKeyboardButton("CB", callback_data="sec_cb"),
            InlineKeyboardButton("LB", callback_data="sec_lb"),
            InlineKeyboardButton("RB", callback_data="sec_rb"),
            InlineKeyboardButton("CM", callback_data="sec_cm")
        ],
        [
            InlineKeyboardButton("LM", callback_data="sec_lm"),
            InlineKeyboardButton("RM", callback_data="sec_rm"),
            InlineKeyboardButton("CAM", callback_data="sec_cam"),
            InlineKeyboardButton("CDM", callback_data="sec_cdm"),
            InlineKeyboardButton("RW", callback_data="sec_rw")
        ],
        [
            InlineKeyboardButton("LW", callback_data="sec_lw"),
            InlineKeyboardButton("ST", callback_data="sec_st"),
            InlineKeyboardButton("CF", callback_data="sec_cf")
        ]
    ]

    text = 'Select the desired post.'

    if lan == "fa":
        keyboard_main.append([InlineKeyboardButton("برگشت", callback_data="best_cart")])
        text = 'پست مورد نظر را انتخاب کنید.'
    else:
        keyboard_main.append([InlineKeyboardButton("Back", callback_data="best_cart")])
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard_main))


def send_player_image_cheap(update, context):
    query = update.callback_query.data
    chat_id = update.callback_query.message.chat_id

    info = get_data('Cheap_player')
    caption = """⚽️ @FcMobile_Everlasting"""
    lan = what_lang(chat_id)
    swich = str(query).replace('sec', 'upc')
    key_3 = [[InlineKeyboardButton("Share 🔗", switch_inline_query=swich)]]
    if lan == "fa":
        key_3 = [[InlineKeyboardButton("اشتراک گذاری 🔗", switch_inline_query=swich)]]
    if query == "sec_gk":
        GK = info[1]
        insert_and_select_image("select", image=GK, name="GK_Cheap")
        context.bot.send_photo(chat_id=chat_id, photo=open('GK_Cheap.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "sec_cb":
        CB = info[2]
        insert_and_select_image("select", image=CB, name="CB_Cheap")
        context.bot.send_photo(chat_id=chat_id, photo=open('CB_Cheap.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "sec_lb":
        LB = info[3]
        insert_and_select_image("select", image=LB, name="LB_Cheap")
        context.bot.send_photo(chat_id=chat_id, photo=open('LB_Cheap.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "sec_rb":
        RB = info[4]
        insert_and_select_image("select", image=RB, name="RB_Cheap")
        context.bot.send_photo(chat_id=chat_id, photo=open('RB_Cheap.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "sec_cm":
        CM = info[5]
        insert_and_select_image("select", image=CM, name="CM_Cheap")
        context.bot.send_photo(chat_id=chat_id, photo=open('CM_Cheap.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "sec_lm":
        LM = info[6]
        insert_and_select_image("select", image=LM, name="LM_Cheap")
        context.bot.send_photo(chat_id=chat_id, photo=open('LM_Cheap.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "sec_rm":
        RM = info[7]
        insert_and_select_image("select", image=RM, name="RM_Cheap")
        context.bot.send_photo(chat_id=chat_id, photo=open('RM_Cheap.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "sec_cam":
        CAM = info[8]
        insert_and_select_image("select", image=CAM, name="CAM_Cheap")
        context.bot.send_photo(chat_id=chat_id, photo=open('CAM_Cheap.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "sec_cdm":
        CDM = info[9]
        insert_and_select_image("select", image=CDM, name="CDM_Cheap")
        context.bot.send_photo(chat_id=chat_id, photo=open('CDM_Cheap.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "sec_rw":
        RW = info[10]
        insert_and_select_image("select", image=RW, name="RW_Cheap")
        context.bot.send_photo(chat_id=chat_id, photo=open('RW_Cheap.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "sec_lw":
        LW = info[11]
        insert_and_select_image("select", image=LW, name="LW_Cheap")
        context.bot.send_photo(chat_id=chat_id, photo=open('LW_Cheap.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "sec_st":
        ST = info[12]
        insert_and_select_image("select", image=ST, name="ST_Cheap")
        context.bot.send_photo(chat_id=chat_id, photo=open('ST_Cheap.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))
    elif query == "sec_cf":
        CF = info[13]
        insert_and_select_image("select", image=CF, name="CF_Cheap")
        context.bot.send_photo(chat_id=chat_id, photo=open('CF_Cheap.jpg', 'rb'), caption=caption, reply_markup=InlineKeyboardMarkup(key_3))


# ----------------------------------------------------------------------------------------------------------


def failed(update, context):
    query = update.callback_query
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("New league", callback_data="reg_leg"),
                     InlineKeyboardButton("Help Panel", callback_data="choose")]]
    text = '• There was a problem, try again ❌'
    if lan == "fa":
        text = '• مشکلی وجود داشت، دوباره تلاش کنید ❌'
        keyboard_kld = [[InlineKeyboardButton("لیگ جدید", callback_data="reg_leg"),
                         InlineKeyboardButton("پنل راهنما", callback_data="choose")]]
    update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard_kld))
    context.user_data.clear()
    return ConversationHandler.END


def cancle_leag(update, context):
    query = update.callback_query
    lan = what_lang(query.message.chat_id)
    text = '• Conversition Closed!'
    if lan == "fa":
        text = '• مکالمه پایان یافت!'
    query.edit_message_text(text=text)
    context.user_data.clear()
    return ConversationHandler.END


def reg_leag(update, context):
    query = update.callback_query
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = '• OK, Submit your latest league photo.\n• Note that do not send the photo as a file!'
    if lan == "fa":
        text = '• خیلی خب، جدیدترین عکس لیگ خود را بفرستید.\n• توجه کنید که عکس را به صورت فایل ارسال نکنید!'
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]

    context.bot.send_message(chat_id=query.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard_kld))
    return PHOTO


def photo(update, context):
    lan = what_lang(update.message.chat_id)
    try:
        user_photo = update.message.photo[-1].file_id
        context.user_data['photo'] = user_photo
        text = '• Well Done, now submit your league name.'
        if lan == "fa":
            text = '• بسیار خوب، حالا نام لیگ خودتون را ارسال کنید.'
        update.message.reply_text(text=text)
        return STEP1
    except:
        failed(update, context)


def step1(update, context):
    lan = what_lang(update.message.chat_id)
    try:
        user_text = update.message.text
        context.user_data['step1'] = user_text
        text = '• Great, now tell us your league region.'
        if lan == "fa":
            text = '• عالی، اکنون به ما ریجن لیگ خود را بگویید.'
        update.message.reply_text(text=text)
        return STEP2
    except:
        failed(update, context)


def step2(update, context):
    lan = what_lang(update.message.chat_id)
    try:
        user_text = update.message.text
        context.user_data['step2'] = user_text
        text = '• received! Submit your league fim.'
        if lan == "fa":
            text = '• دریافت شد! فیم لیگ خود را بفرستید.'
        update.message.reply_text(text=text)
        return STEP3
    except:
        failed(update, context)


def step3(update, context):
    lan = what_lang(update.message.chat_id)
    try:
        user_text = update.message.text
        context.user_data['step3'] = user_text
        text = '• OK, what is your league rank? tell us.'
        if lan == "fa":
            text = '• خوب، رنک لیگ شما چند است؟ به ما بگویید.'
        update.message.reply_text(text=text)
        return STEP4
    except:
        failed(update, context)


def step4(update, context):
    lan = what_lang(update.message.chat_id)
    try:
        user_text = update.message.text
        context.user_data['step4'] = user_text
        text = '• Now, tell me your lowest league over.'
        if lan == "fa":
            text = '• حداقل اور لیگتان را برای ما ارسال کنید.'
        update.message.reply_text(text=text)
        return STEP5
    except:
        failed(update, context)


def step5(update, context):
    lan = what_lang(update.message.chat_id)
    try:
        user_text = update.message.text
        context.user_data['step5'] = user_text
        text = '• I got it! How many players are there in your league?'
        if lan == "fa":
            text = '• فهمیدم! چند پلیر در لیگ شما وجود دارد؟'
        update.message.reply_text(text=text)
        return STEP6
    except:
        failed(update, context)


def step6(update, context):
    lan = what_lang(update.message.chat_id)
    try:
        user_text = update.message.text
        context.user_data['step6'] = user_text
        text = '• Allright! Who manages your league?'
        if lan == "fa":
            text = '• بسیار عالی! چه کسی لیگ شما را مدیریت میکند؟'
        update.message.reply_text(text=text)
        return STEP7
    except:
        failed(update, context)


def step7(update, context):
    lan = what_lang(update.message.chat_id)
    try:
        user_text = update.message.text
        context.user_data['step7'] = user_text
        text = '• Well, is there any more information you can give us?'
        if lan == "fa":
            text = '• خوب، اطلاعات بیشتری وجود دارد که به ما بدهید؟'
        update.message.reply_text(text=text)
        return STEP8
    except:
        failed(update, context)


def step8(update, context):
    lan = what_lang(update.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("New league", callback_data="reg_leg"),
                     InlineKeyboardButton("Help Panel", callback_data="choose")]]
    try:
        about = update.message.text
        pic = context.user_data['photo']
        name = context.user_data['step1']
        reg = context.user_data['step2']
        fim = context.user_data['step3']
        rank = context.user_data['step4']
        low_over = context.user_data['step5']
        players = context.user_data['step6']
        manager = context.user_data['step7']
        username = ""

        if update.message.from_user.username:
            username = f" | @{update.message.from_user.username}"

        file = context.bot.getFile(pic)
        file.download('leeg.jpg')

        caption = f"""
League name: {name}
Region: {reg}
Feem: {fim}
Rank: {rank}
Low Ower: {low_over}
Player Count: {players}
Manager: {manager}
About: {about}

submitted by <a href="tg://user?id={str(update.message.from_user.id)}">{update.message.from_user.first_name}</a>{username}
"""

        text = 'Your league has been successfully registered ✅\nThank you, your information has been sent to the admins and will be displayed after review.'
        if lan == "fa":
            text = 'لیگ شما با موفقیت ثبت شد ✅\nاز شما متشکریم، اطلاعات شما برای ادمین ها ارسال شد و بعد از بررسی نمایش داده میشه.'
            caption = f"""
نام لیگ: {name}
ریجن: {reg}
فیم: {fim}
رنک: {rank}
حداقل اور: {low_over}
تعداد بازیکنان: {players}
مدیر: {manager}
درباره لیگ: {about}

ارسال شده توسط <a href="tg://user?id={str(update.message.from_user.id)}">{update.message.from_user.first_name}</a>{username}
"""
            keyboard_kld = [[InlineKeyboardButton("لیگ جدید", callback_data="reg_leg"),
                             InlineKeyboardButton("پنل راهنما", callback_data="choose")]]
        update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard_kld))
        context.bot.send_photo(chat_id=5938166133, photo=open('leeg.jpg', 'rb'), caption=caption, parse_mode="html")
        context.bot.send_photo(chat_id=5820447488, photo=open('leeg.jpg', 'rb'), caption=caption, parse_mode="html")
        context.user_data.clear()
        os.remove('leeg.jpg')
        return ConversationHandler.END
    except:
        failed(update, context)


conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(reg_leag, pattern='reg_leg')],
    states={
        PHOTO: [MessageHandler(Filters.photo, photo)],
        STEP1: [MessageHandler(Filters.text & ~Filters.command, step1)],
        STEP2: [MessageHandler(Filters.text & ~Filters.command, step2)],
        STEP3: [MessageHandler(Filters.text & ~Filters.command, step3)],
        STEP4: [MessageHandler(Filters.text & ~Filters.command, step4)],
        STEP5: [MessageHandler(Filters.text & ~Filters.command, step5)],
        STEP6: [MessageHandler(Filters.text & ~Filters.command, step6)],
        STEP7: [MessageHandler(Filters.text & ~Filters.command, step7)],
        STEP8: [MessageHandler(Filters.text & ~Filters.command, step8)],
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=300,
)


# ----------------------------------------------------------------------------


def inline_query(update, context):
    caption = "⚽ @FcMobile_Everlasting"

    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Photo_url")
    info = c.fetchall()
    column_names = [description[0] for description in c.description]
    conn.commit()
    conn.close()

    photos = []
    a = 0
    for inf in info[0]:
        v = inf
        n = column_names[a]
        photos.append({'photo_id': n, 'photo_url': v, 'caption': caption})
        a += 1

    query = update.inline_query.query

    lan = what_lang(update.inline_query.from_user.id)
    button = InlineKeyboardButton("Start Bot 💫", url="t.me/FcMobileEverlasting_Bot/?start")

    if lan == "fa":
        button = InlineKeyboardButton("راه اندازی ربات 💫", url="t.me/FcMobileEverlasting_Bot/?start")

    results = []
    for p in photos:
        if p['photo_id'] == query:
            keyboard = InlineKeyboardMarkup([[button]])

            result = InlineQueryResultPhoto(
                photo_file_id=str(p['photo_id']),
                id=str(p['photo_id']),
                photo_url=p['photo_url'],
                caption=p['caption'],
                parse_mode='html',
                thumb_url=p['photo_url'],
                reply_markup=keyboard
            )
            results.append(result)
    update.inline_query.answer(results)
