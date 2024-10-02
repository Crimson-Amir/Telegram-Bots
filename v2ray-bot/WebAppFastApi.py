from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import utilities_reFactore
import crud, WebAppUtilities
from database_sqlalchemy import SessionLocal
from WebAppDialogue import transaction

app = FastAPI()
templates = Jinja2Templates(directory="templates")

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
            response_json = WebAppUtilities.verify_payment_zarinpal(Authority, financial.amount)
            payment_code = response_json.get('data', {}).get('code', 101)

        except Exception as e:
            await WebAppUtilities.report_unhandled_error(e, 'ZarinPalWebApp', Authority, financial)
            return templates.TemplateResponse(
                request=request,
                name='fail_pay.html',
                context={'translation': dialogues, 'error_code': 405}
            )

        if payment_code == 100 and financial.payment_status not in ['paid', 'refund']:

            ref_id = response_json.get('data').get('ref_id')
            message = dialogues.get('successful_pay', '').format(ref_id)
            await utilities_reFactore.report_to_user('success', financial.chat_id, message)

            try:
                await WebAppUtilities.handle_successful_payment(session, financial, Authority, 'ZarinPalWebApp')
                session.commit()
            except Exception as e:
                session.rollback()
                await WebAppUtilities.handle_failed_payment(session, financial, e, dialogues, Authority, 'ZarinPalWebApp')
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

@app.post('/cryptomus_receive_payment_result/')
async def crypto_receive_payment_result(data: WebAppUtilities.CryptomusPaymentWebhook):
    """Handles incoming webhook for Cryptomus payment result."""
    with SessionLocal() as session:
        session.begin()
        financial = crud.get_financial_report_by_authority(session, data.order_id)

        if not financial or data.status not in ['paid', 'paid_over'] or financial.payment_status in ['paid', 'refund']:
            return

        dialogues = transaction.get(financial.owner.language, transaction.get('fa'))
        response = await WebAppUtilities.verify_cryptomus_payment(data.order_id, None, financial)

        if response:
            ref_id = response.get('result', {}).get('uuid')
            message = dialogues.get('successful_pay', '').format(ref_id)
            await utilities_reFactore.report_to_user('success', financial.chat_id, message)

            try:
                await WebAppUtilities.handle_successful_payment(session, financial, data.order_id, 'CryptomusWebApp')
                session.commit()
            except Exception as e:
                session.rollback()
                await WebAppUtilities.handle_failed_payment(session, financial, e, dialogues, data.order_id, 'CryptomusWebApp')
