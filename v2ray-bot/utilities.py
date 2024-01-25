import datetime
import arrow
import pytz
from private import telegram_bot_token, ADMIN_CHAT_ID
from private import ADMIN_CHAT_ID
import requests


def human_readable(number):
    return arrow.get(number).humanize(locale="fa-ir")

def not_ready_yet(update, context):
    query = update.callback_query
    query.answer(text="ببخشید، درحال توسعه است.", show_alert=False)


def something_went_wrong(update, context):
    query = update.callback_query
    query.answer(text="مشکلی وجود دارد!", show_alert=False)


def just_for_show(update, context):
    query = update.callback_query
    query.answer(text="این دکمه برای نمایش دادن اطلاعات است!", show_alert=False)


def report_problem_to_admin(context, text):
    text = ("🔴 Report Problem in Bot\n\n"
            f"{text}")
    context.bot.send_message(ADMIN_CHAT_ID, text, parse_mode='html')


def ready_report_problem_to_admin(context, text, chat_id, error, detail=None):
    text = ("🔴 Report Problem in Bot\n\n"
            f"Something Went Wrong In <b>{text}</b> Section."
            f"\nUser ID: {chat_id}"
            f"\nError Type: {type(error).__name__}"
            f"\nError Reason:\n{error}")

    text += f"\nDetail:\n {detail}" if detail else ''
    context.bot.send_message(ADMIN_CHAT_ID, text, parse_mode='html')
    print(f'* REPORT TO ADMIN SUCCESS: ERR: {error}')


def format_traffic(traffic, without_text=None):
    if int(traffic) < 1:
        megabytes = traffic * 1024
        if without_text:
            return int(megabytes)
        return f"{int(megabytes)} مگابایت"
    else:
        return f"{traffic} گیگابایت"

def record_operation_in_file(chat_id, status_of_pay, price, name_of_operation, context, operation=1):
    try:
        if operation:
            pay_emoji = '💰'
            status_of_operation = 'دریافت پول'
        else:
            pay_emoji = '💸'
            status_of_operation = 'پرداخت پول'

        status_text = '🟢 تایید شده' if status_of_pay else '🔴 تایید نشده'
        date = datetime.datetime.now(pytz.timezone('Asia/Tehran')).strftime('%Y/%m/%d - %H:%M:%S')

        text = (f"\n\n{pay_emoji} {status_of_operation} | {status_text}"
                f"\nمبلغ تراکنش: {price:,} تومان"
                f"\nنام تراکنش: {name_of_operation}"
                f"\nتاریخ: {date}")

        with open(f'financial_transactions/{chat_id}.txt', 'a', encoding='utf-8') as e:
            e.write(text)
        return True

    except Exception as e:
        ready_report_problem_to_admin(context,'APLLY CARD PAY', chat_id, e)
        return False


def send_service_to_customer_report(context, status, chat_id, error=None, service_name=None, more_detail=None):
    text = 'SEND SERVICE TO USER'
    text = f'🟢 {text} SUCCESSFULL' if status else f'🔴 {text} FAILED'
    text += f'\n\nUSER ID: {chat_id}'
    text += f'\nSERVICE NAME: {service_name}'

    if not more_detail:
        context.bot.send_message(ADMIN_CHAT_ID, text)
    else:
        if error:
            text += f'\nERROR TYPE: {type(error).__name__}'
            text += f'\nERROR REASON:\n {error}'
        text += f'\nMORE DETAIL:\n {more_detail}'
        context.bot.send_message(ADMIN_CHAT_ID, text)


def report_problem_to_admin_witout_context(text, chat_id, error, detail=None):
    text = ("🔴 Report Problem in Bot\n\n"
            f"Something Went Wrong In <b>{text}</b> Section."
            f"\nUser ID: {chat_id}"
            f"\nError Type: {type(error).__name__}"
            f"\nError Reason:\n{error}")
    text += f"\nDetail:\n {detail}" if detail else ''
    telegram_bot_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    requests.post(telegram_bot_url, data={'chat_id': ADMIN_CHAT_ID, 'text': text})
    print(f'* REPORT TO ADMIN SUCCESS: ERR: {error}')