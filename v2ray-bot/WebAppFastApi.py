from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import setting, logging, traceback
import crud, requests, utilities_reFactore, wallet_reFactore
from database_sqlalchemy import SessionLocal
from vpn_service import buy_and_upgrade_service
from WebAppDialogue import transaction
from pydantic import BaseModel
from API import cryptomusAPI

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def refund(session, financial_db):
    crud.add_credit_to_wallet(session, financial_db, 'refund')
    session.commit()

class PaymentError(Exception):
    pass

def verify_payment_zarinpal(authority: str, amount: int):
    """Verifies payment with Zarinpal API."""
    url = 'https://payment.zarinpal.com/pg/v4/payment/verify.json'
    json_payload = {
        'merchant_id': setting.zarinpal_merchant_id,
        'amount': amount,
        'authority': authority
    }

    response = requests.post(url=url, json=json_payload)

    if not response.json():
        raise PaymentError(f"Invalid response from Zarinpal: {response}")

    return response.json()


@app.get('/zarinpal_receive_payment_result/')
async def receive_payment_result(Authority: str, Status: str, request: Request):
    """Handles the Zarinpal payment result webhook."""
    with SessionLocal() as session:
        session.begin()
        financial = crud.get_financial_report_by_authority(session, Authority)

        if Status != 'OK' or not financial:
            dialogues = transaction.get('fa')
            return templates.TemplateResponse(
                request=request,
                name='fail_pay.html',
                context={'translation': dialogues, 'error_code': 400}
            )

        try:
            dialogues = transaction.get(financial.owner.language, transaction.get('fa'))
            response_json = verify_payment_zarinpal(Authority, financial.amount)
            payment_code = response_json.get('data', {}).get('code', 101)

        except Exception as e:
            await report_unhandled_error(e, 'ZarinPalWebApp', Authority, financial)
            return templates.TemplateResponse(
                request=request,
                name='fail_pay.html',
                context={'translation': dialogues, 'error_code': 405}
            )

        if payment_code == 100 and financial.payment_status not in ['paid', 'refund']:
            try:
                ref_id = response_json.get('data').get('ref_id')
                await handle_successful_payment(session, financial, dialogues, ref_id, Authority, 'ZarinPalWebApp')
                session.commit()
            except Exception as e:
                session.rollback()
                await handle_failed_payment(session, financial, e, dialogues, Authority, 'ZarinPalWebApp')
                return templates.TemplateResponse(
                    request=request,
                    name='error_and_refund_credit_to_wallet.html',
                    context={'translation': dialogues, 'amount': financial.amount}
                )
            else:
                return templates.TemplateResponse(
                    request=request,
                    name='success_pay.html',
                    context={'ref_id': ref_id}
                )

        else:
            error_code = response_json.get('data', {}).get('code', 404)
            error_code = response_json.get('errors', {}).get('code', 404) if error_code == 404 else error_code
            return templates.TemplateResponse(
                request=request,
                name='fail_pay.html',
                context={'translation': dialogues, 'error_code': error_code}
            )


async def handle_successful_payment(session, financial, dialogues, ref_id, authority, payment_getway):
    """Processes the successful payment."""
    class Update:
        class effective_chat:
            id = financial.owner.chat_id

    update = Update()
    context = utilities_reFactore.FakeContext()

    message = dialogues.get('successful_pay', '').format(ref_id)
    await utilities_reFactore.report_to_user('success', financial.chat_id, message)

    extra_data = ""
    if financial.action == 'buy_vpn_service':
        service = await buy_and_upgrade_service.create_service_for_user(update, context, session, financial.id_holder)
        extra_data = f"Service Traffic: {service.traffic}\nService Period: {service.period}"

    elif financial.action == 'increase_wallet_balance':
        await wallet_reFactore.increase_wallet_balance(update, context, session, financial.financial_id)

    await handle_successful_report(session, financial, extra_data, authority, payment_getway)

async def handle_failed_payment(session, financial, exception, dialogues, authority, payment_getway):
    """Handles payment failure and refunds if necessary."""
    refund(session, financial)
    error_msg = log_error(
        'Amount refunded to user wallet! Payment was not successful!', exception, authority
    )
    message = dialogues.get('operation_failed_user').format(f"{financial.amount:,}")

    await utilities_reFactore.report_to_admin('error', payment_getway, error_msg, financial.owner)
    await utilities_reFactore.report_to_user('warning', financial.chat_id, message)

async def handle_successful_report(session, financial, extra_data, authority, payment_getway):
    """Reports successful payment."""
    try:
        msg = (
            f'Action: {financial.action.replace("_", " ")}\n'
            f'Authority: {authority}\n'
            f'Amount: {financial.amount:,}\n'
            f'Service ID: {financial.id_holder}\n'
            f'{extra_data}'
        )
        await utilities_reFactore.report_to_admin('purchase', payment_getway, msg, financial.owner)
        crud.update_financial_report_status(session, financial.financial_id, 'paid')

    except Exception as e:
        logging.error(f'error in report successful payment to admin.\n{e}')

def log_error(msg, exception, order_id):
    """Logs error details."""
    logging.error(f'{msg} {exception}')
    tb = traceback.format_exc()
    error = (
        f'Unhandled error | User does not know payment status\n\n'
        f'Error Type: {type(exception)}\n'
        f'Authority: {order_id}\n'
        f'Error Reason: {exception}\n'
        f'Traceback: \n{tb}'
    )
    return error

async def report_unhandled_error(exception, section, authority, financial):
    """Reports unhandled errors to the admin."""
    error_msg = log_error('Unhandled error occurred', exception, authority)
    await utilities_reFactore.report_to_admin(
        'emergency_error', section, error_msg, financial.owner
    )

class CryptomusPaymentWebhook(BaseModel):
    type: str
    uuid: str
    order_id: str
    amount: str
    payment_amount_usd: str
    is_final: bool
    status: str
    sign: str
    additional_data: str

async def verify_cryptomus_payment(order_id: str, uuid_: str | None, financial):
    """Verifies payment status using the Cryptomus API."""
    try:
        invoice_check = await cryptomusAPI.InvoiceInfo(
            setting.cryptomus_api_key, setting.cryptomus_merchant_id
        ).execute(order_id, uuid_)

        if invoice_check:
            payment_status = invoice_check.get('result', {}).get('payment_status')
            if payment_status in ('paid', 'paid_over'):
                return invoice_check

    except Exception as e:
        await report_unhandled_error(e, 'CryptomusWebApp', order_id, financial)

@app.post('/cryptomus_receive_payment_result/')
async def crypto_receive_payment_result(data: CryptomusPaymentWebhook):
    """Handles incoming webhook for Cryptomus payment result."""
    with SessionLocal() as session:
        session.begin()
        financial = crud.get_financial_report_by_authority(session, data.order_id)

        if not financial or data.status not in ['paid', 'paid_over'] or financial.payment_status in ['paid', 'refund']:
            return

        dialogues = transaction.get(financial.owner.language, transaction.get('fa'))
        response = await verify_cryptomus_payment(data.order_id, None, financial)

        if response:
            try:
                ref_id = response.get('result', {}).get('uuid')
                await handle_successful_payment(session, financial, dialogues, ref_id, data.order_id, 'CryptomusWebApp')
                session.commit()
            except Exception as e:
                session.rollback()
                await handle_failed_payment(session, financial, e, dialogues, data.order_id, 'CryptomusWebApp')
