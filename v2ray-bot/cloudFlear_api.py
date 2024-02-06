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


    def make_request(self, method, url, json_data):
        response = self.connect.request(method, url, json=json_data, timeout=5)
        try:
            response.json()
            print('connect cloouflear Successful!')
            return True
        except Exception as e:
            text = f'🔴 connection problem\ncode: {response.status_code}\nurl: {response.url}'
            print(text, e)
            requests.post(
                telegram_bot_url,
                data={'chat_id': ADMIN_CHAT_ID, "text": message})
            return False

    def change_dns_record_ip(self, record_ip, record_name, proxied, record_type, comment, ttl='Auto', zone_id=None):
        zone_id = zone_id or self.zone_id

        data = {
            "content": record_ip,
            "name": record_name,
            "proxied": proxied,
            "type": record_type,
            "comment": comment,
            "ttl": ttl
        }

        req = requests.post(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records',
                            headers=self.headers, json=data).json()


a = CloudFlearApi('e609eff4c987a0557cfe43d4956e99ea24170', 'ytchanneltinos@gmail.com', 'e764ba1c8fc10092843c59ab4bd4fdec')
a.change_dns_record_ip("178.128.196.7", "soka", False, "A", 'OK')