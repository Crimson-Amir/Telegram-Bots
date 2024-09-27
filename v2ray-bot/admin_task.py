import random
from datetime import datetime, timedelta
import pytz
import utilities
from private import ADMIN_CHAT_ID, OTHER_ADMIN
from utilities import (init_name, ready_report_problem_to_admin, message_to_user, sqlite_manager, api_operation,
                       infinity_name, report_status_to_admin, second_to_ms, traffic_to_gb, ranking_manage, wallet_manage)
from ranking import rank_access, rank_access_fa
from ticket import TicketManager

ticket_manager = TicketManager('v2ray')

def add_service(update, context):
    chat_id = update.message.chat_id
    if chat_id not in OTHER_ADMIN: return
    """
    {
    'update': 0,
    'inbound_id': 1,
    'active': 1,
    'name': 'Netherlands Server 🇳🇱',
    'country': 'Netherlands',
    'period': 30,
    'traffic': 10,
    'domain': 'admin.ggkala.shop',
    'server_domain': 'netherlands.ggkala.shop',
    'inbound_header_type': 'http',
    'inbound_host': 'ponisha.ir'
    }
    """
    if update.message.reply_to_message:
        try:
            user_message = eval(update.message.reply_to_message.text)
            price = (int(user_message["traffic"]) * utilities.PRICE_PER_GB) + (int(user_message["period"]) * utilities.PRICE_PER_DAY)
            get_data = {'inbound_id': user_message["inbound_id"],'active': user_message["active"],
                        'name': init_name(user_message["name"]),'country': user_message["country"],
                        'period': user_message["period"],'traffic': user_message["traffic"],
                        'price': price, 'date': datetime.now(pytz.timezone('Asia/Tehran')),
                        'domain': user_message['domain'], 'server_domain': user_message['server_domain'],
                        'inbound_header_type': user_message['inbound_header_type'], 'inbound_host': user_message['inbound_host']
                        }
            if user_message['update']:
                sqlite_manager.update({'Product': get_data}, where=f'id = {user_message["update"]}')
            else:
                sqlite_manager.insert('Product', get_data)
            update.message.reply_text('OK')
        except Exception as e:
            print(e)
            update.message.reply_text(e)

def del_service(update, context):
    chat_id = update.message.chat_id
    if chat_id not in OTHER_ADMIN: return
    if context.args:
        try:
            sqlite_manager.delete({"Product": [context.args[0], eval(context.args[1])]})
            update.message.reply_text("OK")
        except Exception as e:
            update.message.reply_text("Error", e)


def add_client_bot(purchased_id):

    try:
        random_number = random.randint(0, 10_000_000)
        get_client_db = sqlite_manager.select(table='Purchased', where=f'id = {purchased_id}')
        get_service_db = sqlite_manager.select(column='inbound_id,name,period,traffic,domain,server_domain,inbound_host,inbound_header_type', table='Product', where=f'id = {get_client_db[0][6]}')

        inbound_host = get_service_db[0][6]
        inbound_header_type = get_service_db[0][7]

        id_ = f"{get_client_db[0][4]}_{random_number}"
        name = '_Gift' if 'gift' in get_service_db[0][1] else ''  # f'{get_service_db[0][6]}GB'
        email_ = f"{purchased_id}{name}"

        if get_service_db[0][3]:
            traffic_to_gb_ = traffic_to_gb(get_service_db[0][3], False)
        else:
            email_ = f"{purchased_id}{infinity_name}"
            traffic_to_gb_ = 0

        if get_service_db[0][2]:
            now = datetime.now(pytz.timezone('Asia/Tehran'))
            period = get_service_db[0][2]
            now_data_add_day = now + timedelta(days=period)
            time_to_ms = second_to_ms(now_data_add_day)
        else:
            time_to_ms = 0

        data = {
            "id": int(get_service_db[0][0]),
            "settings": "{{\"clients\":[{{\"id\":\"{0}\",\"alterId\":0,\"start_after_first_use\":true,"
                        "\"email\":\"{1}\",\"limitIp\":0,\"totalGB\":{2},\"expiryTime\":{3},"
                        "\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}}]}}".format(id_, email_, traffic_to_gb_, time_to_ms)
        }

        create = api_operation.add_client(data, get_service_db[0][5])

        check_servise_available = api_operation.get_client(email_, domain=get_service_db[0][5])
        if not check_servise_available['obj']: return False, create, 'service do not create'

        get_cong = api_operation.get_client_url(email_, int(get_service_db[0][0]),
                                                domain=get_service_db[0][4], server_domain=get_service_db[0][5],
                                                host=inbound_host, header_type=inbound_header_type)

        sqlite_manager.update({'Purchased': {'inbound_id': int(get_service_db[0][0]),'client_email': email_,
                                             'client_id': id_, 'date': datetime.now(pytz.timezone('Asia/Tehran')),
                                             'details': get_cong, 'active': 1, 'status': 1}}, where=f'id = {purchased_id}')

        if create['success']:
            return True, create, 'service create success'
        else:
            return False, create, 'create service is failed'

    except Exception as e:
        utilities.report_problem_to_admin_witout_context('ADD CLIENT BOT [ADMIN TASK]', chat_id=None, error=e)
        return False, None, f'Error: {e}'


