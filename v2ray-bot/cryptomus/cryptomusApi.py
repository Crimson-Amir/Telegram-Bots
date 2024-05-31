import aiohttp
import asyncio
import base64
import hashlib
import json
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class SessionError(Exception):
    def __init__(self, message):
        super().__init__(message)


class MakeRequest:
    def __init__(self, session):
        self._session = session

    async def make_request(self, url, headers=None, data=None):
        if not self._session:
            raise SessionError("session is not set!")

        async with self._session.post(url, headers=headers, json=data, ssl=False, timeout=15) as response:
            try:
                response.raise_for_status()
                return await response.json(content_type=None)

            except aiohttp.ClientResponseError as e:
                print(f"Request failed with status {e.status}: {e.message}")
                return None


class RequestFactory:
    @staticmethod
    async def run_requests(requests_list, session_header=None, headers=None, data=None, return_exceptions=True):
        if not isinstance(requests_list, list):
            requests_list = [requests_list]

        async with aiohttp.ClientSession(headers=session_header) as session:
            request_manager = MakeRequest(session)
            requests_ = [request_manager.make_request(request, headers=headers, data=data) for request in requests_list]
            results = await asyncio.gather(*requests_, return_exceptions=return_exceptions)
            return results


class Encryption:
    @staticmethod
    def md5_hash(data: bytes) -> str:
        hash_instance = hashlib.md5()
        hash_instance.update(data)
        return hash_instance.hexdigest()

    @staticmethod
    def b64encoding(data: bytes) -> str:
        return base64.b64encode(data).decode('utf-8')

    @staticmethod
    def b64decode(data: str) -> bytes:
        return base64.b64decode(data)


class Cryptomus:

    def __init__(self, api_key, merchant_id):
        self._api_key = api_key
        self._merchant_id = merchant_id
        self._request_manager = RequestFactory()
        self._encryption = Encryption()

        self.headers = {
            'merchant': self._merchant_id,
            'sign': '',
            'Content-Type': 'application/json'
        }

    def create_sign(self, data: dict):
        encode_params = ''
        if data:
            encode_params = self._encryption.b64encoding(json.dumps(data).encode('utf-8'))
        return self._encryption.md5_hash(f'{encode_params}{self._api_key}'.encode('utf-8'))


class CreateInvoice(Cryptomus):
    request_endpoint = 'https://api.cryptomus.com/v1/payment'

    async def execute(self, amount: str, currency: str, order_id: str,
                             network: str = None, url_return: str = None, url_success: str = None, url_callback: str = None,
                             is_payment_multiple: bool = True, lifetime: int = 3600, to_currency: str = None, subtract: int = 0,
                             accuracy_payment_percent: float = 0, additional_data: str = None, currencies: list = None,
                             except_currencies: list = None, course_source: str = None, from_referral_code: str = None,
                             discount_percent: int = None, is_refresh: bool = False):
        """
        :param amount: Amount to be paid. Example: 10.28
        :param currency: Currency code
        :param order_id: Order ID in your system. max: 128
        :param network: Blockchain network code
        :param url_return: Before paying, the user can click on the button on the payment form and return to the store page at this URL. max: 255
        :param url_success: After successful payment, the user can click on the button on the payment form and return to this URL. max: 255
        :param url_callback: URL to which webhooks with payment status will be sent. max: 255
        :param is_payment_multiple: Whether the user is allowed to pay the remaining amount. Useful when the user has not paid the entire amount of the invoice for one transaction.
        :param lifetime: The lifespan of the issued invoice (in seconds). min: 300 - max: 43200
        :param to_currency: The target currency for converting the invoice amount.
        :param subtract: Percentage of the payment commission charged to the client. max: 100
        :param accuracy_payment_percent: Acceptable inaccuracy in payment. max: 5
        :param additional_data: Additional information for you (not shown to the client). max: 255
        :param currencies: List of allowed currencies for payment.
        :param except_currencies: List of excluded currencies for payment.
        :param course_source: The service from which the exchange rates are taken for conversion in the invoice. min: 4 - max: 20
        :param from_referral_code: The merchant who makes the request connects to a referrer by code.
        :param discount_percent: Positive numbers: Allows you to set a discount. Negative numbers: Allows you to set custom additional commission. min: -99 - max: 100
        :param is_refresh: Update the lifetime and get a new address for the invoice if the lifetime has expired.
        :return: Invoice json data
        """

        data = {
            'amount': amount,
            'currency': currency,
            'order_id': order_id,
            'network': network,
            'url_return': url_return,
            'url_success': url_success,
            'url_callback': url_callback,
            'is_payment_multiple': is_payment_multiple,
            'lifetime': lifetime,
            'to_currency': to_currency,
            'subtract': subtract,
            'accuracy_payment_percent': accuracy_payment_percent,
            'additional_data': additional_data,
            'currencies': currencies,
            'except_currencies': except_currencies,
            'course_source': course_source,
            'from_referral_code': from_referral_code,
            'discount_percent': discount_percent,
            'is_refresh': is_refresh
        }

        self.headers['sign'] = self.create_sign(data)

        return await self._request_manager.run_requests(self.request_endpoint, session_header=self.headers, data=data)


    async def get_qrcode(self, invoice_result_json, save_img=False):
        get_qrcode_key = invoice_result_json.get('result', {}).get('address_qr_code')

        if get_qrcode_key:
            encoded_data = get_qrcode_key.split(',')[1]
            decode_data =  self._encryption.b64decode(encoded_data)
            if save_img:
                with open(str(encoded_data[:20]) + '.png', 'wb') as image:
                    image.write(decode_data)
            return decode_data


