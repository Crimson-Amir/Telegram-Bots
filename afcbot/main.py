from telegram.ext import *

from ApiKey import Key
from keyboards import keyboard, keyboard_fa, lang_key
from Srart_ActivateTheUser import bot_start, select_lang, choose, help_bot, button
from Other import what_lang, create_database, delete_all_me, say_update
from MainOption_keys import (check_ivents, support, help_link, setting,
                             quid_help, best_cart, set_league, statistics,
                             regions_fun, account_protection_fun, good_team,
                             ural_calculation_formula_fun, ew_wor_show,
                             fifa_mobile_social_show, fifa_mobile_social_show_now,
                             helps_sites_realy, fifa_prizee, fifa_renders, futbin,
                             best_player_show, send_player_image, send_player_image_cheap,
                             send_best_player_cheap, conv_handler, inline_query)
from Actions import filter_words
from Quidance import permissions
from Settings import langueg_code, language, status_permission_code, status_permission, change_language, change_permisson
from Admin_panel import (new_admin_conversation_handler, admin_panel, up_help_section,
                         up_best_cart, up_support, up_help_link, view_bot_admin, view_bot_users,
                         new_help_main_text_conversation_handler, new_admin_amar_image_handler,
                         new_region_text_conversation_handler, new_ap_text_conversation_handler,
                         new_gt_text_conversation_handler, new_ural_conversation_handler,
                         new_support_main_text_conversation_handler, new_support_email_conversation_handler,
                         up_best_cart_best_player, up_cheap_player_post, new_image_handler, new_cheap_image_handler,
                         new_best_cart_main_text_conversation_handler, new_social_handler, new_tabale_help_link,
                         new_tabale_best_player, fifa_mobile_section, download_and_update, new_download_handler,
                         new_fifa_main_text_con_handler, fifa_link_con_handler, up_help_site_link, close, new_reg_lig_con_handler,
                         new_event_con_handler, new_support_telegram_id_conversation_handler, new_help_lenk_main_text,
                         add_event_con_handler, new_tabale_event, remove_admin_conversation_handler, edit_start_text_handel,
                         edit_choice_text_handel, join_conversation_handler, jh_con_han)


# main -----------------------------------------------------

