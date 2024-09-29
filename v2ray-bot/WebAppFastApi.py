from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import private, logging
import crud, requests, utilities_reFactore, wallet_reFactore
from database_sqlalchemy import SessionLocal
from vpn_service import buy_and_upgrade_service
from WebAppDialogue import transaction

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def refund(session, financial_db):
    crud.add_credit_to_wallet(session, financial_db, 'refund')
    session.commit()


def verify_payment(authority: str, amount: int):
    url = 'https://payment.zarinpal.com/pg/v4/payment/verify.json'
    json_payload = {
        'merchant_id': private.merchant_id,
        'amount': amount,
        'authority': authority
    }

    response = requests.post(url=url, json=json_payload)
    return response

@app.get('/iran_recive_payment_result/')
async def recive_payment_result(Authority: str, Status: str, request: Request):

    with SessionLocal() as session:
        session.begin()

        financial = crud.get_financial_report_by_authority(session, Authority)

        if Status == 'OK' and financial:
            try:
                dialogues = transaction[financial.owner.language]
                response = verify_payment(Authority, financial.amount)

                if not response.json():
                    raise ConnectionError(f'respoce does not have json!\nResponse code: {response}\nReason:\n{response}')

                response_json = response.json()

            except Exception as e:
                error = ('UnHandeled error'
                         f'\nError Type: {type(e)}'
                         f'\nAuthority: {Authority}'
                         f'\nError Reason: \n{str(e)}')

                await utilities_reFactore.report_to_admin('emergecy_error', 'ZarinPalWebApp', error, financial.owner)
                return templates.TemplateResponse(
                    request=request,
                    name='fail_pay.html',
                    context={'translation': dialogues, 'error_code': 405}
                )

            if response_json.get('data').get('code', 101) == 100:
                try:
                    ref_id = response_json.get('data').get('ref_id')
                    class Update:
                        class effective_chat: id = financial.owner.chat_id

                    context = utilities_reFactore.FakeContext()
                    update = Update()
                    message = dialogues.get('successful_pay')
                    message = message.format(ref_id)
                    await utilities_reFactore.report_to_user('success', financial.chat_id, message)

                    extra_data = ''
                    if financial.action == 'buy_vpn_service':
                        service = await buy_and_upgrade_service.create_service_for_user(update, context, session, financial.id_holder)
                        extra_data = (f'Service Traffic: {service.traffic}'
                                      f'\nService Period: {service.period}')

                    # elif financial.action == 'upgrade_service':
                    #     upgrade_service(id_holder)

                    elif financial.action == 'increase_wallet_balance':
                        await wallet_reFactore.increase_wallet_balance(update, context, session, financial.financial_id)

                    msg = (f'Action: {financial.action}'
                           f'\nAuthority: {Authority}'
                           f'\nAmount: {financial.amount}'
                           f'\nService ID: {financial.financial_id}'
                           f'\n\n{extra_data}')

                    await utilities_reFactore.report_to_admin('purchase', 'ZarinPalWebApp', msg, financial.owner)
                    session.commit()
                    return templates.TemplateResponse(request=request, name='success_pay.html', context={'ref_id': ref_id})

                except Exception as e:
                    session.rollback()
                    logging.error(f'error in zarinpal webapp payment {e}')
                    refund(session, financial)

                    error = ('Amount refunded to user wallet! Payment was not successfull! '
                             f'\nError Type: {type(e)}'
                             f'\nAuthority: {Authority}'
                             f'\nError Reason: \n{str(e)}')

                    message = dialogues.get('operation_failed_user')
                    message = message.format(f"{financial.amount:,}")

                    await utilities_reFactore.report_to_admin('error', 'ZarinPalWebApp', error, financial.owner)
                    await utilities_reFactore.report_to_user('warning', financial.chat_id, message)

                    return templates.TemplateResponse(
                        request=request,
                        name='error_and_refund_credit_to_walet.html',
                        context={'translation': dialogues, 'amount': financial.amount}
                    )

            else:
                error_code = response_json.get('data', {}).get('code', 404)

                if error_code == 404:
                    error_code = response_json.get('errors', {}).get('code', 404)

                return templates.TemplateResponse(
                    request=request,
                    name='fail_pay.html',
                    context={'translation': dialogues, 'error_code': error_code})

        else:
            return templates.TemplateResponse(request=request, name='fail_pay.html', context={'error_reason': 'پرداخت از طرف درگاه پرداخت تایید نشده است', 'error_code': 400})
