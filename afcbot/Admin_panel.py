import os
import sqlite3
from telegram.ext import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from Other import what_lang
from keyboards import admin_key, admin_key_fa
import base64
import requests

# -- MAIN --

ENTER_NEW_TEXT = 0
REMOVE_ADMIN = 0
JOIN_TEXT = 0
BOT_START_TEXT_FA, BOT_START_TEXT_EN = range(2)
BOT_PANEL_TEXT_FA, BOT_PANEL_TEXT_EN = range(2)

# ------- #

ENTER_NEW_ENGLISH_TEXT_HELP_MAIN, ENTER_NEW_FARSI_TEXT_HELP_MAIN = range(2)

NETER_NEW_MAIN_IMAGE_FOR_STATISTICS = 0

NETER_NEW_RIGON_FARSI, NETER_NEW_RIGON_ENGLISH = range(2)

NETER_NEW_AP_FARSI, NETER_NEW_AP_ENGLISH = range(2)

NETER_NEW_GT_FARSI, NETER_NEW_GT_ENGLISH = range(2)

NETER_NEW_URAL_IMAGE, NETER_NEW_URAL_FA, NETER_NEW_URAL_EN = range(3)

# -- Support

NEW_SUPPORT_MAIN_TEXT_FA, NEW_SUPPORT_MAIN_TEXT_EN = range(2)
NEW_TELEGRAM_ID_SUPPORT = 0
NEW_EMAIL_SUPPORT = 0

# --- Best Cart

NEW_BEST_CART_MAIN_TEXT_FA, NEW_BEST_CART_MAIN_TEXT_EN = range(2)
NEW_IMAGES_BEST_CART = 0
NEW_IMAGES_CHEAP_CART = 0

# -- Help Link

NEW_SOCIAL_LINK = 0
NEW_JH_TEXT_FA, NEW_JH_TEXT_EN = range(2)
NEW_DOWNLOAD_LINK = 0
MAIN_TEXT_FIFA_FA, MAIN_TEXT_FIFA_EN = range(2)
MAIN_TEXT_HL_FA, MAIN_TEXT_HL_EN = range(2)
NEW_LINK_FIFA = 0

# -- Reg Lig

MAIN_TEXT_REGLIG_FA, MAIN_TEXT_REGLIG_EN = range(2)

# -- Events

EVENTS_INFO, EVENTS_LINK = range(2)
MAIN_TEXT_EVENT_FA, MAIN_TEXT_EVENT_EN = range(2)


def admin_panel(update, context):
    try:
        chat_id = str(update.message.chat_id)
        admin_id = update.message.from_user.id
    except:
        query = update.callback_query
        query.answer()
        chat_id = query.message.chat_id
        admin_id = query.from_user.id

    lan = what_lang(chat_id)

    key = admin_key
    text = """
• Hello, dear admin.
• You can choose the desired
• section from the sections below

<B>▸ Select the desired option:</B>
"""
    if lan == "fa":
        text = """
• سلام ادمین عزیز.
• می توانید از قسمت های زیر،
• بخش مورد نظر خود را تغییر دهید

<B>◂ گزینه مورد نظر را انتخاب کنید:</B>
    """
        key = admin_key_fa

    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()

    c.execute("SELECT user_id FROM Admins")
    text_2 = c.fetchall()
    for a in text_2:
        if str(admin_id) == a[0]:
            try:
                update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='html')
            except:
                query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='html')
            break
    conn.commit()
    conn.close()

    return ConversationHandler.END


# ------------------------------------------------------------------------------------


def upload_image(image_binary):
    url = "https://api.imgur.com/3/image"
    payload = {
        'image': base64.b64encode(image_binary).decode('utf-8')
    }
    headers = {
        'Authorization': 'Client-ID ' + 'ab3f912f29a5866'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()['data']['link']
    else:
        return None


def close(update, context):
    query = update.callback_query
    lan = what_lang(query.message.chat_id)
    text = '• Panel Closed!'
    if lan == "fa":
        text = '• پنل بسته شد!'
    query.edit_message_text(text=text)
    context.user_data.clear()


def up_help_section(update, context):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    key = [[InlineKeyboardButton("Update Main Text", callback_data="up_help_se_main_text")],
           [InlineKeyboardButton("Update Statistics Translation Image", callback_data="up_st_tr")],
           [InlineKeyboardButton("Update Region Text", callback_data='up_region')],
           [InlineKeyboardButton("Update Account Protection Text", callback_data="up_a_p")],
           [InlineKeyboardButton("Update Ural Calculation Photo & Text", callback_data="up_ural")],
           [InlineKeyboardButton("Update Good Team Text", callback_data="up_good_team")],
           [InlineKeyboardButton("Back", callback_data="admin_p")]]

    text = """
• Here you can change the text
• and photos of the help section

<B>▸ Select the desired option:</B>
"""
    if lan == "fa":
        text = """
• در اینجا می توانید متن و عکس های قسمت راهنما را عوض کنید 

<B>◂ گزینه مورد نظر را انتخاب کنید:</B>
    """
        key = [[InlineKeyboardButton("آپدیت متن اصلی", callback_data="up_help_se_main_text")],
               [InlineKeyboardButton("آپدیت عکس ترجمه آمار", callback_data="up_st_tr")],
               [InlineKeyboardButton("آپدیت متن ریجن", callback_data='up_region')],
               [InlineKeyboardButton("آپدیت متن محافظت از اکانت", callback_data="up_a_p")],
               [InlineKeyboardButton("آپدیت عکس و متن محاسبه اورال", callback_data="up_ural")],
               [InlineKeyboardButton("آپدیت کشورهای ریجن", callback_data="up_good_team")],
               [InlineKeyboardButton("برگشت", callback_data="admin_p")]]

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='html')
    return ConversationHandler.END


def up_best_cart(update, context):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    key = [[InlineKeyboardButton("Update Main Text", callback_data="up_main_text_best_cart")],
           [InlineKeyboardButton("Best Player", callback_data="best_player_change")],
           [InlineKeyboardButton("Cheap Player", callback_data='cheap_player_change')],
           [InlineKeyboardButton("-- CREAT TABALE --", callback_data='create_best_player_tabale')],
           [InlineKeyboardButton("Back", callback_data="admin_p")]]

    text = """
• Specify which category of players you want to change

<B>▸ Select the desired option:</B>
"""
    if lan == "fa":
        text = """
• مشخص کنید میخواهید بازیکنان کدام دسته را تغییر دهید

<B>◂ گزینه مورد نظر را انتخاب کنید:</B>
    """
        key = [[InlineKeyboardButton("آپدیت متن اصلی", callback_data="up_main_text_best_cart")],
               [InlineKeyboardButton("بهترین بازیکنان", callback_data="best_player_change")],
               [InlineKeyboardButton("بازیکنان به صرفه", callback_data='cheap_player_change')],
               [InlineKeyboardButton("-- CREAT TABALE --", callback_data='create_best_player_tabale')],
               [InlineKeyboardButton("برگشت", callback_data="admin_p")]]

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='html')


def up_support(update, context):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    key = [[InlineKeyboardButton("Update Main Text", callback_data="up_main_text_support")],
           [InlineKeyboardButton("Update Telegram ID", callback_data="up_telegram_id")],
           [InlineKeyboardButton("Update Email Addres", callback_data='up_email_addres')],
           [InlineKeyboardButton("Back", callback_data="admin_p")]]

    text = """
• Specify which one you want to change

<B>▸ Select the desired option:</B>
"""
    if lan == "fa":
        text = """
• مشخص کنید میخواهید کدام یک را تغییر دهید

<B>◂ گزینه مورد نظر را انتخاب کنید:</B>
    """
        key = [[InlineKeyboardButton("آپدیت متن اصلی", callback_data="up_main_text_support")],
               [InlineKeyboardButton("آپدیت آیدی تلگرام", callback_data="up_telegram_id")],
               [InlineKeyboardButton("آپدیت آدرس ایمیل", callback_data='up_email_addres')],
               [InlineKeyboardButton("برگشت", callback_data="admin_p")]]

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='html')


def up_help_link(update, context):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    keyboard_3 = [[InlineKeyboardButton("Edit Main Text", callback_data="ch_mt_hl")],
                  [InlineKeyboardButton("Everlasting World", callback_data="ch_ew")],
                  [InlineKeyboardButton("FIFA Mobile Section", callback_data="ch_ms")],
                  [InlineKeyboardButton("Download & Update Section", callback_data='up_download_and_update')],
                  [InlineKeyboardButton("Helpfull sites", callback_data='up_help_site')],
                  [InlineKeyboardButton("-- CREAT TABALE --", callback_data="create_help_link_tabale")],
                  [InlineKeyboardButton("Back", callback_data="admin_p")]]

    keyboard_fa_3 = [[InlineKeyboardButton("ویرایش متن اصلی", callback_data="ch_mt_hl")],
                     [InlineKeyboardButton("جهان اورلستینگ", callback_data="ch_ew")],
                     [InlineKeyboardButton("فیفا موبایل", callback_data="ch_ms")],
                     [InlineKeyboardButton("دانلود و آپدیت", callback_data='up_download_and_update')],
                     [InlineKeyboardButton("سایت های کمکی", callback_data='up_help_site')],
                     [InlineKeyboardButton("-- CREAT TABALE --", callback_data='create_best_player_tabale')],
                     [InlineKeyboardButton("برگشت", callback_data="admin_p")]]

    key = keyboard_3
    text = """
• Specify which one you want to change

<B>▸ Select the desired option:</B>
"""
    if lan == "fa":
        text = """
• مشخص کنید میخواهید کدام یک را تغییر دهید

<B>◂ گزینه مورد نظر را انتخاب کنید:</B>
    """
        key = keyboard_fa_3

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='html')


