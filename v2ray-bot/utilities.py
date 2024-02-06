import datetime
import json

import arrow
import pytz
from private import telegram_bot_token, ADMIN_CHAT_ID
from private import ADMIN_CHAT_ID
import requests
from ranking import rank_emojis, rank_title_fa, rank_access_fa, rank_access
from sqlite_manager import ManageDb
from api_clean import XuiApiClean

api_operation = XuiApiClean()
sqlite_manager = ManageDb('v2ray')
telegram_bot_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"

def human_readable(number):
    try:
        return arrow.get(number).humanize(locale="fa-ir")

    except Exception as e:
        print(e)
        return arrow.get(number).humanize()

def not_ready_yet(update, context):
    query = update.callback_query
    query.answer(text="ببخشید، درحال توسعه است.", show_alert=False)


def alredy_have_show(update, context):
    query = update.callback_query
    query.answer(text="روی همین سرور هستید", show_alert=False)


def not_for_depleted_service(update, context):
    query = update.callback_query
    query.answer(text="این ویژگی برای سرویس های فعال است", show_alert=False)


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
    text += f'\n\nUser ID: {chat_id}'
    text += f'\nService Name: {service_name}'

    if not more_detail:
        context.bot.send_message(ADMIN_CHAT_ID, text)
    else:
        if error:
            text += f'\nERROR TYPE: {type(error).__name__}'
            text += f'\nERROR REASON:\n {error}'
        text += f'\nMORE DETAIL:\n {more_detail}'
        context.bot.send_message(ADMIN_CHAT_ID, text, parse_mode='html')


def report_problem_to_admin_witout_context(text, chat_id, error, detail=None):
    text = ("🔴 Report Problem in Bot\n\n"
            f"Something Went Wrong In {text} Section."
            f"\nUser ID: {chat_id}"
            f"\nError Type: {type(error).__name__}"
            f"\nError Reason:\n{error}")
    text += f"\nDetail:\n {detail}" if detail else ''
    telegram_bot_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    requests.post(telegram_bot_url, data={'chat_id': ADMIN_CHAT_ID, 'text': text})
    print(f'* REPORT TO ADMIN SUCCESS: ERR: {error}')


def report_problem_by_user(context, problem, user):
    text = (f'🟠 Report Problem By User'
            f'\nReport Reason: {problem}'
            f'\nUser Chat ID: {user["id"]}'
            f'\nName: {user["name"]}'
            f'\nUser Name: {user["username"]}')

    context.bot.send_message(ADMIN_CHAT_ID, text, parse_mode='html')


def report_status_to_admin(context, text, chat_id):
    text = (f'🔵 Report Status:'
            f'\nUser Chat ID: {chat_id}'
            f'\n{text}')

    context.bot.send_message(ADMIN_CHAT_ID, text, parse_mode='html')


def get_rank_and_emoji(rank):
    rank_fa = rank_title_fa.get(rank)
    rank_emoji = rank_emojis.get(rank)
    return f"{rank_fa} {rank_emoji}"


def get_access_fa(rank):
    all_access = []

    for key, value in rank_access_fa.items():
        all_access += value[1:]
        if key == rank:
            break

    return all_access


def find_next_rank(rank, level_now):
    check = 0
    for key, value in rank_access.items():
        if check == 1:
            return get_rank_and_emoji(key), value['level'][0] - level_now
        elif key == rank:
            check = 1


def message_to_user(update, context, message=None, chat_id=None):
    if not message:
        chat_id = update.message.text.replace('/message_to_user ', '')
        message = update.message.reply_to_message.text
    text  = ("<b>🟠 یک پیام جدید دریافت کردید:</b>"
             f"\n\n{message}")
    try:
        context.bot.send_message(chat_id, text, parse_mode='html')
    except Exception as e:
        update.message.reply_text('somthing went wrong!')
        ready_report_problem_to_admin(context, 'MESSAGE TO USER', update.message.from_user['id'], e)


def change_service_server(context, update, email, country):
    try:
        get_data = sqlite_manager.select(table='Purchased', where=f'client_email = "{email}"')
        get_server_country = sqlite_manager.select(column='name,server_domain', table='Product',
                                                   where=f'id = {get_data[0][6]}')

        get_new_inbound = sqlite_manager.select(column='id,server_domain,name,domain', table='Product',
                                                where=f'country = "{country}"', limit=1)

        get_domain = get_server_country[0][1]
        get_new_domain = get_new_inbound[0][1]
        ret_conf = api_operation.get_client(email, get_domain)

        if not ret_conf['obj']['enable']:
            raise EOFError('service_is_depleted')

        if int(ret_conf['obj']['total']):
            upload_gb = ret_conf['obj']['up']
            download_gb = ret_conf['obj']['down']
            usage_traffic = upload_gb + download_gb
            total_traffic = ret_conf['obj']['total']
            left_traffic = total_traffic - usage_traffic
        else:
            left_traffic = 0

        data = {
            "id": int(get_data[0][7]),
            "settings": "{{\"clients\":[{{\"id\":\"{0}\",\"alterId\":0,"
                        "\"email\":\"{1}\",\"limitIp\":0,\"totalGB\":{2},\"expiryTime\":{3},"
                        "\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}}]}}".format(get_data[0][10], get_data[0][9],
                                                                                   left_traffic,
                                                                                   ret_conf['obj']['expiryTime'])
        }

        api_operation.add_client(data, get_new_domain)

        get_cong = api_operation.get_client_url(get_data[0][9], int(get_data[0][7]),
                                                domain=get_new_inbound[0][3], server_domain=get_new_domain)

        sqlite_manager.update({'Purchased': {'details': get_cong, 'product_id': get_new_inbound[0][0]}},
                              where=f'client_email = "{email}"')

        api_operation.del_client(get_data[0][7], get_data[0][10], get_domain)
        return get_new_inbound

    except Exception as e:
        ready_report_problem_to_admin(context, text='change_service_server', chat_id=update.callback_query.message.chat_id, error=e)
        raise e