def run_in_system(update, context):
    chat_id = update.message.chat_id
    if chat_id not in OTHER_ADMIN: return
    try:
        user_message = eval(update.message.reply_to_message.text)
        text = f'ok {user_message}'
    except Exception as e:
        text = f'There Is Problem\n{e}'
    update.message.reply_text(text=text)


def say_to_every_one(update, context):
    chat_id = update.message.chat_id
    if chat_id not in OTHER_ADMIN: return
    all_user = sqlite_manager.select('chat_id,name', 'User')
    text = update.message.reply_to_message.text

    for user in all_user:
        try:
            context.bot.send_message(chat_id=user[0], text=text, parse_mode='html')
        except Exception as e:
            context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f'BLOCKED BY USER {user[1]} | {user[0]}', parse_mode='html')
            print(e)


def clear_depleted_service(update, context):
    chat_id = update.message.chat_id
    if chat_id not in OTHER_ADMIN: return
    try:
        get_inbound_id = int(update.message.text.replace('/clear_depleted_service ', ''))

        customer_service = sqlite_manager.select(column='chat_id,name,client_email,inbound_id', table='Purchased', where=f'status = 0 and inbound_id = {get_inbound_id}')
        sqlite_manager.select(column='server_domain', table='Product',
                              where=f'id = "{customer_service[0][3]}"')

        reason = update.message.reply_to_message.text if update.message.reply_to_message else 'عدم تمدید و یا ارتقا سرویس'
        text = 'سرویس شما با نام {} که قبلا منقضی شده بود، حذف شد!\nعلت: '

        for service in customer_service:
            message_to_user(update, context, message=f"{text.format(service[2])}{reason}", chat_id=service[0])

        api_operation.delete_depleted_clients(get_inbound_id)
        sqlite_manager.advanced_delete({'Purchased': [['status', 0], ['inbound_id', get_inbound_id]]})
        update.message.reply_text('Clear Depleted Service Successfull')

    except Exception as e:
        ready_report_problem_to_admin(context, 'Clear Depleted Service', update.message.from_user['id'], e)

def add_credit_to_customer(update, context):
    chat_id = update.message.chat_id
    if chat_id not in OTHER_ADMIN: return
    try:
        get_admin_order = update.message.text.replace('/add_credit_to_customer ', '').split(', ')
        get_user_chat_id = get_admin_order[0]
        get_credit = int(get_admin_order[1])

        reason = update.message.reply_to_message.text if update.message.reply_to_message else 'برای قطعی اخیر سرور متاسفیم، مبلغ خسارت محاسبه و جبران خسارت انجام شد.'
        text = f'<b>مبلغ {get_credit:,} تومان به کیف پول شما اضافه شد.</b>' + f'\n\n{reason}'

        customer_of_service = sqlite_manager.select(column='name,user_name', table='User',
                                                    where=f'chat_id = {get_user_chat_id}')

        wallet_manage.add_to_wallet(get_user_chat_id, get_credit)

        message_to_user(update, context, message=text, chat_id=get_user_chat_id)

        update.message.reply_text('Add to User Wallet Successfull')

    except Exception as e:
        ready_report_problem_to_admin(context, 'add credit to customer', update.message.from_user['id'], e)

def admin_rank_up(update, context):
    chat_id = update.message.chat_id
    if chat_id not in OTHER_ADMIN: return

    get_admin_order = update.message.text.replace('/rank_up ', '').split(', ')
    get_user_chat_id = get_admin_order[0]
    try:
        get_rank_name = get_admin_order[1]
        rank_access_ = '\n'.join(rank_access_fa[get_rank_name][1:])

        text = f'رنک شما توسط ادمین ارتقا یافت.\n\nویژگی های این رنک:\n {rank_access_}'

        sqlite_manager.select(column='name,user_name', table='User',
                              where=f'chat_id = {get_user_chat_id}')

        ranking_manage.rank_up(get_rank_name, get_user_chat_id)
        message_to_user(update, context, message=text, chat_id=get_user_chat_id)

        update.message.reply_text('RANKUP SUCCESS')

    except TypeError:
        rank_name_ = next(iter(rank_access))
        level = 0

        sqlite_manager.insert(table='Rank', rows={'name': None, 'user_name': None, 'chat_id': get_user_chat_id,
                                                  'level': level, 'rank_name': rank_name_})
        report_status_to_admin(context, 'I Create Rank For User. Try Again!', get_user_chat_id)

    except Exception as e:
        ready_report_problem_to_admin(context, 'admin_rank_up', update.message.from_user['id'], e)