def view_bot_admin(update, context):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    keyboard_3 = [[InlineKeyboardButton("Back", callback_data="admin_p")]]

    keyboard_fa_3 = [[InlineKeyboardButton("برگشت", callback_data="admin_p")]]

    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()

    c.execute("SELECT user_id FROM Admins")
    text_id = c.fetchall()

    conn.close()

    t = ""
    for a in text_id:
        t += f"""<a href="tg://user?id={a[0]}">{a[0]}</a>\n"""

    key = keyboard_3
    text = f"""
• Here you can see the list of bot admins
• The following IDs have access to the admin panel

{t}
"""
    if lan == "fa":
        text = f"""
• در اینجا می توانید لیست ادمین های ربات را ببینید
• آیدی های زیر به پنل ادمین دسترسی دارند

{t}
"""
        key = keyboard_fa_3

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='html')


def view_bot_users(update, context):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    keyboard_3 = [[InlineKeyboardButton("Back", callback_data="admin_p")]]

    keyboard_fa_3 = [[InlineKeyboardButton("برگشت", callback_data="admin_p")]]

    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()

    c.execute("SELECT U_Name, user_name, id FROM Pv_Data")
    text_id = c.fetchall()
    conn.close()

    t = ""
    for a in text_id:
        t += f"""<a href="tg://user?id={a[2]}">{a[0]}</a> | @{a[1]}\n"""

    key = keyboard_3
    text = f"""
• Here you can see the list of
• those who started the bot

{t}
"""
    if lan == "fa":
        text = f"""
• در اینجا می توانید لیست کسانی که
• ربات را استارت کردند را ببینید

{t}
"""
        key = keyboard_fa_3

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='html')


# ----------------------------------------------------------------------------------------------


def new_tabale_help_link(update, context):
    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()

    sql = ''' INSERT INTO FIFA_Mobile_Social(twiter, twich, discord, instagram, youtube, facebook, website) VALUES(?,?,?,?,?,?,?) '''
    c.execute(sql, ('www.twitter.com', 'www.twitch.com', 'www.discord.com', 'www.instagram.com', 'www.youtube.com', 'www.facebook.com', 'www.google.com'))
    conn.commit()

    sql = ''' INSERT INTO Download_and_update(google_play, micet, appstore, farsroid, APKPURE, tinroid) VALUES(?,?,?,?,?,?) '''
    c.execute(sql, ('www.google_play.com', 'www.micet.com', 'www.appstore.com', 'www.farsroid.com', 'www.APKPURE.com', 'www.tinroid.com'))
    conn.commit()

    sql = ''' INSERT INTO Fifa_prizee(info_fa, info_en, site, android_app) VALUES(?,?,?,?) '''
    c.execute(sql, ('Hello There', 'Hello There (EN)', 'www.google.com', 'www.google.com'))
    conn.commit()

    sql = ''' INSERT INTO Fifa_renders(info_fa, info_en, site) VALUES(?,?,?,?) '''
    c.execute(sql, ('Hello There', 'Hello There (EN)', 'www.google.com'))
    conn.commit()

    sql = ''' INSERT INTO Futbin(info_fa, info_en, site, android_app) VALUES(?,?,?,?) '''
    c.execute(sql, ('Hello There', 'Hello There (EN)', 'www.google.com', 'www.google.com'))
    conn.commit()

    conn.close()


def new_tabale_best_player(update, context):
    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()

    sql = ''' INSERT INTO The_Best_player(GK, CB, LB, RB, CM, LM, RM, CAM, CDM,
     RW, LW, ST, CF, ONE, TWO, TRE, FOUR, FIVE, SIX, SEVEN) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
    c.execute(sql, (b'\x01', b'\x01', b'\x01', b'\x01', b'\x01', b'\x01', b'\x01', b'\x01',
                    b'\x01', b'\x01', b'\x01', b'\x01', b'\x01', b'\x01', b'\x01', b'\x01',
                    b'\x01', b'\x01', b'\x01', b'\x01'))
    conn.commit()

    sql = ''' INSERT INTO Cheap_player(GK, CB, LB, RB, CM, LM, RM, CAM, CDM,
         RW, LW, ST, CF, ONE, TWO, TRE, FOUR, FIVE, SIX, SEVEN) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
    c.execute(sql, (b'\x01', b'\x01', b'\x01', b'\x01', b'\x01', b'\x01', b'\x01', b'\x01',
                    b'\x01', b'\x01', b'\x01', b'\x01', b'\x01', b'\x01', b'\x01', b'\x01',
                    b'\x01', b'\x01', b'\x01', b'\x01'))
    conn.commit()

    sql = "INSERT INTO Photo_url VALUES ({0})".format(','.join(['?'] * 28))
    values = ('https://i.imgur.com/yRuiIaw.jpg',) * 28
    c.execute(sql, values)

    conn.commit()
    conn.close()


def new_tabale_event(update, context):
    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()

    for a in range(30):
        sql = ''' INSERT INTO Event(info, link) VALUES(?,?) '''
        c.execute(sql, (a, 'www.google.com'))
        conn.commit()

    conn.close()


def fifa_mobile_section(update, context):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    key = [
        [
            InlineKeyboardButton("Twitter", callback_data="up_twiter"),
            InlineKeyboardButton("Twitch", callback_data="up_twich"),
        ],
        [
            InlineKeyboardButton("Discord", callback_data="up_discord"),
            InlineKeyboardButton("Instagram", callback_data="up_instagram"),
        ],
        [
            InlineKeyboardButton("YouTube", callback_data="up_youtube"),
            InlineKeyboardButton("Facebook", callback_data="up_facebook"),
            InlineKeyboardButton("website", callback_data="up_website"),
        ],
        [
            InlineKeyboardButton("Back", callback_data="ch_hl")
        ]
    ]

    text = """
<B>▸ Which link do you want to change?:</B>
"""
    if lan == "fa":
        text = """
<B>◂ لینک کدام را میخواهید تغییر دهید:</B>
"""

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='html')


def download_and_update(update, context):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    key = [
        [
            InlineKeyboardButton("Google Play", callback_data="up_google_play"),
            InlineKeyboardButton("Myket", callback_data="up_micet"),
        ],
        [
            InlineKeyboardButton("App Store", callback_data="up_appstore"),
            InlineKeyboardButton("farsroid", callback_data="up_farsroid"),
        ],
        [
            InlineKeyboardButton("APKPURE", callback_data="up_apkpure"),
            InlineKeyboardButton("Tinroid", callback_data="up_tinroid"),
        ],
        [
            InlineKeyboardButton("Back", callback_data="ch_hl")
        ]
    ]

    text = """
<B>▸ Which link do you want to change?:</B>
"""
    if lan == "fa":
        text = """
<B>◂ لینک کدام را میخواهید تغییر دهید:</B>
"""
        key = [
            [
                InlineKeyboardButton("گوگل پلی", callback_data="up_google_play"),
                InlineKeyboardButton("مایکت", callback_data="up_micet"),
            ],
            [
                InlineKeyboardButton("اپ استور", callback_data="up_appstore"),
                InlineKeyboardButton("فارسروید", callback_data="up_farsroid"),
            ],
            [
                InlineKeyboardButton("اپک پور", callback_data="up_apkpure"),
                InlineKeyboardButton("تینروید", callback_data="up_tinroid"),
            ],
            [
                InlineKeyboardButton("برگشت", callback_data="ch_hl")
            ]
        ]
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='html')


