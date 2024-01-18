import json

import requests
from private import PORT, auth, telegram_bot_token, ADMIN_CHAT_ID, DOMAIN, protocol

telegram_bot_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"


class XuiApiClean:
    def __init__(self):
        self.connect = requests.Session()
        get_cookies = ""

        if get_cookies == "":
            self.login = self.connect.post(f'{protocol}{DOMAIN}:{PORT}/login', data=auth)
            get_cookies = self.login.cookies.get('session')
            self.headers = {'Cookie': f'session={get_cookies}'}
            if self.login.status_code == 200:
                print(self.login.json())
            else:
                print(f'Connection Problem. {self.login.status_code}')

    @staticmethod
    def send_telegram_message(message):
        requests.post(
            telegram_bot_url,
            data={'chat_id': ADMIN_CHAT_ID, "text": message})

    def check_request(self, request):
        if request.status_code == 200:
            print('connect Successful!')
            return True
        else:
            try:
                json_if_available = request.json()
            except Exception as e:
                json_if_available = e
            text = f'connection problem!\ncode: {request.status_code}\nurl: {request.url}\njson: {json_if_available}'
            print(text)
            self.send_telegram_message(text)
            return False

    def check_json(self, request):
        try:
            test_ = request.json()
            print('connect Successful!')
            return True
        except Exception as e:
            text = f'connection problem\ncode: {request.status_code}\nurl: {request.url}'
            print(text, e)
            self.send_telegram_message(text)
            return False

    def get_all_inbounds(self):
        get_inbounds = self.connect.get(f'{protocol}{DOMAIN}:{PORT}/panel/api/inbounds/list')
        if self.check_request(get_inbounds):
            return get_inbounds.json()

    def get_inbound(self, inbound_id):
        get_inbound = self.connect.get(f'{protocol}{DOMAIN}:{PORT}/panel/api/inbounds/get/{inbound_id}')
        if self.check_request(get_inbound):
            return get_inbound.json()

    def get_client(self, client_email):
        get_client_ = self.connect.get(f'{protocol}{DOMAIN}:{PORT}/panel/api/inbounds/getClientTraffics/{client_email}')
        if self.check_request(get_client_):
            return get_client_.json()

    def add_inbound(self, data):
        add_inb = self.connect.post(f'{protocol}{DOMAIN}:{PORT}/panel/api/inbounds/add', json=data)
        if self.check_json(add_inb):
            return add_inb.json()

    def add_client(self, data):
        ad_client = self.connect.post(f'{protocol}{DOMAIN}:{PORT}/panel/api/inbounds/addClient', json=data)
        if self.check_json(ad_client):
            return ad_client.json()

    def update_inbound(self, inbound_id, data):
        inb = self.connect.post(f'{protocol}{DOMAIN}:{PORT}/panel/api/inbounds/update/{inbound_id}', json=data)
        if self.check_json(inb):
            return inb.json()

    def update_client(self, uuid, data):
        inb = self.connect.post(f'{protocol}{DOMAIN}:{PORT}/panel/api/inbounds/updateClient/{uuid}', json=data)
        if self.check_json(inb):
            return inb.json()

    def del_inbound(self, inbound_id):
        inb = self.connect.post(f'{protocol}{DOMAIN}:{PORT}/panel/api/inbounds/del/{inbound_id}')
        if self.check_json(inb):
            return inb.json()

    def del_client(self, inboundid, uuid):
        inb = self.connect.post(f'{protocol}{DOMAIN}:{PORT}/panel/api/inbounds/{inboundid}/delClient/{uuid}')
        if self.check_json(inb):
            return inb.json()

    def del_depleted_clients(self, inbound_id=""):
        inb = self.connect.post(f'{protocol}{DOMAIN}:{PORT}/panel/api/inbounds/delDepletedClients/{inbound_id}')
        if self.check_json(inb):
            return inb.json()

    def create_backup(self):
        inb = self.connect.post(f'{protocol}{DOMAIN}:{PORT}/panel/api/inbounds/createbackup')
        if self.check_json(inb):
            return inb.json()

    def get_client_url(self, client_email, inbound_id, domain=None, host="ponisha.ir", default_config_schematic=None):
        if not default_config_schematic:
            default_config_schematic = "vless://{}@{}:{}?security=none&host={}&headerType=http&type={}#{} {}"
        get_in = self.get_inbound(inbound_id)
        domain = domain or 'human.ggkala.shop'
        if get_in['success']:
            port = get_in['obj']['port']
            remark = get_in['obj']['remark']
            client_list = json.loads(get_in['obj']['settings'])['clients']
            network = json.loads(get_in['obj']['streamSettings'])['network']
            for client in client_list:
                if client['email'] == client_email:
                    return default_config_schematic.format(client['id'], domain, port, host, network,remark, client['email'])

            return False
        else:
            return False

    def get_ips(self, email):
        inb = self.connect.post(f'{protocol}{DOMAIN}:{PORT}/panel/api/inbounds/clientIps/{email}')
        if self.check_json(inb):
            return inb.json()


# test = XuiApiClean()
# print(test.get_ips('kyhm2hhk'))