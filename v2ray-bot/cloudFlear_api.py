import requests
from sqlite_manager import ManageDb
from private import telegram_bot_url, ADMIN_CHAT_ID

class CloudFlearApi(ManageDb):
    def __init__(self, api_key, email, zone_id):
        super().__init__('v2ray')
        self.api_key = api_key
        self.email = email
        self.zone_id = zone_id

        self.headers = {
            'X-Auth-Email': email,
            'X-Auth-Key': api_key,
            'Content-Type': 'application/json'
        }

        self.connect = requests.Session()

    def make_request(self, method, url, json_data=None):
        response = self.connect.request(method, url, headers=self.headers, json=json_data, timeout=5)
        response_json = response.json()

        if not response_json['success']:
            text = f'🔴 connection problem in cloudflear\ncode: {response.status_code}\nurl: {response.url}'
            requests.post(telegram_bot_url, data={'chat_id': ADMIN_CHAT_ID, "text": text})
            print(f'Connection to CloudFlear Failed. json:\n{response_json}')
            return False

        print('connect cloouflear Successful!')
        return response_json

    def add_dns_record(self, record_ip, record_name, proxied, record_type, comment, ttl=1, zone_id=None):
        zone_id = zone_id or self.zone_id

        data = {
            "content": record_ip,
            "name": record_name,
            "proxied": proxied,
            "type": record_type,
            "comment": comment,
            "ttl": ttl
        }

        return self.make_request('post', f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records', json_data=data)

    def get_dns_record_list(self, zone_id=None):
        zone_id = zone_id or self.zone_id

        return self.make_request('get', f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records')

    def change_dns_record_stting(self, domain_name=None, record_ip=None, record_name=None, proxied=None, record_type=None, comment=None, ttl=1, zone_id=None):
        zone_id = zone_id or self.zone_id

        get_dns_id = self.get_dns_record_list(zone_id)
        dns_record_id = [dns_id for dns_id in get_dns_id['result'] if dns_id['name'] == domain_name][0]

        data = {
            "content": record_ip,
            "name": record_name,
            "proxied": proxied,
            "type": record_type,
            "comment": comment,
            "ttl": ttl
        }

        return self.make_request('post', f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records', json_data=data)



