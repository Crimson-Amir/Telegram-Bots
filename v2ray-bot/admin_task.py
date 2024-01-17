from datetime import datetime, timedelta
import pytz
from sqlite_manager import ManageDb
from api_clean import XuiApiClean

sqlite_manager = ManageDb('v2ray')
api_operation = XuiApiClean()


def admin_add_update_inbound(update, context):
    """
    {'update': 3,
    'total_traffic': 0,
    'streamSettings': '' ,
    'enable': True,
    'remark': 'First_Inbound',
    'listen_ip': '',
    'port': 21442,
    'protocol': 'vless'}
    """
    try:
        user_message = eval(update.message.reply_to_message.text)

        total_to_gb = user_message['total_traffic'] * (1024 ** 3)
        stream_settings = user_message['streamSettings']
        if not stream_settings:
            stream_settings = ("{\"network\": \"tcp\",\"security\": \"none\", \"externalProxy\": [],\"tcpSettings\":"
                               "{\"acceptProxyProtocol\": false,\"header\": {\"type\": \"http\",\"request\": {\"method\": \"GET\","
                               "\"path\": [\"/\"],\"headers\": {}},\"response\": {\"version\": \"1.1\",\"status\": \"200\","
                               "\"reason\": \"OK\",\"headers\": {}}}}}")

        add_inbound_data = {
            "enable": user_message['enable'],
            "remark": user_message['remark'],
            "total": total_to_gb,
            "listen": user_message['listen_ip'],
            "port": user_message['port'],
            "protocol": user_message['protocol'],
            "expiryTime": 0,
            "settings": "{\"clients\":[],\"decryption\":\"none\",\"fallbacks\":[]}",
            "streamSettings": stream_settings,
            "sniffing": "{\"enabled\":true,\"destOverride\":[\"http\",\"tls\",\"quic\",\"fakedns\"]}"
        }
        if user_message["update"]:
            api_operation.update_inbound(user_message["update"], add_inbound_data)
        else:
            api_operation.add_inbound(add_inbound_data)
        update.message.reply_text("Done!")
    except Exception as e:
        update.message.reply_text(e)


def add_service(update, context):
    """
    {
    'update': 0,
    'inbound_id': 1,
    'active': 1,
    'name': 'Netherlands Server 🇳🇱',
    'country': 'Netherlands',
    'period': 30,
    'traffic': 10,
    'price': 10000,
    'domain': 'admin.ggkala.shop'
    }
    """
    if update.message.reply_to_message:
        try:
            user_message = eval(update.message.reply_to_message.text)
            get_data = {'inbound_id': user_message["inbound_id"],'active': user_message["active"],
                        'name': user_message["name"],'country': user_message["country"],
                        'period': user_message["period"],'traffic': user_message["traffic"],
                        'price': user_message["price"],'date': datetime.now(pytz.timezone('Asia/Tehran')), 'domain': user_message['domain']}
            if user_message['update']:
                sqlite_manager.update({'Product': get_data}, where=f'id = {user_message["update"]}')
            else:
                sqlite_manager.insert('Product', [get_data])
            update.message.reply_text('OK')
        except Exception as e:
            print(e)
            update.message.reply_text(e)


def get_all_service():
    all_serv = sqlite_manager.select(table='Product')
    indexed_data = []
    clean_data = [
        'id',
        'inbound_id',
        'active',
        'name',
        'country',
        'period',
        'traffic',
        'price',
        'date',
        'is_personalization',
        'domain'
    ]
    for ser in all_serv:
        indexed_data += [f"{clean_data[index]}: {data}" for index, data in enumerate(ser)]
        indexed_data.append(" -------------------------------------- ")
    return "\n".join(indexed_data)


def all_service(update, context):
    try:
        get = get_all_service()
        update.message.reply_text('All Service:\n\n' + str(get))
    except Exception as e:
        update.message.reply_text(e)


def del_service(update, context):
    if context.args:
        try:
            sqlite_manager.delete({"Product": [context.args[0], eval(context.args[1])]})
            update.message.reply_text("OK")
        except Exception as e:
            update.message.reply_text("Error", e)


def traffic_to_gb(traffic, byte_to_gb:bool = True):
    if byte_to_gb:
        return traffic / (1024 ** 3)
    else:
        return traffic * (1024 ** 3)


def second_to_ms(date, time_to_ms: bool = True):
    if time_to_ms:
        return int(date.timestamp() * 1000)
    else:
        seconds = date / 1000
        return datetime.fromtimestamp(seconds)


def add_client_bot(purchased_id, personalization=None):
    try:
        get_client_db = sqlite_manager.select(table='Purchased', where=f'id = {purchased_id}')
        get_service_db = sqlite_manager.select(table='Product', where=f'id = {get_client_db[0][6]}')
        traffic_to_gb_ = traffic_to_gb(get_service_db[0][6], False)
        now = datetime.now(pytz.timezone('Asia/Tehran'))
        period = get_service_db[0][5]
        now_data_add_day = now + timedelta(days=period)
        time_to_ms = second_to_ms(now_data_add_day)
        id_ = f"{get_client_db[0][4]}_{purchased_id}"
        email_ = f"{purchased_id}_{get_service_db[0][6]}GB"
        data = {
            "id": int(get_service_db[0][1]),
            "settings": "{{\"clients\":[{{\"id\":\"{0}\",\"alterId\":0,\"start_after_first_use\":true,"
                        "\"email\":\"{1}\",\"limitIp\":0,\"totalGB\":{2},\"expiryTime\":{3},"
                        "\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}}]}}".format(id_, email_, traffic_to_gb_, time_to_ms)
        }
        create = api_operation.add_client(data)
        get_cong = api_operation.get_client_url(email_, int(get_service_db[0][1]), domain=get_service_db[0][10])
        sqlite_manager.update({'Purchased': {'inbound_id': int(get_service_db[0][1]),'client_email': email_,
                                             'client_id': id_, 'date': datetime.now(pytz.timezone('Asia/Tehran')),
                                             'details': get_cong, 'active': 1, 'status': 1}},
                              where=f'id = {purchased_id}')
        print(create)
        if create['success']:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

def run_in_system(update, context):
    try:
        user_message = eval(update.message.reply_to_message.text)
        text = f'ok {user_message}'
    except Exception as e:
        text = f'There Is Problem\n{e}'
    update.message.reply_text(text=text)


# a = api_operation.get_client_url('1_Expiration:2024_06_06__12:38:17', 1)
# print(a)