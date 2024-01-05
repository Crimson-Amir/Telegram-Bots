import datetime
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
    'inbound_id': 1,
    'active': 1,
    'name': 'Netherlands Server 🇳🇱',
    'country': 'Netherlands',
    'period': 30,
    'traffic': 10,
    }
    """
    try:
        user_message = eval(update.message.reply_to_message.text)
        sqlite_manager.insert('Product', [{'inbound_id': user_message["inbound_id"],'active': user_message["active"],
                                           'name': user_message["name"],'country': user_message["country"],
                                           'period': user_message["period"],'traffic': user_message["traffic"],
                                           'date': datetime.datetime.now(pytz.timezone('Asia/Tehran'))}])
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
        'date',
    ]
    for ser in all_serv:
        indexed_data += [f"{clean_data[index]}: {data}" for index, data in enumerate(ser)]
        indexed_data.append(" -------------------------------------- ")
    return "\n".join(indexed_data)


def all_service(update, context):
    try:
        get = get_all_service()
        update.message.reply_text("Like This: \n", get)
    except Exception as e:
        update.message.reply_text(e)


def del_service(update, context):
    try:
        if context.args:
            print(context.args)
            sqlite_manager.delete({"Product": [context.args[0], eval(context.args[1])]})
            update.message.reply_text("OK")
    except Exception as e:
        update.message.reply_text(e)