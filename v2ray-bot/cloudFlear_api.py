import json

import requests
from private import PORT, auth, telegram_bot_token, ADMIN_CHAT_ID, DOMAIN, protocol
from sqlite_manager import ManageDb


class CloudFlearApi(ManageDb):
    def __init__(self, api_key, email, zoneid):
        super().__init__('v2ray')