def main():
    updater = Updater(Key)

    create_database()

    dp = updater.dispatcher
    dp.add_handler(InlineQueryHandler(inline_query))

    dp.add_handler(CommandHandler('start', select_lang))
    dp.add_handler(CommandHandler('help', help_bot))
    dp.add_handler(CommandHandler('admin', admin_panel))
    dp.add_handler(CommandHandler('say_update', say_update))
    dp.add_handler(CommandHandler('db', delete_all_me))

    dp.add_handler(CallbackQueryHandler(admin_panel, pattern='admin_p'))
    dp.add_handler(CallbackQueryHandler(new_tabale_event, pattern='cr_ev_ta'))

    dp.add_handler(CallbackQueryHandler(up_help_section, pattern='ch_he'))

    dp.add_handler(CallbackQueryHandler(up_help_section, pattern='ch_he'))
    dp.add_handler(CallbackQueryHandler(up_best_cart, pattern='ch_bc'))
    dp.add_handler(CallbackQueryHandler(up_support, pattern='ch_su'))
    dp.add_handler(CallbackQueryHandler(up_help_link, pattern='ch_hl'))
    dp.add_handler(CallbackQueryHandler(view_bot_admin, pattern='view_admin'))
    dp.add_handler(CallbackQueryHandler(view_bot_users, pattern='view_users'))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, select_lang))
    # dp.add_handler(MessageHandler(Filters.text, filter_words))
    # dp.add_handler(MessageHandler(Filters.voice, filter_words))

    dp.add_handler(CallbackQueryHandler(fifa_mobile_section, pattern='ch_ms'))
    dp.add_handler(CallbackQueryHandler(download_and_update, pattern='up_download_and_update'))
    dp.add_handler(CallbackQueryHandler(up_help_site_link, pattern='up_help_site'))
    dp.add_handler(CallbackQueryHandler(close, pattern='close'))

    dp.add_handler(CallbackQueryHandler(new_tabale_help_link, pattern='create_help_link_tabale'))
    dp.add_handler(CallbackQueryHandler(new_tabale_best_player, pattern='create_best_player_tabale'))

    dp.add_handler(new_admin_conversation_handler)
    dp.add_handler(new_help_main_text_conversation_handler)
    dp.add_handler(conv_handler)
    dp.add_handler(new_admin_amar_image_handler)
    dp.add_handler(new_region_text_conversation_handler)
    dp.add_handler(new_ap_text_conversation_handler)
    dp.add_handler(new_gt_text_conversation_handler)
    dp.add_handler(new_ural_conversation_handler)
    dp.add_handler(new_support_main_text_conversation_handler)
    dp.add_handler(new_support_email_conversation_handler)
    dp.add_handler(new_image_handler)
    dp.add_handler(new_cheap_image_handler)
    dp.add_handler(new_best_cart_main_text_conversation_handler)
    dp.add_handler(new_social_handler)
    dp.add_handler(new_download_handler)
    dp.add_handler(new_fifa_main_text_con_handler)
    dp.add_handler(fifa_link_con_handler)
    dp.add_handler(new_reg_lig_con_handler)
    dp.add_handler(new_event_con_handler)
    dp.add_handler(new_support_telegram_id_conversation_handler)
    dp.add_handler(new_help_lenk_main_text)
    dp.add_handler(add_event_con_handler)
    dp.add_handler(remove_admin_conversation_handler)
    dp.add_handler(edit_start_text_handel)
    dp.add_handler(edit_choice_text_handel)
    dp.add_handler(join_conversation_handler)
    dp.add_handler(jh_con_han)

    dp.add_handler(CallbackQueryHandler(check_ivents, pattern='check_ivents'))
    dp.add_handler(CallbackQueryHandler(best_cart, pattern='best_cart'))
    dp.add_handler(CallbackQueryHandler(quid_help, pattern='help_bot'))
    dp.add_handler(CallbackQueryHandler(help_link, pattern='help_link'))
    dp.add_handler(CallbackQueryHandler(support, pattern='support'))
    dp.add_handler(CallbackQueryHandler(set_league, pattern='set_league'))
    dp.add_handler(CallbackQueryHandler(setting, pattern='settings'))

    dp.add_handler(CallbackQueryHandler(choose, pattern='choose'))

    dp.add_handler(CallbackQueryHandler(button, pattern='start_bot'))
    dp.add_handler(CallbackQueryHandler(bot_start, pattern='fa'))
    dp.add_handler(CallbackQueryHandler(bot_start, pattern='en'))

    dp.add_handler(CallbackQueryHandler(statistics, pattern='statistics'))
    dp.add_handler(CallbackQueryHandler(regions_fun, pattern='region'))
    dp.add_handler(CallbackQueryHandler(account_protection_fun, pattern='account_protection'))
    dp.add_handler(CallbackQueryHandler(ural_calculation_formula_fun, pattern='ural_formula'))
    dp.add_handler(CallbackQueryHandler(good_team, pattern='good_team'))

    dp.add_handler(CallbackQueryHandler(up_best_cart_best_player, pattern='best_player_change'))
    dp.add_handler(CallbackQueryHandler(up_cheap_player_post, pattern='cheap_player_change'))

    dp.add_handler(CallbackQueryHandler(ew_wor_show, pattern='everlasting_world'))
    dp.add_handler(CallbackQueryHandler(fifa_mobile_social_show, pattern='fifa_mobile'))
    dp.add_handler(CallbackQueryHandler(fifa_mobile_social_show_now, pattern='download_update'))
    dp.add_handler(CallbackQueryHandler(helps_sites_realy, pattern='helpful_site'))
    dp.add_handler(CallbackQueryHandler(fifa_prizee, pattern='fifa_prizee'))
    dp.add_handler(CallbackQueryHandler(fifa_renders, pattern='fifa_renders'))
    dp.add_handler(CallbackQueryHandler(futbin, pattern='futbin'))

    dp.add_handler(CallbackQueryHandler(best_player_show, pattern='best_player'))
    dp.add_handler(CallbackQueryHandler(send_best_player_cheap, pattern='cheap_best'))

    dp.add_handler(CallbackQueryHandler(permissions, pattern='permissions'))
    dp.add_handler(CallbackQueryHandler(language, pattern='language'))
    dp.add_handler(CallbackQueryHandler(change_language, pattern='us'))
    dp.add_handler(CallbackQueryHandler(change_language, pattern='ir'))
    dp.add_handler(CallbackQueryHandler(status_permission, pattern='status_permission'))
    dp.add_handler(CallbackQueryHandler(change_permisson, pattern='all'))
    dp.add_handler(CallbackQueryHandler(change_permisson, pattern='spec'))
    dp.add_handler(CallbackQueryHandler(change_permisson, pattern='admin'))

    dp.add_handler(CallbackQueryHandler(send_player_image, pattern='seb_gk'))
    dp.add_handler(CallbackQueryHandler(send_player_image, pattern='seb_cb'))
    dp.add_handler(CallbackQueryHandler(send_player_image, pattern='seb_lb'))
    dp.add_handler(CallbackQueryHandler(send_player_image, pattern='seb_rb'))
    dp.add_handler(CallbackQueryHandler(send_player_image, pattern='seb_cm'))
    dp.add_handler(CallbackQueryHandler(send_player_image, pattern='seb_lm'))
    dp.add_handler(CallbackQueryHandler(send_player_image, pattern='seb_rm'))
    dp.add_handler(CallbackQueryHandler(send_player_image, pattern='seb_cam'))
    dp.add_handler(CallbackQueryHandler(send_player_image, pattern='seb_cdm'))
    dp.add_handler(CallbackQueryHandler(send_player_image, pattern='seb_rw'))
    dp.add_handler(CallbackQueryHandler(send_player_image, pattern='seb_lw'))
    dp.add_handler(CallbackQueryHandler(send_player_image, pattern='seb_st'))
    dp.add_handler(CallbackQueryHandler(send_player_image, pattern='seb_cf'))

    dp.add_handler(CallbackQueryHandler(send_player_image_cheap, pattern='sec_gk'))
    dp.add_handler(CallbackQueryHandler(send_player_image_cheap, pattern='sec_cb'))
    dp.add_handler(CallbackQueryHandler(send_player_image_cheap, pattern='sec_lb'))
    dp.add_handler(CallbackQueryHandler(send_player_image_cheap, pattern='sec_rb'))
    dp.add_handler(CallbackQueryHandler(send_player_image_cheap, pattern='sec_cm'))
    dp.add_handler(CallbackQueryHandler(send_player_image_cheap, pattern='sec_lm'))
    dp.add_handler(CallbackQueryHandler(send_player_image_cheap, pattern='sec_rm'))
    dp.add_handler(CallbackQueryHandler(send_player_image_cheap, pattern='sec_cam'))
    dp.add_handler(CallbackQueryHandler(send_player_image_cheap, pattern='sec_cdm'))
    dp.add_handler(CallbackQueryHandler(send_player_image_cheap, pattern='sec_rw'))
    dp.add_handler(CallbackQueryHandler(send_player_image_cheap, pattern='sec_lw'))
    dp.add_handler(CallbackQueryHandler(send_player_image_cheap, pattern='sec_st'))
    dp.add_handler(CallbackQueryHandler(send_player_image_cheap, pattern='sec_cf'))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