def up_help_site_link(update, context):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    key = [
        [InlineKeyboardButton("Change about Fifa Prizee", callback_data="up_fifaprize")],
        [InlineKeyboardButton("Change about Fifa Renders", callback_data="up_fifrenders")],
        [InlineKeyboardButton("Change about Futbin", callback_data="up_futbin")],

        [
            InlineKeyboardButton("Fifa Prizee SITE LINK", callback_data="upfp_site"),
            InlineKeyboardButton("Fifa Prizee Android", callback_data="upfp_android_app"),
        ],
        [
            InlineKeyboardButton("Futbin SITE LINK", callback_data="upfu_site"),
            InlineKeyboardButton("Futbin Android", callback_data="upfu_android_app"),
        ],
        [
            InlineKeyboardButton("Fifa Renders SITE LINK", callback_data="upfr_site")
        ],
        [
            InlineKeyboardButton("Back", callback_data="ch_hl")
        ]
    ]

    text = """
    <B>▸ Which link do you want to change?:</B>
    """
    if lan == "fa":
        text = """
    <B>◂ لینک کدام را میخواهید تغییر دهید:</B>
    """
        key = [
            [InlineKeyboardButton(" توضیحات Fifa Prizee", callback_data="up_fifaprize")],
            [InlineKeyboardButton(" توضیحات Fifa Renders", callback_data="up_fifrenders")],
            [InlineKeyboardButton(" توضیحات Futbin", callback_data="up_futbin")],

            [
                InlineKeyboardButton("لینک سایت Fifa Prizee", callback_data="upfp_site"),
                InlineKeyboardButton("لینک اپلیکیشن Fifa Prizee", callback_data="upfp_android_app"),
            ],
            [
                InlineKeyboardButton("لینک سایت Futbin", callback_data="upfu_site"),
                InlineKeyboardButton("لینک اپلیکیشن Futbin", callback_data="upfu_android_app"),
            ],
            [
                InlineKeyboardButton("لینک سایت Fifa Renders", callback_data="upfr_site")
            ],
            [
                InlineKeyboardButton("برگشت", callback_data="ch_hl")
            ]
        ]
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='html')


def up_best_cart_best_player(update, context):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    key = [
        [
            InlineKeyboardButton("GK", callback_data="up_gk"),
            InlineKeyboardButton("CB", callback_data="up_cb"),
            InlineKeyboardButton("LB", callback_data="up_lb"),
            InlineKeyboardButton("RB", callback_data="up_rb"),
            InlineKeyboardButton("CM", callback_data="up_cm")
        ],
        [
            InlineKeyboardButton("LM", callback_data="up_lm"),
            InlineKeyboardButton("RM", callback_data="up_rm"),
            InlineKeyboardButton("CAM", callback_data="up_cam"),
            InlineKeyboardButton("CDM", callback_data="up_cdm"),
            InlineKeyboardButton("RW", callback_data="up_rw")
        ],
        [
            InlineKeyboardButton("LW", callback_data="up_lw"),
            InlineKeyboardButton("ST", callback_data="up_st"),
            InlineKeyboardButton("CF", callback_data="up_cf")
        ]
    ]

    text = """
<B>▸ Select the desired post:</B>
"""
    if lan == "fa":
        text = """
<B>◂ پست مورد نظر را انتخاب کنید:</B>
    """
        key.append([InlineKeyboardButton("برگشت", callback_data="ch_bc")])
    else:
        key.append([InlineKeyboardButton("Back", callback_data="ch_bc")])

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='html')


def up_cheap_player_post(update, context):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    lan = what_lang(chat_id)

    key = [
        [
            InlineKeyboardButton("GK", callback_data="upc_gk"),
            InlineKeyboardButton("CB", callback_data="upc_cb"),
            InlineKeyboardButton("LB", callback_data="upc_lb"),
            InlineKeyboardButton("RB", callback_data="upc_rb"),
            InlineKeyboardButton("CM", callback_data="upc_cm")
        ],
        [
            InlineKeyboardButton("LM", callback_data="upc_lm"),
            InlineKeyboardButton("RM", callback_data="upc_rm"),
            InlineKeyboardButton("CAM", callback_data="upc_cam"),
            InlineKeyboardButton("CDM", callback_data="upc_cdm"),
            InlineKeyboardButton("RW", callback_data="upc_rw")
        ],
        [
            InlineKeyboardButton("LW", callback_data="upc_lw"),
            InlineKeyboardButton("ST", callback_data="upc_st"),
            InlineKeyboardButton("CF", callback_data="upc_cf")
        ]
    ]

    text = """
<B>▸ Select the desired post:</B>
"""
    if lan == "fa":
        text = """
<B>◂ پست مورد نظر را انتخاب کنید:</B>
    """
        key.append([InlineKeyboardButton("برگشت", callback_data="ch_bc")])
    else:
        key.append([InlineKeyboardButton("Back", callback_data="ch_bc")])

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(key), parse_mode='html')


# -----------------------------------------------------------------------------------------------

def failed(update, context, lan):
    keyboard_kld = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p")]]
    text = '• There was a problem, try again ❌'
    if lan == "fa":
        text = '• مشکلی وجود داشت، دوباره تلاش کنید ❌'
        keyboard_kld = [[InlineKeyboardButton("پنل ادمین", callback_data="admin_p")]]
    update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard_kld))


def cancle_leag(update, context):
    query = update.callback_query
    lan = what_lang(query.message.chat_id)
    text = '• Conversition Closed!'
    if lan == "fa":
        text = '• مکالمه پایان یافت!'
    query.edit_message_text(text=text)
    context.user_data.clear()
    return ConversationHandler.END


def add_new_admin(update, context):
    query = update.callback_query
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New Admin ID."
    if lan == "fa":
        text = "• آیدی کاربری که میخواهید به عنوان ادمین اضافه شود، را ارسال کنید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]
    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return ENTER_NEW_TEXT


def handle_new_admin(update, context):
    new_text = str(update.message.text)
    lan = what_lang(update.message.chat_id)
    key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p"),
            InlineKeyboardButton("New Admin", callback_data="add_admin")]]
    try:
        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sql = ''' INSERT INTO Admins(user_id) VALUES(?) '''
        c.execute(sql, (new_text,))

        conn.commit()

        text = "New admin added successfully ✅"
        if lan == "fa":
            key = [[InlineKeyboardButton("برگشت به پنل ادمین", callback_data="admin_p"),
                    InlineKeyboardButton("اضافه کردن ادمین", callback_data="add_admin")]]
            text = "ادمین جدید با موفقیت اضافه شد ✅"

        conn.close()

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        context.user_data.clear()
        return ConversationHandler.END

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


new_admin_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_new_admin, pattern='add_admin')],
    states={
        ENTER_NEW_TEXT: [MessageHandler(Filters.text & ~Filters.command, handle_new_admin)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# -----------------------------------------------------------------------


def remove_admin(update, context):
    query = update.callback_query
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send Admin ID."
    if lan == "fa":
        text = "• آیدی ادمین را ارسال کنید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]
    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return REMOVE_ADMIN


def handle_remove_admin(update, context):
    new_text = str(update.message.text)
    lan = what_lang(update.message.chat_id)
    user = update.message.from_user.id
    key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p"),
            InlineKeyboardButton("Remove Admin Again", callback_data="add_admin")]]
    try:
        if id == 5938166133 or id == 5820447488:
            conn = sqlite3.connect('fifa.db')
            c = conn.cursor()

            sql = ''' DELETE FROM Admins WHERE user_id = ? '''
            c.execute(sql, (new_text,))

            conn.commit()

            text = "New admin removed successfully ✅"
            if lan == "fa":
                key = [[InlineKeyboardButton("برگشت به پنل ادمین", callback_data="admin_p"),
                        InlineKeyboardButton("حذف دوباره ادمین ها", callback_data="add_admin")]]
                text = "ادمین جدید با موفقیت حذف شد ✅"

            conn.close()

            context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        else:
            text = "sorry, you cant remove admins"
            if lan == "fa":
                text = "ببخشید، شما دسترسی برای حذف ادمین را ندارید"
            context.bot.send_message(chat_id=update.message.chat_id, text=text)
        context.user_data.clear()
        return ConversationHandler.END

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


remove_admin_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(remove_admin, pattern='remove_admin')],
    states={
        REMOVE_ADMIN: [MessageHandler(Filters.text & ~Filters.command, handle_remove_admin)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# -------------------------------------------------------


def insert_and_select_image(dowhat, file_pass=None, image=None, name=None):
    if dowhat == "insert":
        with open(file_pass, 'rb') as file:
            img = file.read()
        return img

    else:
        with open(f'{name}.jpg', 'wb') as file:
            img = file.write(image)


def edit_main_text_help(update, context):
    query = update.callback_query
    query.answer()
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New farsi Main Text."
    if lan == "fa":
        text = "• متن جدید فارسی را ارسال کنید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]

    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return ENTER_NEW_FARSI_TEXT_HELP_MAIN


def handle_farsi_edit_main_text_help(update, context):
    lan = what_lang(update.message.chat_id)
    try:
        new_text = str(update.message.text)
        context.user_data['new_farsi_text_main'] = new_text
        text = "Send New English Text."
        if lan == "fa":
            text = "متن جدید انگلیسی را ارسال کنید."

        context.bot.send_message(chat_id=update.message.chat_id, text=text)
        return ENTER_NEW_ENGLISH_TEXT_HELP_MAIN
    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


def handle_new_english_main_text_help(update, context):
    lan = what_lang(update.message.chat_id)

    try:
        new_english_text = str(update.message.text)
        new_farsi_text = context.user_data['new_farsi_text_main']
        key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p"),
                InlineKeyboardButton("Edit Again", callback_data="up_help_se_main_text")]]

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sql = ''' INSERT INTO Help_text_main(info_fa, info_en) VALUES(?,?) '''
        c.execute(sql, (new_farsi_text, new_english_text))

        conn.commit()
        conn.close()

        text = "new texts add ✅"
        if lan == "fa":
            text = "متن های جدید با موفقیت اضافه شدند ✅"
            key = [[InlineKeyboardButton("پنل ادمین", callback_data="admin_p"),
                    InlineKeyboardButton("ویرایش دوباره", callback_data="up_help_se_main_text")]]

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        context.user_data.clear()
        return ConversationHandler.END

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