class InvoiceInfo(Cryptomus):
    request_endpoint = 'https://api.cryptomus.com/v1/payment/info'

    async def execute(self, uuid, order_id):
        """
        only need one arguman
        :param order_id: Order ID in your system. max: 128
        :param uuid: Invoice uuid
        :return: Invoice info
        """

        data = {'order_id': order_id, 'uuid': uuid}

        self.headers['sign'] = self.create_sign(data)

        return await self._request_manager.run_requests(self.request_endpoint, session_header=self.headers, data=data)


class CreateStaticWallet(Cryptomus):
    request_endpoint = 'https://api.cryptomus.com/v1/wallet'

    async def execute(self, currency: str, order_id: str, network: str = None,
                            url_callback: str = None, from_referral_code: str = None):
        """
        :param currency: Currency code
        :param order_id: Order ID in your system. max: 128
        :param network: Blockchain network code
        :param url_callback: URL to which webhooks with payment status will be sent. max: 255
        :param from_referral_code: The merchant who makes the request connects to a referrer by code.
        :return: static wallet info
        """

        data = {
            'currency': currency,
            'order_id': order_id,
            'network': network,
            'url_callback': url_callback,
            'from_referral_code': from_referral_code,
        }

        self.headers['sign'] = self.create_sign(data)

        return await self._request_manager.run_requests(self.request_endpoint, session_header=self.headers, data=data)


class Refund(Cryptomus):
    request_endpoint = 'https://api.cryptomus.com/v1/payment/refund'

    async def execute(self, address: str, is_subtract: str, uuid: str = None,
                     order_id: str = None):
        """
        :param address: The address to which the refund should be made
        :param order_id: Order ID in your system. max: 128
        :param is_subtract: Whether to take a commission from the merchant's balance or from the refund amount
        true - take the commission from merchant balance
        false - reduce the refundable amount by the commission amount
        :param uuid: Invoice uuid
        :return: status json
        """

        data = {
            'address': address,
            'order_id': order_id,
            'uuid': uuid,
            'is_subtract': is_subtract,
        }

        self.headers['sign'] = self.create_sign(data)

        return await self._request_manager.run_requests(self.request_endpoint, session_header=self.headers, data=data)


class ListOfService(Cryptomus):
    request_endpoint = 'https://api.cryptomus.com/v1/payment/services'

    async def execute(self):
        self.headers['sign'] = self.create_sign({})
        return await self._request_manager.run_requests(self.request_endpoint, session_header=self.headers)


class PaymentHistory(Cryptomus):
    request_endpoint = 'https://api.cryptomus.com/v1/payment/list'

    async def execute(self, date_from: str = None, data_to: str = None):
        """
        time format: YYYY-MM-DD H:mm:ss
        :param date_from: Filtering by creation date, from
        :param data_to: Filtering by creation date, to
        :return: payment history json
        """

        data = {
            'date_from': date_from,
            'data_to': data_to
        }

        self.headers['sign'] = self.create_sign(data)
        return await self._request_manager.run_requests(self.request_endpoint, session_header=self.headers, data=data)


def client(cryptomus_api_key, cryptomus_merchant_id, class_, **method_kwargs):
    class_instance = class_(cryptomus_api_key, cryptomus_merchant_id)
    run_method = asyncio.run(class_instance.execute(**method_kwargs))
    return run_method

# cryptomus_api_key = 'xbPjwvsT6qiypVVwYHvUsjp5giSH2WUQ75oBDuiHSM7Wi5Zu2t9h8R02R7WC1ptF6FLfeDq1gyYTcHP9Rf4N2dwNcNTWA1PlaAaY666VGxs9foah4UXuYfTLXQfsAebW'
# cryptomus_merchant_id = 'b493112a-350e-4c57-ad74-91b608a36af9'
# print(client(cryptomus_api_key, cryptomus_merchant_id, CreateInvoice, order_id='1321', currency='USD', amount='0.10'))