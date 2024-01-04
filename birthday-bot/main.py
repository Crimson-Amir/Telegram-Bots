from telegram.ext import *

from ApiKey import Key
from Srart_ActivateTheUser import bot_start, select_lang, choose, help_bot
from Other import create_database, all_births, delete_birth, say_update
from MainOption_keys import (set_birthday_ways, set_birthday_text, set_birthday_video, see_birthday, support, guidance,
                             setting)
from Actions import filter_words, clear_data
from Quidance import birth_orders, information, permissions
from Settings import (cal, greetings, language, reminder, status_permission, change_status, change_language,
                      change_reminder, change_permisson, change_cal)


# main -----------------------------------------------------


def main():
    updater = Updater(Key)

    create_database()

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', select_lang))
    dp.add_handler(CommandHandler('help', help_bot))
    dp.add_handler(CommandHandler('all', all_births))
    dp.add_handler(CommandHandler('db', delete_birth))
    dp.add_handler(CommandHandler('say_update', say_update))

    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, select_lang))
    dp.add_handler(MessageHandler(Filters.text, filter_words))
    dp.add_handler(MessageHandler(Filters.voice, filter_words))

    # Main
    dp.add_handler(CallbackQueryHandler(support, pattern='support'))
    dp.add_handler(CallbackQueryHandler(clear_data, pattern='clear_data'))
    dp.add_handler(CallbackQueryHandler(see_birthday, pattern='see_birthday'))
    dp.add_handler(CallbackQueryHandler(help_bot, pattern='help_bot'))

    dp.add_handler(CallbackQueryHandler(set_birthday_ways, pattern='set_birthday'))
    dp.add_handler(CallbackQueryHandler(set_birthday_text, pattern='1set_birthday_text'))
    dp.add_handler(CallbackQueryHandler(set_birthday_video, pattern='2set_birthday_video'))

    dp.add_handler(CallbackQueryHandler(choose, pattern='choose'))
    dp.add_handler(CallbackQueryHandler(guidance, pattern='guidance'))
    dp.add_handler(CallbackQueryHandler(setting, pattern='settings'))

    dp.add_handler(CallbackQueryHandler(bot_start, pattern='fa'))
    dp.add_handler(CallbackQueryHandler(bot_start, pattern='en'))

    # guidance
    dp.add_handler(CallbackQueryHandler(birth_orders, pattern='birthday_orders'))
    dp.add_handler(CallbackQueryHandler(information, pattern='information'))
    dp.add_handler(CallbackQueryHandler(permissions, pattern='permissions'))

    # setting
    dp.add_handler(CallbackQueryHandler(greetings, pattern='greetings'))
    dp.add_handler(CallbackQueryHandler(language, pattern='language'))
    dp.add_handler(CallbackQueryHandler(reminder, pattern='reminder'))
    dp.add_handler(CallbackQueryHandler(status_permission, pattern='status_permission'))
    dp.add_handler(CallbackQueryHandler(cal, pattern='calenders'))

    dp.add_handler(CallbackQueryHandler(change_language, pattern='us'))
    dp.add_handler(CallbackQueryHandler(change_language, pattern='ir'))
    dp.add_handler(CallbackQueryHandler(change_cal, pattern='jala'))
    dp.add_handler(CallbackQueryHandler(change_cal, pattern='greg'))
    dp.add_handler(CallbackQueryHandler(change_status, pattern='change_status'))
    dp.add_handler(CallbackQueryHandler(change_reminder, pattern='ch_remind'))
    dp.add_handler(CallbackQueryHandler(change_reminder, pattern='more'))
    dp.add_handler(CallbackQueryHandler(change_reminder, pattern='fewer'))

    dp.add_handler(CallbackQueryHandler(status_permission, pattern='status_permission'))
    dp.add_handler(CallbackQueryHandler(change_permisson, pattern='all'))
    dp.add_handler(CallbackQueryHandler(change_permisson, pattern='spec'))
    dp.add_handler(CallbackQueryHandler(change_permisson, pattern='admin'))

    # dp.add_handler(CallbackQueryHandler(cs, pattern='cs_1'))
    # dp.add_handler(CallbackQueryHandler(cs, pattern='cs_2'))
    # dp.add_handler(CallbackQueryHandler(cs, pattern='cs_3'))
    # dp.add_handler(CallbackQueryHandler(cs, pattern='cs_4'))
    # dp.add_handler(CallbackQueryHandler(cs, pattern='cs_5'))

    updater.start_polling(1)
    updater.idle()


if __name__ == '__main__':
    main()