new_help_main_text_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_main_text_help, pattern='up_help_se_main_text')],
    states={
        ENTER_NEW_FARSI_TEXT_HELP_MAIN: [MessageHandler(Filters.text & ~Filters.command, handle_farsi_edit_main_text_help)],
        ENTER_NEW_ENGLISH_TEXT_HELP_MAIN: [MessageHandler(Filters.text & ~Filters.command, handle_new_english_main_text_help)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# ------------------------------------------------------------------------


def add_new_statistics_image(update, context):
    query = update.callback_query
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New Image."
    if lan == "fa":
        text = "• عکس جدید را بفرستید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]
    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return NETER_NEW_MAIN_IMAGE_FOR_STATISTICS


def add_new_statistics_image_handel(update, context):
    images_ = update.message.photo[-1].file_id
    lan = what_lang(update.message.chat_id)
    key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p")]]
    try:
        file = context.bot.getFile(images_)
        file.download('new_statistics.jpg')

        rb = insert_and_select_image("insert", 'new_statistics.jpg')

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sql = ''' INSERT INTO Translation_of_statistics(image) VALUES(?) '''
        c.execute(sql, (rb,))
        conn.commit()

        c.execute(''' UPDATE Photo_url SET Translation_of_statistics = 'Translation_of_statistics'  ''')
        conn.commit()

        text = "New images added successfully ✅"
        if lan == "fa":
            key = [[InlineKeyboardButton("برگشت به پنل ادمین", callback_data="admin_p")]]
            text = "عکس جدید با موفقیت اضافه شد ✅"

        conn.close()

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        return ConversationHandler.END

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


new_admin_amar_image_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_new_statistics_image, pattern='up_st_tr')],
    states={
        NETER_NEW_MAIN_IMAGE_FOR_STATISTICS: [MessageHandler(Filters.photo & ~Filters.command, add_new_statistics_image_handel)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# ---------------------------------------------------------------------------


def add_new_region(update, context):
    query = update.callback_query
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New Farsi Region Text."
    if lan == "fa":
        text = "• متن فارسی ریجن جدید را ارسال کنید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]
    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return NETER_NEW_RIGON_FARSI


def add_new_persian_region_handel(update, context):
    new_text = str(update.message.text)
    context.user_data['new_farsi_text_region'] = new_text
    lan = what_lang(update.message.chat_id)
    try:
        text = "Now Send New image."
        if lan == "fa":
            text = "حالا عکس را وارد کنید."
        context.bot.send_message(chat_id=update.message.chat_id, text=text)
        return NETER_NEW_RIGON_ENGLISH

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


def add_new_english_region_handel(update, context):
    images_ = update.message.photo[-1].file_id
    lan = what_lang(update.message.chat_id)
    key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p")]]
    try:
        file = context.bot.getFile(images_)
        file.download('region.jpg')
        new_t = context.user_data['new_farsi_text_region']

        rb = insert_and_select_image("insert", 'region.jpg')

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sql = ''' INSERT INTO Regions(info_fa, image) VALUES(?,?) '''
        c.execute(sql, (new_t, rb))
        conn.commit()

        text = "New images added successfully ✅"
        if lan == "fa":
            key = [[InlineKeyboardButton("برگشت به پنل ادمین", callback_data="admin_p")]]
            text = "عکس جدید با موفقیت اضافه شد ✅"

        conn.close()

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        return ConversationHandler.END

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


new_region_text_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_new_region, pattern='up_region')],
    states={
        NETER_NEW_RIGON_FARSI: [MessageHandler(Filters.text & ~Filters.command, add_new_persian_region_handel)],
        NETER_NEW_RIGON_ENGLISH: [MessageHandler(Filters.photo & ~Filters.command, add_new_english_region_handel)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# --------------------------------------------------------------------------


def add_new_ap(update, context):
    query = update.callback_query
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New Farsi AP Text."
    if lan == "fa":
        text = "• متن فارسی محافظت از اکانت جدید را ارسال کنید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]
    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return NETER_NEW_AP_FARSI


def add_new_persian_ap_handel(update, context):
    new_text = str(update.message.text)
    context.user_data['new_farsi_text_ap'] = new_text
    lan = what_lang(update.message.chat_id)
    try:
        text = "Now Send New video"
        if lan == "fa":
            text = "حالا ویدیو را وارد کنید."
        context.bot.send_message(chat_id=update.message.chat_id, text=text)
        return NETER_NEW_AP_ENGLISH

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


def add_new_english_ap_handel(update, context):
    video = update.message.video.file_id
    lan = what_lang(update.message.chat_id)
    key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p")]]
    try:
        file = context.bot.getFile(video)
        file.download('ap.mp4')
        new_t = context.user_data['new_farsi_text_ap']

        rb = insert_and_select_image("insert", 'ap.mp4')

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sql = ''' INSERT INTO Account_protection(info_fa, video) VALUES(?,?) '''
        c.execute(sql, (new_t, rb))
        conn.commit()

        text = "New video added successfully ✅"
        if lan == "fa":
            key = [[InlineKeyboardButton("برگشت به پنل ادمین", callback_data="admin_p")]]
            text = "ویدیو جدید با موفقیت اضافه شد ✅"

        conn.close()

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        return ConversationHandler.END

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


new_ap_text_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_new_ap, pattern='up_a_p')],
    states={
        NETER_NEW_AP_FARSI: [MessageHandler(Filters.text & ~Filters.command, add_new_persian_ap_handel)],
        NETER_NEW_AP_ENGLISH: [MessageHandler(Filters.video & ~Filters.command, add_new_english_ap_handel)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# -------------------------------------------------------------------------

def add_new_gt(update, context):
    query = update.callback_query
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New Farsi Text."
    if lan == "fa":
        text = "• متن فارسی جدید را ارسال کنید (لینک های خود را به صورت یک پیام بفرستید)."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]
    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return NETER_NEW_GT_FARSI


def add_new_persian_gt_handel(update, context):
    new_text = str(update.message.text)
    context.user_data['new_farsi_text_gt'] = new_text
    lan = what_lang(update.message.chat_id)
    try:
        text = "Now Send New English Text."
        if lan == "fa":
            text = "حالا متن انگلیسی را وارد کنید."
        context.bot.send_message(chat_id=update.message.chat_id, text=text)
        return NETER_NEW_GT_ENGLISH

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


def add_new_english_gt_handel(update, context):
    lan = what_lang(update.message.chat_id)

    try:
        new_english_text = str(update.message.text)
        new_farsi_text = context.user_data['new_farsi_text_gt']
        key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p")]]

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sql = ''' INSERT INTO Good_team_en(info_fa, info_en) VALUES(?,?) '''
        c.execute(sql, (new_farsi_text, new_english_text))

        conn.commit()
        conn.close()

        text = "new texts add ✅"
        if lan == "fa":
            text = "متن های جدید با موفقیت اضافه شدند ✅"
            key = [[InlineKeyboardButton("پنل ادمین", callback_data="admin_p")]]

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        context.user_data.clear()
        return ConversationHandler.END

    except Exception as e:
        print(e)
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


new_gt_text_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_new_gt, pattern='up_good_team')],
    states={
        NETER_NEW_GT_FARSI: [MessageHandler(Filters.text & ~Filters.command, add_new_persian_gt_handel)],
        NETER_NEW_GT_ENGLISH: [MessageHandler(Filters.text & ~Filters.command, add_new_english_gt_handel)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# ----------------------------------------------------------------------------


def add_new_ural(update, context):
    query = update.callback_query
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New image."
    if lan == "fa":
        text = "• عکس جدید را ارسال کنید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]
    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return NETER_NEW_URAL_IMAGE


def add_new_ural_image_handel(update, context):
    new_image = update.message.photo[-1].file_id
    context.user_data['new_ural_image'] = new_image
    lan = what_lang(update.message.chat_id)
    try:
        text = "Now Send New Farsi Text."
        if lan == "fa":
            text = "حالا متن فارسی را وارد کنید."
        context.bot.send_message(chat_id=update.message.chat_id, text=text)
        return NETER_NEW_URAL_FA

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


def add_new_persian_ural_handel(update, context):
    new_text = str(update.message.text)
    context.user_data['new_farsi_text_ural'] = new_text
    lan = what_lang(update.message.chat_id)
    try:
        text = "Now Send New English Text."
        if lan == "fa":
            text = "حالا متن انگلیسی را وارد کنید."
        context.bot.send_message(chat_id=update.message.chat_id, text=text)
        return NETER_NEW_URAL_EN

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


def add_new_english_ural_handel(update, context):
    lan = what_lang(update.message.chat_id)

    try:
        new_english_text = str(update.message.text)
        new_farsi_text = context.user_data['new_farsi_text_ural']
        new_images = context.user_data['new_ural_image']

        file = context.bot.getFile(new_images)
        file.download('ural_calculation.jpg')
        rb = insert_and_select_image("insert", 'ural_calculation.jpg')

        key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p")]]

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sql = ''' INSERT INTO Ural_calculation_formula(info_fa, info_en, image) VALUES(?,?,?) '''
        c.execute(sql, (new_farsi_text, new_english_text, rb))
        conn.commit()

        c.execute(''' UPDATE Photo_url SET Ural_calculation_formula = 'Ural_calculation_formula'  ''')
        conn.commit()
        conn.close()

        text = "new texts and image added ✅"
        if lan == "fa":
            text = "عکس و متن های جدید با موفقیت اضافه شدند ✅"
            key = [[InlineKeyboardButton("پنل ادمین", callback_data="admin_p")]]

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        context.user_data.clear()
        return ConversationHandler.END

    except Exception as e:
        print(e)
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


new_ural_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_new_ural, pattern='up_ural')],
    states={
        NETER_NEW_URAL_IMAGE: [MessageHandler(Filters.photo & ~Filters.command, add_new_ural_image_handel)],
        NETER_NEW_URAL_FA: [MessageHandler(Filters.text & ~Filters.command, add_new_persian_ural_handel)],
        NETER_NEW_URAL_EN: [MessageHandler(Filters.text & ~Filters.command, add_new_english_ural_handel)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# --------------------------------------------------------------------------

def edit_support_main_text(update, context):
    query = update.callback_query
    query.answer()
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New farsi Main Text."
    if lan == "fa":
        text = "• متن جدید فارسی را ارسال کنید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]

    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return NEW_SUPPORT_MAIN_TEXT_FA


def edit_support_main_text_fa(update, context):
    lan = what_lang(update.message.chat_id)
    try:
        new_text = str(update.message.text)
        context.user_data['new_farsi_text_main_support'] = new_text
        text = "Send New English Text."
        if lan == "fa":
            text = "متن جدید انگلیسی را ارسال کنید."

        context.bot.send_message(chat_id=update.message.chat_id, text=text)
        return NEW_SUPPORT_MAIN_TEXT_EN
    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


def edit_support_main_text_en(update, context):
    lan = what_lang(update.message.chat_id)
    try:
        new_english_text = str(update.message.text)
        new_farsi_text = context.user_data['new_farsi_text_main_support']
        key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p"),
                InlineKeyboardButton("Edit Again", callback_data="up_help_se_main_text")]]

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sql = ''' INSERT INTO Help_text_Support(info_fa, info_en) VALUES(?,?) '''
        c.execute(sql, (new_farsi_text, new_english_text))

        conn.commit()
        conn.close()

        text = "new texts add ✅"
        if lan == "fa":
            text = "متن های جدید با موفقیت اضافه شدند ✅"
            key = [[InlineKeyboardButton("پنل ادمین", callback_data="admin_p"),
                    InlineKeyboardButton("ویرایش دوباره", callback_data="up_help_se_main_text")]]

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        context.user_data.clear()
        return ConversationHandler.END
    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


