from database import create_database
create_database()

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from private import BOT_TOKEN, channel_id, channel_username
from scrapping_class import Scraping
check_every_min = 1

instance = Scraping('scraping.db')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


list_of_sententces = [
    '@irsc_public'
]


def clean_message(message):
    final_return = ''

    for sententce in list_of_sententces:
        final_return = message.replace(sententce, '')

    final_return += f'\n{channel_username}'
    return final_return


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = ('این ربات برای گزارش اخبار زلزله طراحی شده است.'
            f'\nکانال ما: {channel_username}')
    await context.bot.send_message(chat_id=chat_id, text=text)


async def check_for_new_message(context: ContextTypes.DEFAULT_TYPE):
    get_new_messages = instance.eeta_scraping('https://eitaa.com/irsc_public')

    for message in get_new_messages:
        if not message: continue
        await context.bot.send_message(chat_id=channel_id, text=clean_message(message))


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.job_queue.run_repeating(check_for_new_message, interval=check_every_min * 60, first=0)
    application.run_polling()