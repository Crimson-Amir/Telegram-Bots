import datetime
import arrow
import pytz
from private import *
import requests
from ranking import rank_emojis, rank_title_fa, rank_access_fa, rank_access
from sqlite_manager import ManageDb
from api_clean import XuiApiClean

api_operation = XuiApiClean()
sqlite_manager = ManageDb('v2ray')
infinity_name = '_Infinite_Service'


def human_readable(number):
    get_date = arrow.get(number)
    try:
        return get_date.humanize(locale="fa-ir")

    except ValueError as e:
        if 'week' in str(e):
            return str(get_date.humanize()).replace('weeks ago', 'هفته پیش').replace('a week ago', 'هفته پیش')
        else:
            return get_date.humanize()

    except Exception as e:
        print(e)
        return f'Error In Parse Data'


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
    text= "مشکلی وجود داشت!"
    if getattr(update, 'callback_query'):
        query = update.callback_query
        query.answer(text)
    else:
        update.message.reply_text(text)


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


def format_mb_traffic(traffic):
    if traffic == 0:
        return 'بدون مصرف'
    elif int(traffic) < 1000:
        return f"{int(traffic)} مگابایت"
    else:
        return f"{round(traffic / 1000, 2)} گیگابایت"


def make_day_name_farsi(text):
    days_mapping = {
        'Monday': 'دوشنبه',
        'Tuesday': 'سه‌شنبه',
        'Wednesday': 'چهارشنبه',
        'Thursday': 'پنج‌شنبه',
        'Friday': 'جمعه',
        'Saturday': 'شنبه',
        'Sunday': 'یک‌شنبه'
    }

    return days_mapping[text]


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


def report_problem(func_name, error, side):
    text = (f"🔴 BOT Report Problem [{side}]\n\n"
            f"\nFunc Name: {func_name}"
            f"\nError Type: {type(error).__name__}"
            f"\nError Reason:\n{error}")

    requests.post(telegram_bot_url, data={'chat_id': ADMIN_CHAT_ID, 'text': text})


def report_problem_by_user_utilitis(context, problem, user):
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
        if update:
            update.message.reply_text('somthing went wrong!')
            ready_report_problem_to_admin(context, 'MESSAGE TO USER', update.message.from_user['id'], e)
        else:
            ready_report_problem_to_admin(context, 'MESSAGE TO USER', chat_id, e)


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
        shematic = None

        if get_data[0][7] == TLS_INBOUND:
            shematic = ('vless://{}@{}:{}'
                        '?path=%2F&host={}&headerType=http&security=tls&'
                        'fp=&alpn=h2%2Chttp%2F1.1&sni=sni_&type={}#{} {}'.replace('sni_', get_new_domain))

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
                                                domain=get_new_inbound[0][3], server_domain=get_new_domain,
                                                host=get_new_domain,
                                                default_config_schematic=shematic
                                                )

        sqlite_manager.update({'Purchased': {'details': get_cong, 'product_id': get_new_inbound[0][0]}},
                              where=f'client_email = "{email}"')

        api_operation.del_client(get_data[0][7], get_data[0][10], get_domain)
        return get_new_inbound

    except Exception as e:
        if update:
            chat_id = update.callback_query.message.chat_id
        else:
            chat_id = 1
        report_problem_to_admin_witout_context(text='change_service_server', chat_id=chat_id, error=e)
        raise e



def convert_service_to_tls(update, email, convert_to):
    try:
        get_data = sqlite_manager.select(table='Purchased', where=f'client_email = "{email}"')
        get_server_country = sqlite_manager.select(column='name,server_domain,domain,inbound_id', table='Product',
                                                   where=f'id = {get_data[0][6]}')

        get_domain = get_server_country[0][1]
        ret_conf = api_operation.get_client(email, get_domain)

        if eval(convert_to):
            shematic = ('vless://{}@{}:{}'
                        '?path=%2F&host={}&headerType=http&security=tls&'
                        'fp=&alpn=h2%2Chttp%2F1.1&sni=sni_&type={}#{} {}'.replace('sni_', get_domain))
            detected_inbound = TLS_INBOUND
        else:
            shematic = None
            detected_inbound = get_server_country[0][3]

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
            "id": detected_inbound,
            "settings": "{{\"clients\":[{{\"id\":\"{0}\",\"alterId\":0,"
                        "\"email\":\"{1}\",\"limitIp\":0,\"totalGB\":{2},\"expiryTime\":{3},"
                        "\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}}]}}".format(get_data[0][10], get_data[0][9],
                                                                                   left_traffic,
                                                                                   ret_conf['obj']['expiryTime'])}

        api_operation.del_client(get_data[0][7], get_data[0][10], get_domain)

        api_operation.add_client(data, get_domain)

        get_cong = api_operation.get_client_url(get_data[0][9], detected_inbound,
                                                domain=get_server_country[0][2], server_domain=get_domain, host=get_domain,
                                                default_config_schematic=shematic)

        sqlite_manager.update({'Purchased': {'inbound_id': detected_inbound, 'details': get_cong}},
                              where=f'client_email = "{email}"')

        return get_server_country

    except Exception as e:
        if update:
            chat_id = update.callback_query.message.chat_id
        else:
            chat_id = 1
        report_problem_to_admin_witout_context(text='change_service_server', chat_id=chat_id, error=e)
        raise e


def moving_all_service_to_server_with_database_change(server_country):
    get_all = api_operation.get_all_inbounds_except(server_country)

    for server in get_all:
        for config in server['obj']:
            for client in config['clientStats']:
                if client['enable']:
                    change_service_server(None, None, client['email'], server_country)