new_support_main_text_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_support_main_text, pattern='up_main_text_support')],
    states={
        NEW_SUPPORT_MAIN_TEXT_FA: [MessageHandler(Filters.text & ~Filters.command, edit_support_main_text_fa)],
        NEW_SUPPORT_MAIN_TEXT_EN: [MessageHandler(Filters.text & ~Filters.command, edit_support_main_text_en)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# ------------------------------------------------------------------------------

def edit_support_telegram_id(update, context):
    query = update.callback_query
    query.answer()
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New Telegram ID."
    if lan == "fa":
        text = "• آیدی جدید تلگرام را ارسال کنید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]

    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return NEW_TELEGRAM_ID_SUPPORT


def edit_support_telegram_id_handler(update, context):
    lan = what_lang(update.message.chat_id)

    try:
        new_id = str(update.message.text)
        key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p"),
                InlineKeyboardButton("Edit Again", callback_data="up_help_se_main_text")]]

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sql = ''' INSERT INTO Telgram_id_support(info) VALUES(?) '''
        c.execute(sql, (new_id,))

        conn.commit()
        conn.close()

        text = "new ID add ✅"
        if lan == "fa":
            text = "آیدی جدید اضافه شد ✅"
            key = [[InlineKeyboardButton("پنل ادمین", callback_data="admin_p"),
                    InlineKeyboardButton("ویرایش دوباره", callback_data="up_help_se_main_text")]]

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        context.user_data.clear()
        return ConversationHandler.END
    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


new_support_telegram_id_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_support_telegram_id, pattern='up_telegram_id')],
    states={
        NEW_TELEGRAM_ID_SUPPORT: [MessageHandler(Filters.text & ~Filters.command, edit_support_telegram_id_handler)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# ---------------------------------------------------------------------------


def edit_support_email(update, context):
    query = update.callback_query
    query.answer()
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New Telegram ID."
    if lan == "fa":
        text = "• ایمیل جدید را ارسال کنید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]

    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return NEW_EMAIL_SUPPORT


def edit_support_email_handler(update, context):
    lan = what_lang(update.message.chat_id)

    try:
        new_id = str(update.message.text)
        key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p"),
                InlineKeyboardButton("Edit Again", callback_data="up_help_se_main_text")]]

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sql = ''' INSERT INTO Email_supoort(info) VALUES(?) '''
        c.execute(sql, (new_id,))

        conn.commit()
        conn.close()

        text = "New Email add ✅"
        if lan == "fa":
            text = "ایمیل جدید اضافه شد ✅"
            key = [[InlineKeyboardButton("پنل ادمین", callback_data="admin_p"),
                    InlineKeyboardButton("ویرایش دوباره", callback_data="up_help_se_main_text")]]

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        context.user_data.clear()
        return ConversationHandler.END
    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


new_support_email_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_support_email, pattern='up_email_addres')],
    states={
        NEW_EMAIL_SUPPORT: [MessageHandler(Filters.text & ~Filters.command, edit_support_email_handler)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# -------------------------------------------------------------------------

def edit_best_cart_main_text(update, context):
    query = update.callback_query
    query.answer()
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New farsi Main Text."
    if lan == "fa":
        text = "• متن جدید فارسی را ارسال کنید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]

    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return NEW_BEST_CART_MAIN_TEXT_FA


def edit_best_cart_main_text_fa(update, context):
    lan = what_lang(update.message.chat_id)
    try:
        new_text = str(update.message.text)
        context.user_data['new_farsi_text_main_best_cart'] = new_text
        text = "Send New English Text."
        if lan == "fa":
            text = "متن جدید انگلیسی را ارسال کنید."

        context.bot.send_message(chat_id=update.message.chat_id, text=text)
        return NEW_BEST_CART_MAIN_TEXT_EN
    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


def edit_best_cart_main_text_en(update, context):
    lan = what_lang(update.message.chat_id)
    try:
        new_english_text = str(update.message.text)
        new_farsi_text = context.user_data['new_farsi_text_main_best_cart']
        key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p"),
                InlineKeyboardButton("Edit Again", callback_data="up_help_se_main_text")]]

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sql = ''' INSERT INTO Help_text_BestCart(info_fa, info_en) VALUES(?,?) '''
        c.execute(sql, (new_farsi_text, new_english_text))

        conn.commit()
        conn.close()

        text = "new texts add ✅"
        if lan == "fa":
            text = "متن های جدید با موفقیت اضافه شدند ✅"
            key = [[InlineKeyboardButton("پنل ادمین", callback_data="admin_p"),
                    InlineKeyboardButton("ویرایش دوباره", callback_data="up_help_se_main_text")]]

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        context.user_data.clear()
        return ConversationHandler.END
    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


