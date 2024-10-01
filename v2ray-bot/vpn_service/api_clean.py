import json, requests, os, sys
from private import ADMIN_CHAT_IDs, telegram_bot_token
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database_sqlalchemy import SessionLocal
import models_sqlalchemy as model

PORT = 2053
auth = ''
telegram_bot_url =  ''
DOMAIN = 'f'
protocol = 'http://'

def report_problem_to_admin_witout_context(text, chat_id, error, detail=None):
    text = ("🔴 Report Problem in Bot\n\n"
            f"Something Went Wrong In {text} Section."
            f"\nUser ID: {chat_id}"
            f"\nError Type: {type(error).__name__}"
            f"\nError Reason:\n{error}")

    text += f"\nDetail:\n {detail}" if detail else ''
    telegram_bot_url_ = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    requests.post(telegram_bot_url_, data={'chat_id': ADMIN_CHAT_IDs[0], 'text': text})
    print(f'* REPORT TO ADMIN SUCCESS: ERR: {error}')

class XuiApiClean:
    coockie_list = {}

    def __init__(self):
        self.connect = requests.Session()
        self.refresh_connecion()

    def refresh_connecion(self):
        with SessionLocal() as session:
            servers = session.query(model.Server).where(model.Server.active == True)

            for server in servers:
                login = self.connect.post(f'{protocol}{server.server_ip}:{server.server_port}/login', data={'username': server.server_user_name, 'password': server.server_password})
                response = login.json()
                if not response.get('success', False):
                    raise ConnectionError(response.get('msg'))
                self.coockie_list[server.server_ip] = login.cookies
                if login.status_code != 200: print(f'Connection Problem. {login.status_code}')

    @staticmethod
    def send_telegram_message(message):
        requests.post(
            telegram_bot_url,
            data={'chat_id': ADMIN_CHAT_IDs[0], "text": message})

    def make_request(self, method, url, json_data=None, domain=DOMAIN):
        try:

            cookie = self.coockie_list[domain]
            print(cookie)

            with self.connect.request(method, url, json=json_data, cookies=cookie, timeout=5) as response:
                if response.ok:
                    connection_response = response.json()

                    if not connection_response.get('success', False):
                        text = f'🔴 Xui Api Response Success Is False\ncode: {connection_response}\nurl: {response.url}'
                        self.send_telegram_message(text)
                        raise ConnectionError(text)

                    return connection_response

                else:
                    text = f'🔴 Connection problem in Xui Api\ncode: {response.status_code}\nurl: {response.url}'
                    print(text)
                    self.send_telegram_message(text)
                    raise ConnectionError(text)
        except Exception as e:
            report_problem_to_admin_witout_context('make_requests_api_section', None, e)
            raise e

    def get_all_inbounds(self):
        with SessionLocal() as session:
            servers = session.query(model.Server).where(model.Server.active == True)
            all_inbound = []

            for server in servers:
                get_inbounds = self.make_request('get', f'{protocol}{server.server_ip}:{server.server_port}/panel/api/inbounds/list', domain=server.server_ip)
                all_inbound.append(get_inbounds)

            return all_inbound

    def get_country_inbounds(self, domain=DOMAIN):
        get_inbounds = self.make_request('get', f'{protocol}{domain}:{PORT}/panel/api/inbounds/list')
        return get_inbounds

    def get_inbound(self, inbound_id, domain=DOMAIN):
        get_inbound = self.make_request('get', f'{protocol}{domain}:{PORT}/panel/api/inbounds/get/{inbound_id}', domain=domain)
        return get_inbound

    def get_client(self, client_email, domain=DOMAIN):
        get_client_ = self.make_request('get', f'{protocol}{domain}:{PORT}/panel/api/inbounds/getClientTraffics/{client_email}', domain=domain)
        return get_client_

    def add_inbound(self, data, domain=DOMAIN):
        add_inb = self.make_request('post', f'{protocol}{domain}:{PORT}/panel/api/inbounds/add', data, domain=domain)
        return add_inb

    def add_client(self, data, domain=DOMAIN):
        ad_client = self.make_request('post', f'{protocol}{domain}:{PORT}/panel/api/inbounds/addClient', json_data=data, domain=domain)
        return ad_client

    def update_inbound(self, inbound_id, data, domain=DOMAIN):
        inb = self.make_request('post', f'{protocol}{domain}:{PORT}/panel/api/inbounds/update/{inbound_id}', json_data=data, domain=domain)
        return inb

    def reset_client_traffic(self, inbound_id, email, domain=DOMAIN):
        inb = self.make_request('post', f'{protocol}{domain}:{PORT}/panel/api/inbounds/{inbound_id}/resetClientTraffic/{email}', domain=domain)
        return inb

    def update_client(self, uuid, data, domain=DOMAIN):
        inb = self.make_request('post', f'{protocol}{domain}:{PORT}/panel/api/inbounds/updateClient/{uuid}', json_data=data, domain=domain)
        return inb

    def del_inbound(self, inbound_id, domain=DOMAIN):
        inb = self.make_request('post', f'{protocol}{domain}:{PORT}/panel/api/inbounds/del/{inbound_id}', domain=domain)
        return inb

    def del_client(self, inboundid, uuid, domain=DOMAIN):
        inb = self.make_request('post', f'{protocol}{domain}:{PORT}/panel/api/inbounds/{inboundid}/delClient/{uuid}', domain=domain)
        self.send_telegram_message(f'Client Deleted!\nClient Inbound_id: {inboundid}\nclient_uuid: {uuid}\ndomain: {domain}')
        return inb

    def del_depleted_clients(self, inbound_id="", domain=DOMAIN):
        inb = self.make_request('post', f'{protocol}{domain}:{PORT}/panel/api/inbounds/delDepletedClients/{inbound_id}', domain=domain)
        return inb

    def create_backup(self, domain=DOMAIN):
        inb = self.make_request('post', f'{protocol}{domain}:{PORT}/panel/api/inbounds/createbackup', domain=domain)
        return inb

    def get_client_url(self, client_email, inbound_id, domain, header_type="http", host="ponisha.ir", default_config_schematic=None, server_domain=None, remark=None):
        if not default_config_schematic:
            default_config_schematic = "vless://{}@{}:{}?security=none&host={}&headerType={}&type={}#{}"
        get_in = self.get_inbound(inbound_id, server_domain)
        if get_in['success']:
            port = get_in['obj']['port']
            remark = remark or get_in['obj']['remark']
            client_list = json.loads(get_in['obj']['settings'])['clients']
            network = json.loads(get_in['obj']['streamSettings'])['network']
            for client in client_list:
                if client['email'] == client_email:
                    final_shematic = default_config_schematic.format(client['id'], domain, port, host, header_type, network, remark)
                    print(final_shematic)
                    return final_shematic

            return False
        else:
            return False

    def get_ips(self, email, domain=DOMAIN):
        inb = self.make_request('post', f'{protocol}{domain}:{PORT}/panel/api/inbounds/clientIps/{email}', domain=domain)
        return inb

    def delete_depleted_clients(self, inbound_id, domain=DOMAIN):
        inb = self.make_request('post', f'{protocol}{domain}:{PORT}/panel/api/inbounds/delDepletedClients/{inbound_id}', domain=domain)
        return inb

    def get_onlines(self, domain=DOMAIN):
        inb = self.make_request('post', f'{protocol}{domain}:{PORT}/panel/api/inbounds/onlines', domain=domain)
        return inb

    def restart_xray(self, domain=DOMAIN):
        inb = self.make_request('post', f'{protocol}{domain}:{PORT}/server/restartXrayService', domain=domain)
        return inb


# test = XuiApiClean()
# a = test.get_all_inbounds()
# print(a)