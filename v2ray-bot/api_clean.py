import json
import requests

import utilities
from private import PORT, auth, telegram_bot_url, ADMIN_CHAT_ID, DOMAIN, protocol
from sqlite_manager import ManageDb

class XuiApiClean(ManageDb):
    def __init__(self):
        super().__init__('v2ray')
        self.connect = requests.Session()

        get_domains = self.select(column='server_domain', table='Product')
        get_domain_uniq = {dom[0] for dom in get_domains}

        for domain in get_domain_uniq:
            self.login = self.connect.post(f'{protocol}{domain}:{PORT}/login', data=auth)
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

    def make_request(self, method, url, json_data=None):
        try:
            with self.connect.request(method, url, json=json_data, timeout=5) as response:
                if response.ok:
                    connection_response = response.json()
                    print('connect Xui Api Success!')

                    if not connection_response['success']:
                        text = f'🔴 Xui Api Response Success Is False\ncode: {connection_response}\nurl: {response.url}'
                        self.send_telegram_message(text)
                        raise ConnectionError

                    return connection_response

                else:
                    text = f'🔴 Connection problem in Xui Api\ncode: {response.status_code}\nurl: {response.url}'
                    print(text)
                    self.send_telegram_message(text)
                    raise ConnectionError
        except Exception as e:
            utilities.report_problem_to_admin_witout_context('make_requests_api_section', None, e)
            raise e

    def get_all_inbounds(self):
        get_domains = self.select(column='server_domain', table='Product')
        get_domain_uniq = {dom[0] for dom in get_domains}
        all_inbound = []

        for domain in get_domain_uniq:
            get_inbounds = self.make_request('get', f'{protocol}{domain}:{PORT}/panel/api/inbounds/list')
            all_inbound.append(get_inbounds)

        return all_inbound

    def get_country_inbounds(self, domain):
        get_inbounds = self.make_request('get', f'{protocol}{domain}:{PORT}/panel/api/inbounds/list')
        return get_inbounds

    def get_all_inbounds_except(self, except_country):
        get_domains = self.select(column='server_domain,country', table='Product')
        get_domain_uniq = {dom[0] for dom in get_domains if dom[1] != except_country}
        all_inbound = []

        for domain in get_domain_uniq:
            get_inbounds = self.make_request('get', f'{protocol}{domain}:{PORT}/panel/api/inbounds/list')
            all_inbound.append(get_inbounds)

        return all_inbound

    def get_inbound(self, inbound_id, domain=None):
        main_domain = domain or DOMAIN
        get_inbound = self.make_request('get', f'{protocol}{main_domain}:{PORT}/panel/api/inbounds/get/{inbound_id}')
        return get_inbound

    def get_client(self, client_email, domain=None):
        main_domain = domain or DOMAIN
        get_client_ = self.make_request('get', f'{protocol}{main_domain}:{PORT}/panel/api/inbounds/getClientTraffics/{client_email}')
        return get_client_

    def add_inbound(self, data, domain=None):
        main_domain = domain or DOMAIN
        add_inb = self.make_request('post', f'{protocol}{main_domain}:{PORT}/panel/api/inbounds/add', data)
        return add_inb

    def add_client(self, data, domain=None):
        main_domain = domain or DOMAIN
        ad_client = self.make_request('post', f'{protocol}{main_domain}:{PORT}/panel/api/inbounds/addClient', json_data=data)
        return ad_client

    def update_inbound(self, inbound_id, data, domain=None):
        main_domain = domain or DOMAIN
        inb = self.make_request('post', f'{protocol}{main_domain}:{PORT}/panel/api/inbounds/update/{inbound_id}', json_data=data)
        return inb

    def reset_client_traffic(self, inbound_id, email, domain=None):
        main_domain = domain or DOMAIN
        inb = self.make_request('post', f'{protocol}{main_domain}:{PORT}/panel/api/inbounds/{inbound_id}/resetClientTraffic/{email}')
        return inb

    def update_client(self, uuid, data, domain=None):
        main_domain = domain or DOMAIN
        inb = self.make_request('post', f'{protocol}{main_domain}:{PORT}/panel/api/inbounds/updateClient/{uuid}', json_data=data)
        return inb

    def del_inbound(self, inbound_id, domain=None):
        main_domain = domain or DOMAIN
        inb = self.make_request('post', f'{protocol}{main_domain}:{PORT}/panel/api/inbounds/del/{inbound_id}')
        return inb

    def del_client(self, inboundid, uuid, domain=None):
        main_domain = domain or DOMAIN
        inb = self.make_request('post', f'{protocol}{main_domain}:{PORT}/panel/api/inbounds/{inboundid}/delClient/{uuid}')
        self.send_telegram_message(f'Client Deleted!\nClient Inbound_id: {inboundid}\nclient_uuid: {uuid}\ndomain: {domain}')
        return inb

    def del_depleted_clients(self, inbound_id="", domain=None):
        main_domain = domain or DOMAIN
        inb = self.make_request('post', f'{protocol}{main_domain}:{PORT}/panel/api/inbounds/delDepletedClients/{inbound_id}')
        return inb

    def create_backup(self, domain=None):
        main_domain = domain or DOMAIN
        inb = self.make_request('post', f'{protocol}{main_domain}:{PORT}/panel/api/inbounds/createbackup')
        return inb

    def get_client_url(self, client_email, inbound_id, domain=None, host="ponisha.ir", default_config_schematic=None, server_domain=None):
        if not default_config_schematic:
            default_config_schematic = "vless://{}@{}:{}?security=none&host={}&headerType=http&type={}#{} {}"
        get_in = self.get_inbound(inbound_id, server_domain)
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

    def get_ips(self, email, domain=None):
        main_domain = domain or DOMAIN
        inb = self.make_request('post', f'{protocol}{main_domain}:{PORT}/panel/api/inbounds/clientIps/{email}')
        return inb

    def delete_depleted_clients(self, inbound_id, domain=None):
        main_domain = domain or DOMAIN
        inb = self.make_request('post', f'{protocol}{main_domain}:{PORT}/panel/api/inbounds/delDepletedClients/{inbound_id}')
        return inb

    def get_onlines(self, domain=None):
        main_domain = domain or DOMAIN
        inb = self.make_request('post', f'{protocol}{main_domain}:{PORT}/panel/api/inbounds/onlines')
        return inb

# test = XuiApiClean()
# print(test.get_ips('kyhm2hhk'))
