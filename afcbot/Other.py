import sqlite3
from telegram.ext import *


def create_database():
    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS GroupData(G_Name text, user_name text, chat_id text, user_id text, data text, Member number)')
    c.execute('CREATE TABLE IF NOT EXISTS Pv_Data(U_Name text, user_name text, id text,Data text)')
    c.execute('CREATE TABLE IF NOT EXISTS Languages(lang text, chat_id text)')
    c.execute('CREATE TABLE IF NOT EXISTS Per(permison text, chat_id text)')
    c.execute('CREATE TABLE IF NOT EXISTS Specials(id text, chat_id text)')
    c.execute('CREATE TABLE IF NOT EXISTS Admins(user_id text)')

    sql = ''' INSERT INTO Admins(user_id) VALUES(?) '''
    c.execute(sql, ('5938166133',))
    conn.commit()

    # -- MAIN -- #

    c.execute('CREATE TABLE IF NOT EXISTS Bot_Main_Text(id INTEGER PRIMARY KEY, info_fa text, info_en text)')
    c.execute('CREATE TABLE IF NOT EXISTS Bot_Choice_Text(id INTEGER PRIMARY KEY, info_fa text, info_en text)')
    c.execute('CREATE TABLE IF NOT EXISTS Join_Text(id INTEGER PRIMARY KEY, info text)')
    c.execute('CREATE TABLE IF NOT EXISTS Photo_url(up_gk text, up_cb text, up_lb text, up_rb text, up_cm text,'
              'up_lm text, up_rm text, up_cam text, up_cdm text, up_rw text, up_lw text, up_st text, up_cf text, upc_gk text, upc_cb text, upc_lb text, upc_rb text, upc_cm text,'
              'upc_lm text, upc_rm text, upc_cam text, upc_cdm text, upc_rw text, upc_lw text, upc_st text, upc_cf text, Translation_of_statistics text, Ural_calculation_formula text)')

    # -- QUID_HELP -- #

    c.execute('CREATE TABLE IF NOT EXISTS Help_text_main(id INTEGER PRIMARY KEY, info_fa text, info_en text)')
    c.execute('CREATE TABLE IF NOT EXISTS Translation_of_statistics(id INTEGER PRIMARY KEY, image BLOB)')
    c.execute('CREATE TABLE IF NOT EXISTS Regions(id INTEGER PRIMARY KEY, info_fa text, image BLOB)')
    c.execute('CREATE TABLE IF NOT EXISTS Account_protection(id INTEGER PRIMARY KEY, info_fa text, video BLOB)')
    c.execute('CREATE TABLE IF NOT EXISTS Good_team_en(id INTEGER PRIMARY KEY, info_fa text, info_en text)')
    c.execute('CREATE TABLE IF NOT EXISTS Ural_calculation_formula(id INTEGER PRIMARY KEY, info_fa text, info_en text, image BLOB)')

    # -- SUPPORT -- #

    c.execute('CREATE TABLE IF NOT EXISTS Help_text_Support(id INTEGER PRIMARY KEY, info_fa text, info_en text)')
    c.execute('CREATE TABLE IF NOT EXISTS Telgram_id_support(id INTEGER PRIMARY KEY, info text)')
    c.execute('CREATE TABLE IF NOT EXISTS Email_supoort(id INTEGER PRIMARY KEY, info text)')

    # -- HELP_LINK -- #

    c.execute('CREATE TABLE IF NOT EXISTS help_link_main_text(id INTEGER PRIMARY KEY, info_fa text, info_en text)')
    c.execute('CREATE TABLE IF NOT EXISTS Everlasting_world(id INTEGER PRIMARY KEY, info_fa text, info_en text)')
    c.execute('CREATE TABLE IF NOT EXISTS FIFA_Mobile_Social(id INTEGER PRIMARY KEY, twiter text, twich text, discord text,'
              ' instagram text, youtube text, facebook text, website text)')
    c.execute('CREATE TABLE IF NOT EXISTS Download_and_update(id INTEGER PRIMARY KEY, google_play text, micet text, appstore text,'
              ' farsroid text, apkpure text, tinroid text)')
    c.execute('CREATE TABLE IF NOT EXISTS Fifa_prizee(id INTEGER PRIMARY KEY, info_fa text, info_en text, site text, android_app text)')
    c.execute('CREATE TABLE IF NOT EXISTS Fifa_renders(id INTEGER PRIMARY KEY, info_fa text, info_en text, site text)')
    c.execute('CREATE TABLE IF NOT EXISTS Futbin(id INTEGER PRIMARY KEY, info_fa text, info_en text, site text, android_app text)')

    # -- BEST_CART -- #

    c.execute('CREATE TABLE IF NOT EXISTS Help_text_BestCart(id INTEGER PRIMARY KEY, info_fa text, info_en text)')
    c.execute('CREATE TABLE IF NOT EXISTS The_Best_player(id INTEGER PRIMARY KEY, GK BLOB, CB BLOB, LB BLOB, RB BLOB, CM BLOB, LM BLOB,'
              'RM BLOB, CAM BLOB, CDM BLOB, RW BLOB, LW BLOB, ST BLOB, CF BLOB, ONE BLOB, TWO BLOB, TRE BLOB, FOUR BLOB, FIVE BLOB, SIX BLOB, SEVEN BLOB)')
    c.execute('CREATE TABLE IF NOT EXISTS Cheap_player(id INTEGER PRIMARY KEY, GK BLOB, CB BLOB, LB BLOB, RB BLOB, CM BLOB, LM text,'
              'RM BLOB, CAM BLOB, CDM BLOB, RW BLOB, LW BLOB, ST BLOB, CF BLOB, ONE BLOB, TWO BLOB, TRE BLOB, FOUR BLOB, FIVE BLOB, SIX BLOB, SEVEN BLOB)')

    # -- REG_LIG --

    c.execute('CREATE TABLE IF NOT EXISTS Help_text_REG_LIG(id INTEGER PRIMARY KEY, info_fa text, info_en text)')

    # -- EVENTS --

    c.execute('CREATE TABLE IF NOT EXISTS Event(id INTEGER PRIMARY KEY, info text, link text)')
    c.execute('CREATE TABLE IF NOT EXISTS Main_text_Event(id INTEGER PRIMARY KEY, info_fa text, info_en text)')

    conn.commit()
    conn.close()


def what_lang(chat_id):
    conn = sqlite3.connect('fifa.db')
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


def delete_all_me(update, context):
    chat_id = update.message.chat_id
    conn = sqlite3.connect('fifa.db')
    c = conn.cursor()

    c.execute("DELETE FROM Languages WHERE chat_id = {0}".format(chat_id))
    try:
        c.execute("DELETE FROM Pv_Data WHERE chat_id = {0}".format(chat_id))
    except:
        c.execute("DELETE FROM GroupData WHERE chat_id = {0}".format(chat_id))

    conn.commit()
    conn.close()


def say_update(update, context):
    conn = sqlite3.connect('fifa.db')
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
none   
"""
        if lan == "fa":
            text_2 = """
noen
"""

        try:
            context.bot.send_message(chat_id=chat_id, text=text_2, parse_mode='HTML')
        except:
            pass
    conn.commit()
    conn.close()