new_best_cart_main_text_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_best_cart_main_text, pattern='up_main_text_best_cart')],
    states={
        NEW_BEST_CART_MAIN_TEXT_FA: [MessageHandler(Filters.text & ~Filters.command, edit_best_cart_main_text_fa)],
        NEW_BEST_CART_MAIN_TEXT_EN: [MessageHandler(Filters.text & ~Filters.command, edit_best_cart_main_text_en)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# -------------------------------------------------------------------------


def new_best_star_image(update, context):
    query = update.callback_query
    context.user_data['image_type'] = query.data
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New Image."
    if lan == "fa":
        text = "• عکس جدید را بفرستید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]
    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return NEW_IMAGES_BEST_CART


def new_best_star_image_handler(update, context):
    lan = what_lang(update.message.chat_id)
    key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p")]]
    try:
        image_type = context.user_data['image_type']
        images_ = update.message.photo[-1].file_id
        file = context.bot.getFile(images_)
        file.download(f'{image_type}.jpg')

        rb = insert_and_select_image("insert", f'{image_type}.jpg')

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()
        url = upload_image(rb)
        sss = image_type.replace('up_', '').upper()

        sql = ''' UPDATE The_Best_player SET {0} = ?  '''.format(sss)
        c.execute(sql, (rb,))
        conn.commit()

        sql = ''' UPDATE Photo_url SET {0} = ?  '''.format(image_type)
        c.execute(sql, (url,))
        conn.commit()

        text = "New images added successfully ✅"
        if lan == "fa":
            key = [[InlineKeyboardButton("برگشت به پنل ادمین", callback_data="admin_p")]]
            text = "عکس جدید با موفقیت اضافه شد ✅"

        conn.close()

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        return ConversationHandler.END

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


new_image_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(new_best_star_image, pattern='up_gk'),
                  CallbackQueryHandler(new_best_star_image, pattern='up_cb'),
                  CallbackQueryHandler(new_best_star_image, pattern='up_lb'),
                  CallbackQueryHandler(new_best_star_image, pattern='up_rb'),
                  CallbackQueryHandler(new_best_star_image, pattern='up_cm'),
                  CallbackQueryHandler(new_best_star_image, pattern='up_lm'),
                  CallbackQueryHandler(new_best_star_image, pattern='up_rm'),
                  CallbackQueryHandler(new_best_star_image, pattern='up_cam'),
                  CallbackQueryHandler(new_best_star_image, pattern='up_cdm'),
                  CallbackQueryHandler(new_best_star_image, pattern='up_rw'),
                  CallbackQueryHandler(new_best_star_image, pattern='up_lw'),
                  CallbackQueryHandler(new_best_star_image, pattern='up_st'),
                  CallbackQueryHandler(new_best_star_image, pattern='up_cf')],
    states={
        NEW_IMAGES_BEST_CART: [MessageHandler(Filters.photo & ~Filters.command, new_best_star_image_handler)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# ---------------------------------------------------------------------------------------


def new_cheap_star_image(update, context):
    query = update.callback_query
    context.user_data['image_types'] = query.data
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New Image."
    if lan == "fa":
        text = "• عکس جدید را بفرستید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]
    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return NEW_IMAGES_CHEAP_CART


def new_cheap_image_handler(update, context):
    lan = what_lang(update.message.chat_id)
    key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p")]]
    try:
        image_type = context.user_data['image_types']
        images_ = update.message.photo[-1].file_id
        file = context.bot.getFile(images_)
        file.download(f'{image_type}.jpg')

        rb = insert_and_select_image("insert", f'{image_type}.jpg')

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()
        url = upload_image(rb)
        sss = image_type.replace('upc_', '').upper()

        sql = ''' UPDATE Cheap_player SET {0} = ?  '''.format(sss)
        c.execute(sql, (rb,))
        conn.commit()

        sql = ''' UPDATE Photo_url SET {0} = ?  '''.format(image_type)
        c.execute(sql, (url,))
        conn.commit()

        text = "New images added successfully ✅"
        if lan == "fa":
            key = [[InlineKeyboardButton("برگشت به پنل ادمین", callback_data="admin_p")]]
            text = "عکس جدید با موفقیت اضافه شد ✅"

        conn.close()

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        return ConversationHandler.END

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


new_cheap_image_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(new_cheap_star_image, pattern='upc_gk'),
                  CallbackQueryHandler(new_cheap_star_image, pattern='upc_cb'),
                  CallbackQueryHandler(new_cheap_star_image, pattern='upc_lb'),
                  CallbackQueryHandler(new_cheap_star_image, pattern='upc_rb'),
                  CallbackQueryHandler(new_cheap_star_image, pattern='upc_cm'),
                  CallbackQueryHandler(new_cheap_star_image, pattern='upc_lm'),
                  CallbackQueryHandler(new_cheap_star_image, pattern='upc_rm'),
                  CallbackQueryHandler(new_cheap_star_image, pattern='upc_cam'),
                  CallbackQueryHandler(new_cheap_star_image, pattern='upc_cdm'),
                  CallbackQueryHandler(new_cheap_star_image, pattern='upc_rw'),
                  CallbackQueryHandler(new_cheap_star_image, pattern='upc_lw'),
                  CallbackQueryHandler(new_cheap_star_image, pattern='upc_st'),
                  CallbackQueryHandler(new_cheap_star_image, pattern='upc_cf')],
    states={
        NEW_IMAGES_CHEAP_CART: [MessageHandler(Filters.photo & ~Filters.command, new_cheap_image_handler)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# ---------------------------------------------------------------------------------------

def new_social_link_help(update, context):
    query = update.callback_query
    context.user_data['social_link'] = query.data
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New Link."
    if lan == "fa":
        text = "• لینک جدید را بفرستید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]
    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return NEW_SOCIAL_LINK


def new_social_link_handler_help_link(update, context):
    lan = what_lang(update.message.chat_id)
    key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p")]]
    try:
        image_type = context.user_data['social_link']
        rb = update.message.text

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sss = image_type.replace('up_', '')

        sql = ''' UPDATE FIFA_Mobile_Social SET {0} = ?  '''.format(sss)
        c.execute(sql, (rb,))

        conn.commit()

        text = "New Link added successfully ✅"
        if lan == "fa":
            key = [[InlineKeyboardButton("برگشت به پنل ادمین", callback_data="admin_p")]]
            text = "لینک جدید با موفقیت اضافه شد ✅"

        conn.close()

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        return ConversationHandler.END

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


new_social_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(new_social_link_help, pattern='up_twiter'),
                  CallbackQueryHandler(new_social_link_help, pattern='up_twich'),
                  CallbackQueryHandler(new_social_link_help, pattern='up_discord'),
                  CallbackQueryHandler(new_social_link_help, pattern='up_instagram'),
                  CallbackQueryHandler(new_social_link_help, pattern='up_youtube'),
                  CallbackQueryHandler(new_social_link_help, pattern='up_facebook'),
                  CallbackQueryHandler(new_social_link_help, pattern='up_website')],
    states={
        NEW_SOCIAL_LINK: [MessageHandler(Filters.text & ~Filters.command, new_social_link_handler_help_link)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# ---------------------------------------------------------------------------------------


def new_download_link_help(update, context):
    query = update.callback_query
    context.user_data['download_link'] = query.data
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New Link."
    if lan == "fa":
        text = "• لینک جدید را بفرستید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]
    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return NEW_DOWNLOAD_LINK


def new_download_link_handler_help_link(update, context):
    lan = what_lang(update.message.chat_id)
    key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p")]]
    try:
        image_type = context.user_data['download_link']
        rb = update.message.text
        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sss = image_type.replace('up_', '')

        sql = ''' UPDATE Download_and_update SET {0} = ?  '''.format(sss)
        c.execute(sql, (rb,))

        conn.commit()

        text = "New Link added successfully ✅"
        if lan == "fa":
            key = [[InlineKeyboardButton("برگشت به پنل ادمین", callback_data="admin_p")]]
            text = "لینک جدید با موفقیت اضافه شد ✅"

        conn.close()

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        return ConversationHandler.END

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


new_download_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(new_download_link_help, pattern='up_google_play'),
                  CallbackQueryHandler(new_download_link_help, pattern='up_micet'),
                  CallbackQueryHandler(new_download_link_help, pattern='up_appstore'),
                  CallbackQueryHandler(new_download_link_help, pattern='up_farsroid'),
                  CallbackQueryHandler(new_download_link_help, pattern='up_apkpure'),
                  CallbackQueryHandler(new_download_link_help, pattern='up_tinroid')],
    states={
        NEW_DOWNLOAD_LINK: [MessageHandler(Filters.text & ~Filters.command, new_download_link_handler_help_link)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# ----------------------------------------------------------------------------------------------------


def edit_main_text_fifa(update, context):
    query = update.callback_query
    context.user_data['main_fifa_text'] = query.data
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New farsi Main Text."
    if lan == "fa":
        text = "• متن جدید فارسی را ارسال کنید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]

    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return MAIN_TEXT_FIFA_FA


def handle_farsi_edit_main_text_help(update, context):
    lan = what_lang(update.message.chat_id)
    try:
        new_text = str(update.message.text)
        context.user_data['new_farsi_text_main_fifa'] = new_text
        text = "Send New English Text."
        if lan == "fa":
            text = "متن جدید انگلیسی را ارسال کنید."

        context.bot.send_message(chat_id=update.message.chat_id, text=text)
        return MAIN_TEXT_FIFA_EN
    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


def handle_new_english_main_text_help(update, context):
    lan = what_lang(update.message.chat_id)
    try:
        new_english_text = str(update.message.text)
        new_farsi_text = context.user_data['new_farsi_text_main_fifa']
        qqq = context.user_data['main_fifa_text']
        key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p")]]

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        if qqq == "up_fifaprize":
            sql = ''' INSERT INTO Fifa_prizee(info_fa, info_en) VALUES(?,?) '''
            c.execute(sql, (new_farsi_text, new_english_text))

        elif qqq == "up_fifrenders":
            sql = ''' INSERT INTO Fifa_renders(info_fa, info_en) VALUES(?,?) '''
            c.execute(sql, (new_farsi_text, new_english_text))

        elif qqq == "up_futbin":
            sql = ''' INSERT INTO Futbin(info_fa, info_en) VALUES(?,?) '''
            c.execute(sql, (new_farsi_text, new_english_text))

        conn.commit()
        conn.close()

        text = "new texts add ✅"
        if lan == "fa":
            text = "متن های جدید با موفقیت اضافه شدند ✅"
            key = [[InlineKeyboardButton("پنل ادمین", callback_data="admin_p")]]

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        context.user_data.clear()
        return ConversationHandler.END
    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


new_fifa_main_text_con_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_main_text_fifa, pattern='up_fifaprize'),
                  CallbackQueryHandler(edit_main_text_fifa, pattern='up_fifrenders'),
                  CallbackQueryHandler(edit_main_text_fifa, pattern='up_futbin')],
    states={
        MAIN_TEXT_FIFA_FA: [MessageHandler(Filters.text & ~Filters.command, handle_farsi_edit_main_text_help)],
        MAIN_TEXT_FIFA_EN: [MessageHandler(Filters.text & ~Filters.command, handle_new_english_main_text_help)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# -----------------------------------------------------------------------------------------------------------

def edit_fifa_links(update, context):
    query = update.callback_query
    context.user_data['fifa_links_me'] = query.data
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New Link."
    if lan == "fa":
        text = "• لینک جدید را بفرستید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]
    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return NEW_LINK_FIFA


def edit_fifa_links_handler(update, context):
    lan = what_lang(update.message.chat_id)
    key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p")]]
    # try:
    link = context.user_data['fifa_links_me']

    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()
    rb = str(update.message.text)
    sss = link.replace('up', '')

    if "fp" in sss:
        y = sss.replace('fp_', '')
        sql = ''' UPDATE Fifa_prizee SET {0} = ?  '''.format(y)
        c.execute(sql, (rb,))

    if "fr" in sss:
        y = sss.replace('fr_', '')
        sql = ''' UPDATE Fifa_renders SET {0} = ?  '''.format(y)
        c.execute(sql, (rb,))

    if "fu" in sss:
        y = sss.replace('fu_', '')
        sql = ''' UPDATE Futbin SET {0} = ?  '''.format(y)
        c.execute(sql, (rb,))

    conn.commit()
    conn.close()

    text = "New Link added successfully ✅"
    if lan == "fa":
        key = [[InlineKeyboardButton("برگشت به پنل ادمین", callback_data="admin_p")]]
        text = "لینک جدید با موفقیت اضافه شد ✅"

    context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
    return ConversationHandler.END

    # except:
    #     failed(update, context, lan)
    #     context.user_data.clear()
    #     return ConversationHandler.END


fifa_link_con_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_fifa_links, pattern='upfp_site'),
                  CallbackQueryHandler(edit_fifa_links, pattern='upfp_android_app'),
                  CallbackQueryHandler(edit_fifa_links, pattern='upfu_site'),
                  CallbackQueryHandler(edit_fifa_links, pattern='upfu_android_app'),
                  CallbackQueryHandler(edit_fifa_links, pattern='upfr_site')],
    states={
        NEW_LINK_FIFA: [MessageHandler(Filters.text & ~Filters.command, edit_fifa_links_handler)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# -----------------------------------------------------------------------------------------------------------


def edit_reg_lig_main_text(update, context):
    query = update.callback_query
    query.answer()
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New farsi Main Text."
    if lan == "fa":
        text = "• متن جدید فارسی را ارسال کنید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]

    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return MAIN_TEXT_REGLIG_FA


def edit_reg_lig_main_text_fa(update, context):
    lan = what_lang(update.message.chat_id)

    try:
        new_text = str(update.message.text)
        context.user_data['new_reg_lig_main_text'] = new_text
        text = "Send New English Text."
        if lan == "fa":
            text = "متن جدید انگلیسی را ارسال کنید."

        context.bot.send_message(chat_id=update.message.chat_id, text=text)
        return MAIN_TEXT_REGLIG_EN
    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


def edit_reg_lig_main_text_en(update, context):
    lan = what_lang(update.message.chat_id)

    try:
        new_english_text = str(update.message.text)
        new_farsi_text = context.user_data['new_reg_lig_main_text']
        key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p")]]

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sql = ''' INSERT INTO Help_text_REG_LIG(info_fa, info_en) VALUES(?,?) '''
        c.execute(sql, (new_farsi_text, new_english_text))

        conn.commit()
        conn.close()

        text = "new texts add ✅"
        if lan == "fa":
            text = "متن های جدید با موفقیت اضافه شدند ✅"
            key = [[InlineKeyboardButton("پنل ادمین", callback_data="admin_p")]]

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        context.user_data.clear()
        return ConversationHandler.END
    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


new_reg_lig_con_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_reg_lig_main_text, pattern='ch_le')],
    states={
        MAIN_TEXT_REGLIG_FA: [MessageHandler(Filters.text & ~Filters.command, edit_reg_lig_main_text_fa)],
        MAIN_TEXT_REGLIG_EN: [MessageHandler(Filters.text & ~Filters.command, edit_reg_lig_main_text_en)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# ------------------------------------------------------------------------------------------------------------


def edit_event_main_text(update, context):
    query = update.callback_query
    query.answer()
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New farsi Main Text."
    if lan == "fa":
        text = "• متن جدید فارسی را ارسال کنید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]

    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return MAIN_TEXT_EVENT_FA


def edit_event_main_text_fa(update, context):
    lan = what_lang(update.message.chat_id)

    try:
        new_text = str(update.message.text)
        context.user_data['new_events_main_text'] = new_text
        text = "Send New English Text."
        if lan == "fa":
            text = "متن جدید انگلیسی را ارسال کنید."

        context.bot.send_message(chat_id=update.message.chat_id, text=text)
        return MAIN_TEXT_EVENT_EN
    except:
        failed(update, message, lan)
        context.user_data.clear()
        return ConversationHandler.END


def edit_event_main_text_en(update, context):
    lan = what_lang(update.message.chat_id)

    try:
        new_english_text = str(update.message.text)
        new_farsi_text = context.user_data['new_events_main_text']
        key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p")]]

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sql = ''' INSERT INTO Main_text_Event(info_fa, info_en) VALUES(?,?) '''
        c.execute(sql, (new_farsi_text, new_english_text))

        conn.commit()
        conn.close()

        text = "new texts add ✅"
        if lan == "fa":
            text = "متن های جدید با موفقیت اضافه شدند ✅"
            key = [[InlineKeyboardButton("پنل ادمین", callback_data="admin_p")]]

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        context.user_data.clear()
        return ConversationHandler.END

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


new_event_con_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_event_main_text, pattern='ch_rf')],
    states={
        MAIN_TEXT_EVENT_FA: [MessageHandler(Filters.text & ~Filters.command, edit_event_main_text_fa)],
        MAIN_TEXT_EVENT_EN: [MessageHandler(Filters.text & ~Filters.command, edit_event_main_text_en)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# --------------------------------------------------------------------------------------------------------------


def add_event(update, context):
    query = update.callback_query
    query.answer()
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New EVENT info (Text)."
    if lan == "fa":
        text = "• متن ایونت جدید را ارسال کنید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]

    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return EVENTS_INFO


def add_event_info_handler(update, context):
    lan = what_lang(update.message.chat_id)

    try:
        new_text = str(update.message.text)
        context.user_data['new_event'] = new_text
        text = "Send New EVENT link."
        if lan == "fa":
            text = "لینک ایونت جدید را ارسال کنید."

        context.bot.send_message(chat_id=update.message.chat_id, text=text)
        return EVENTS_LINK
    except:
        failed(update, message, lan)
        context.user_data.clear()
        return ConversationHandler.END


def add_event_link_handler(update, context):
    lan = what_lang(update.message.chat_id)

    try:
        link = str(update.message.text)
        texts = context.user_data['new_event']
        key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p"),
                InlineKeyboardButton("Add Event", callback_data="add_event")]]

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sql = ''' INSERT INTO Event(info, link) VALUES(?,?) '''
        c.execute(sql, (texts, link))

        conn.commit()
        conn.close()

        text = "new EVENT add ✅"
        if lan == "fa":
            text = "ایونت جدید با موفقیت اضافه شد ✅"
            key = [[InlineKeyboardButton("پنل ادمین", callback_data="admin_p"),
                    InlineKeyboardButton("اضافه کردن ایونت", callback_data="add_event")]]

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        context.user_data.clear()
        return ConversationHandler.END

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


add_event_con_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_event, pattern='add_event')],
    states={
        EVENTS_INFO: [MessageHandler(Filters.text & ~Filters.command, add_event_info_handler)],
        EVENTS_LINK: [MessageHandler(Filters.text & ~Filters.command, add_event_link_handler)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# ----------------------------------------------------------------------------------------------------------------

def edit_help_link_main_text(update, context):
    query = update.callback_query
    query.answer()
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New farsi Main Text."
    if lan == "fa":
        text = "• متن جدید فارسی را ارسال کنید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]

    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return MAIN_TEXT_HL_FA


def edit_help_link_main_text_fa_han(update, context):
    lan = what_lang(update.message.chat_id)

    try:
        new_text = str(update.message.text)
        context.user_data['farsi_main_text_hl'] = new_text
        text = "Send New English Text."
        if lan == "fa":
            text = "متن جدید انگلیسی را ارسال کنید."

        context.bot.send_message(chat_id=update.message.chat_id, text=text)
        return MAIN_TEXT_HL_EN
    except:
        failed(update, message, lan)
        context.user_data.clear()
        return ConversationHandler.END


def edit_help_link_main_text_en_han(update, context):
    lan = what_lang(update.message.chat_id)

    try:
        new_english_text = str(update.message.text)
        new_farsi_text = context.user_data['farsi_main_text_hl']
        key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p")]]

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sql = ''' INSERT INTO help_link_main_text(info_fa, info_en) VALUES(?,?) '''
        c.execute(sql, (new_farsi_text, new_english_text))

        conn.commit()
        conn.close()

        text = "new texts add ✅"
        if lan == "fa":
            text = "متن های جدید با موفقیت اضافه شدند ✅"
            key = [[InlineKeyboardButton("پنل ادمین", callback_data="admin_p")]]

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        context.user_data.clear()
        return ConversationHandler.END

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


new_help_lenk_main_text = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_help_link_main_text, pattern='ch_mt_hl')],
    states={
        MAIN_TEXT_HL_FA: [MessageHandler(Filters.text & ~Filters.command, edit_help_link_main_text_fa_han)],
        MAIN_TEXT_HL_EN: [MessageHandler(Filters.text & ~Filters.command, edit_help_link_main_text_en_han)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# ---------------------------------------------------------------------------------------------------------------


def edit_ja_over(update, context):
    query = update.callback_query
    query.answer()
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New farsi Main Text."
    if lan == "fa":
        text = "• متن جدید فارسی را ارسال کنید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]

    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return NEW_JH_TEXT_FA


def edit_ja_over_fa_handler(update, context):
    lan = what_lang(update.message.chat_id)
    try:
        new_text = str(update.message.text)
        context.user_data['ew_text'] = new_text
        text = "Send New English Text."
        if lan == "fa":
            text = "متن جدید انگلیسی را ارسال کنید."

        context.bot.send_message(chat_id=update.message.chat_id, text=text)
        return NEW_JH_TEXT_EN
    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


def edit_ja_over_en_handler(update, context):
    lan = what_lang(update.message.chat_id)
    try:
        new_english_text = str(update.message.text)
        new_farsi_text = context.user_data['ew_text']
        key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p"),
                InlineKeyboardButton("Edit Again", callback_data="up_help_se_main_text")]]

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sql = ''' INSERT INTO Everlasting_world(info_fa, info_en) VALUES(?,?) '''
        c.execute(sql, (new_farsi_text, new_english_text))

        conn.commit()
        conn.close()

        text = "new texts add ✅"
        if lan == "fa":
            text = "متن های جدید با موفقیت اضافه شدند ✅"
            key = [[InlineKeyboardButton("پنل ادمین", callback_data="admin_p"),
                    InlineKeyboardButton("ویرایش دوباره", callback_data="up_help_se_main_text")]]

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        context.user_data.clear()
        return ConversationHandler.END
    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


jh_con_han = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_ja_over, pattern='ch_ew')],
    states={
        NEW_JH_TEXT_FA: [MessageHandler(Filters.text & ~Filters.command, edit_ja_over_fa_handler)],
        NEW_JH_TEXT_EN: [MessageHandler(Filters.text & ~Filters.command, edit_ja_over_en_handler)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# -------------------------------------------------------------------------------------------------------------

def edit_start_text(update, context):
    query = update.callback_query
    query.answer()
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New farsi Text."
    if lan == "fa":
        text = "• متن جدید فارسی را ارسال کنید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]

    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return BOT_START_TEXT_FA


def edit_start_text_fa(update, context):
    lan = what_lang(update.message.chat_id)

    try:
        new_text = str(update.message.text)
        context.user_data['farsi_main_txt'] = new_text
        text = "Send New English Text."
        if lan == "fa":
            text = "متن جدید انگلیسی را ارسال کنید."

        context.bot.send_message(chat_id=update.message.chat_id, text=text)
        return BOT_START_TEXT_EN
    except:
        failed(update, message, lan)
        context.user_data.clear()
        return ConversationHandler.END


def edit_start_text_en(update, context):
    lan = what_lang(update.message.chat_id)

    try:
        new_english_text = str(update.message.text)
        new_farsi_text = context.user_data['farsi_main_txt']
        key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p")]]

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sql = ''' INSERT INTO Bot_Main_Text(info_fa, info_en) VALUES(?,?) '''
        c.execute(sql, (new_farsi_text, new_english_text))

        conn.commit()
        conn.close()

        text = "new texts add ✅"
        if lan == "fa":
            text = "متن های جدید با موفقیت اضافه شدند ✅"
            key = [[InlineKeyboardButton("پنل ادمین", callback_data="admin_p")]]

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        context.user_data.clear()
        return ConversationHandler.END

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


edit_start_text_handel = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_start_text, pattern='edit_start_text')],
    states={
        BOT_START_TEXT_FA: [MessageHandler(Filters.text & ~Filters.command, edit_start_text_fa)],
        BOT_START_TEXT_EN: [MessageHandler(Filters.text & ~Filters.command, edit_start_text_en)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# -----------------------------------------------------------------------------------------------------------


def edit_choice_text(update, context):
    query = update.callback_query
    query.answer()
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New farsi Text."
    if lan == "fa":
        text = "• متن جدید فارسی را ارسال کنید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]

    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return BOT_PANEL_TEXT_FA


def edit_choice_text_fa(update, context):
    lan = what_lang(update.message.chat_id)

    try:
        new_text = str(update.message.text)
        context.user_data['farsi_panel_text'] = new_text
        text = "Send New English Text."
        if lan == "fa":
            text = "متن جدید انگلیسی را ارسال کنید."

        context.bot.send_message(chat_id=update.message.chat_id, text=text)
        return BOT_PANEL_TEXT_EN
    except:
        failed(update, message, lan)
        context.user_data.clear()
        return ConversationHandler.END


def edit_choice_text_en(update, context):
    lan = what_lang(update.message.chat_id)

    try:
        new_english_text = str(update.message.text)
        new_farsi_text = context.user_data['farsi_panel_text']
        key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p")]]

        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sql = ''' INSERT INTO Bot_Choice_Text(info_fa, info_en) VALUES(?,?) '''
        c.execute(sql, (new_farsi_text, new_english_text))

        conn.commit()
        conn.close()

        text = "new texts add ✅"
        if lan == "fa":
            text = "متن های جدید با موفقیت اضافه شدند ✅"
            key = [[InlineKeyboardButton("پنل ادمین", callback_data="admin_p")]]

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        context.user_data.clear()
        return ConversationHandler.END

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


edit_choice_text_handel = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_choice_text, pattern='edit_panel_text')],
    states={
        BOT_PANEL_TEXT_FA: [MessageHandler(Filters.text & ~Filters.command, edit_choice_text_fa)],
        BOT_PANEL_TEXT_EN: [MessageHandler(Filters.text & ~Filters.command, edit_choice_text_en)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,
)


# ----------------------------------------------------------------------------------------------------------


def join_text(update, context):
    query = update.callback_query
    lan = what_lang(query.message.chat_id)
    keyboard_kld = [[InlineKeyboardButton("Cancle", callback_data="cancle_leage")]]
    text = "• Send New TEXT."
    if lan == "fa":
        text = "• متن جدید را ارسال کنید."
        keyboard_kld = [[InlineKeyboardButton("انصراف", callback_data="cancle_leage")]]
    context.bot.send_message(text=text, chat_id=query.message.chat_id, reply_markup=InlineKeyboardMarkup(keyboard_kld))

    return JOIN_TEXT


def join_handle(update, context):
    new_text = str(update.message.text)
    lan = what_lang(update.message.chat_id)
    key = [[InlineKeyboardButton("Admin Panel", callback_data="admin_p")]]
    try:
        conn = sqlite3.connect('fifa.db')
        c = conn.cursor()

        sql = ''' INSERT INTO Join_Text(info) VALUES(?) '''
        c.execute(sql, (new_text,))

        conn.commit()

        text = "New Text added successfully ✅"
        if lan == "fa":
            key = [[InlineKeyboardButton("برگشت به پنل ادمین", callback_data="admin_p")]]
            text = "متن با موفقیت اضافه شد ✅"

        conn.close()

        context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(key))
        context.user_data.clear()
        return ConversationHandler.END

    except:
        failed(update, context, lan)
        context.user_data.clear()
        return ConversationHandler.END


join_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(join_text, pattern='edit_join_text')],
    states={
        JOIN_TEXT: [MessageHandler(Filters.text & ~Filters.command, join_handle)]
    },
    fallbacks=[CallbackQueryHandler(cancle_leag, pattern='cancle_leage')],
    conversation_timeout=200,

)
