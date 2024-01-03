from telegram.ext import *
from telegram import InlineKeyboardButton

keyboard = [
    # [InlineKeyboardButton("Scrutiny & Review of Events 🧮", callback_data='check_ivents')],
    #
    # [InlineKeyboardButton("Guide 📚", callback_data='help_bot'),
    #  InlineKeyboardButton("Best Cards 🥇", callback_data='best_cart')],
    #
    # [InlineKeyboardButton("Helpful Links 🌏", callback_data='help_link')],
    #
    # [InlineKeyboardButton("Register League 👔", callback_data='set_league'),
    #  InlineKeyboardButton("Support 👥", callback_data='support')],

    [InlineKeyboardButton("Setting ⚙️", callback_data='settings')],
]

keyboard_fa = [
    [InlineKeyboardButton("موشکافی و بررسی ایونت ها 🧮", callback_data='check_ivents')],

    [InlineKeyboardButton("راهنما 📚", callback_data='help_bot'),
     InlineKeyboardButton("بهترین کارت ها 🥇", callback_data='best_cart')],

    [InlineKeyboardButton("لینک های کمکی 🌏", callback_data='help_link')],

    [InlineKeyboardButton("ثبت لیگ 👔", callback_data='set_league'),
     InlineKeyboardButton("پشتیبانی 👥", callback_data='support')],

    [InlineKeyboardButton("تنظیمات ⚙️", callback_data='settings')],
]

lang_key = [[InlineKeyboardButton("English 🇺🇸", callback_data='en'),
             InlineKeyboardButton("️Persian 🇮🇷", callback_data='fa')]]

# Admin Key ----------------------------------------------------------------------------

admin_key = [[InlineKeyboardButton("Edit Start Text ⚪", callback_data="edit_start_text"),
              InlineKeyboardButton("Edit Panel Text 📃", callback_data="edit_panel_text")],
             [InlineKeyboardButton("Add Event ➕", callback_data="add_event"),
              InlineKeyboardButton("Cf Help Section 📚", callback_data='ch_he')],
             [InlineKeyboardButton("edit join text 🎴", callback_data="edit_join_text")],
             [InlineKeyboardButton("Cf Best Cards Section 🎴", callback_data="ch_bc"),
              InlineKeyboardButton("Cf Support Section 👥", callback_data="ch_su")],
             [InlineKeyboardButton("Cf Helpful Links Section 🔗", callback_data="ch_hl")],
             [InlineKeyboardButton("Cf Main Text of Register League  ⚽", callback_data="ch_le")],
             [InlineKeyboardButton("Cf Main Text of Review of Events 🔃", callback_data="ch_rf")],
             [InlineKeyboardButton("View Bot Admins 👮‍♂️", callback_data="view_admin"),
              InlineKeyboardButton("View Bot Users 🌍", callback_data="view_users")],
             [InlineKeyboardButton("Add Admin 🎗️", callback_data="add_admin"),
              InlineKeyboardButton("Remove Admin ❌", callback_data="remove_admin")],
             [InlineKeyboardButton("-- CREAT EVENT TABAL -- ", callback_data="cr_ev_ta")],
             [InlineKeyboardButton("Close", callback_data="close")]]

admin_key_fa = [[InlineKeyboardButton("ویرایش متن استارت ⚪", callback_data="edit_start_text"),
                 InlineKeyboardButton("ویرایش متن پنل اصلی 📃", callback_data="edit_panel_text")],
                [InlineKeyboardButton("اضافه کردن ایونت ➕", callback_data="add_event"),
                 InlineKeyboardButton("متن جوین اجباری 🎴", callback_data="edit_join_text")],
                [InlineKeyboardButton("تغییر قسمت راهنما 📚", callback_data='ch_he')],
                [InlineKeyboardButton("تغییر قسمت بهترین کارت ها 🎴", callback_data="ch_bc")],
                [InlineKeyboardButton("تغییر قسمت پشتیبانی 👥", callback_data="ch_su")],
                [InlineKeyboardButton("تغییر قسمت لینک های کمکی 🔗", callback_data="ch_hl")],
                [InlineKeyboardButton("تغییر متن اصلی ثبت لیگ ⚽", callback_data="ch_le")],
                [InlineKeyboardButton("تغییر متن اصلی بررسی ایونت ها 🔃", callback_data="ch_rf")],
                [InlineKeyboardButton("ادمین های ربات 👮‍♂️", callback_data="view_admin"),
                 InlineKeyboardButton("کاربران ربات 🌍", callback_data="view_users")],
                [InlineKeyboardButton("افزودن ادمین 🎗️", callback_data="add_admin"),
                 InlineKeyboardButton("حذف ادمین ❌", callback_data="remove_admin")],
                [InlineKeyboardButton("-- CREAT EVENT TABAL -- ", callback_data="cr_ev_ta")],
                [InlineKeyboardButton("بستن", callback_data="close")]]
