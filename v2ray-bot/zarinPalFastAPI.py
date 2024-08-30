from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
import aiohttp
from zarinPalFastAPIUtilities import (merchent_id, upgrade_service, send_clean_for_customer, sqlite_manager,
                                      report_status_to_user, report_status_to_admin, add_to_user_credit,
                                      add_credit_to_wallet, error_reasons)
app = FastAPI()
templates = Jinja2Templates(directory="templates")
# app.mount('/static', StaticFiles(directory='static'), name='static')

class SendRequest:
    @staticmethod
    async def send_request(method, url, params=None, json=None, data=None, header=None, session_header=None):
        async with aiohttp.ClientSession(headers=session_header) as session:
            async with session.request(method, url, params=params, json=json, data=data, headers=header) as response:
                return await response.json()

async def verify_payment(authority: str, amount: int):
    url = 'https://payment.zarinpal.com/pg/v4/payment/verify.json'
    json_payload = {
        'merchant_id': merchent_id,
        'amount': amount,
        'authority': authority
    }
    make_request = SendRequest()
    response = await make_request.send_request('post', url, json=json_payload)

    return response

@app.get('/recive_payment_result/')
async def recive_payment_result(Authority: str, Status: str, request: Request):

    if Status == 'OK':
        get_from_data = sqlite_manager.custom(f'SELECT amount,action,id_holder,chat_id FROM iraIranPaymentGeway WHERE authority = "{Authority}"')

        if not get_from_data:
            report_status_to_admin(f'🔴 CANNOT FIND INVOICE IN DATABASE [WEB SERVER]\nAuthority: {Authority}\nStatus: {Status}', chat_id=None)
            return templates.TemplateResponse(request=request, name='fail_pay.html',
                                              context={'error_reason': f'تراکنش مورد نظر در دیتابیس ما وجود ندارد. آیدی تراکنش {Authority}', 'error_code': 403})

        amount, payment_action, id_holder, chat_id = get_from_data[0]
        response = await verify_payment(Authority, amount)

        if response.get('data').get('code', 101) == 100:
            ref_id = response.get('data').get('ref_id')

            report_status_to_user('🟢 پرداخت شما با موفقیت تایید شد!'
                                  f'\nشماره تراکنش: {ref_id}', chat_id=chat_id)

            try:
                if payment_action == 'buy_service':
                    send_clean_for_customer(id_holder)
                    report_status_to_admin(
                        f'🟢 SEND SERVICE TO CUSTOMER SUCCESSFULL [WEB SERVER FINAL STATUS]'
                        f'\namount: {amount}\nservice or credit id: {id_holder}\nauthority: {Authority}',
                        chat_id
                    )
                elif payment_action == 'upgrade_service':
                    upgrade_service(id_holder)
                    report_status_to_admin(
                        f'🟢 UPGRADE CUSTOMER SERVICE SUCCESSFULL [WEB SERVER FINAL STATUS]'
                        f'\namount: {amount}\nservice or credit id: {id_holder}\nauthority: {Authority}',
                        chat_id
                    )
                elif payment_action == 'charge_wallet':
                    add_credit_to_wallet(credit_id=id_holder)
                    report_status_to_admin(
                        f'🟢 ADD CREDIT TO CUSTOMER WALLET SUCCESSFULL [WEB SERVER FINAL STATUS]'
                        f'\namount: {amount}\nservice or credit id: {id_holder}\nauthority: {Authority}',
                        chat_id
                    )
                return templates.TemplateResponse(request=request, name='success_pay.html', context={'ref_id': ref_id})

            except Exception as e:
                error_message = f'error: {e}'
                add_to_user_credit(chat_id, amount)
                status_message = f'🔴 SERVICE ACTION FAILED AND CREDIT ADDED TO WALLET [WEB SERVER FINAL STATUS]\nref id: {ref_id}'

                report_status_to_admin(status_message + f'\n{error_message}', chat_id)
                return templates.TemplateResponse(request=request, name='error_and_refund_credit_to_walet.html', context={'amount': amount})

        else:
            error_code = response.get('data', {}).get('code', 404)
            if error_code == 404:
                error_code = response.get('errors', {}).get('code', 404)
            reason = error_reasons.get(error_code)
            return templates.TemplateResponse(request=request, name='fail_pay.html', context={'error_reason': reason, 'error_code': error_code})

    else:
        return templates.TemplateResponse(request=request, name='fail_pay.html', context={'error_reason': 'رداخت از طرف درگاه پرداخت تایید نشده است', 'error_code': 400})

