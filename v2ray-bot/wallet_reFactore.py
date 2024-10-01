import json
import uuid

import crud, arrow, logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import setting
from database_sqlalchemy import SessionLocal
from utilities_reFactore import FindText, message_token, handle_error
from API import zarinPalAPI, cryptomusAPI, convert_irt_to_usd

def human_readable(date, user_language):
    get_date = arrow.get(date)
    if user_language == 'en':
        return get_date.humanize()

    try:
        return get_date.humanize(locale="fa-ir")
    except ValueError as e:
        if 'week' in str(e):
            return str(get_date.humanize()).replace('weeks ago', 'هفته پیش').replace('a week ago', 'هفته پیش')
        else:
            return get_date.humanize()

    except Exception as e:
        logging.error(f'an error in humanize data: {e}')
        return f'Error In Parse Data'


async def wallet_page(update, context):
    query = update.callback_query
    chat_id = update.effective_chat.id
    ft_instance = FindText(update, context)

    try:
        with SessionLocal() as session:
            get_user = crud.get_user(session, chat_id)
            get_financial_reports = crud.get_financial_reports(session, chat_id, 5, True)

            last_transaction = await ft_instance.find_text('no_transaction_yet')
            lasts_report = ''

            if get_financial_reports:
                last_transaction = human_readable(f'{get_financial_reports[0].register_date}', await ft_instance.find_user_language())
                lasts_report = await ft_instance.find_text('recent_transactions')
                for report in get_financial_reports:
                    lasts_report += f"\n{await ft_instance.find_text('recive_money') if report.operation == 'recive' else
                    await ft_instance.find_text('spend_money')} {report.amount:,} {await ft_instance.find_text('irt')} - {human_readable(report.register_date, await ft_instance.find_user_language())}"

            keyboard = [
                [InlineKeyboardButton(await ft_instance.find_keyboard('refresh'), callback_data='wallet_page'),
                 InlineKeyboardButton(await ft_instance.find_keyboard('increase_balance'), callback_data='buy_credit_volume')],
                [InlineKeyboardButton(await ft_instance.find_keyboard('financial_transactions'), callback_data='financial_transactions_wallet')],
                [InlineKeyboardButton(await ft_instance.find_keyboard('back_button'), callback_data='start')]]

            text = (
                f"<b>{await ft_instance.find_text('wallet_page_title')}</b>"
                f"\n\n{await ft_instance.find_text('wallet_balance_key')} {get_user.wallet:,} {await ft_instance.find_text('irt')}"
                f"\n{await ft_instance.find_text('last_transaction')} {last_transaction}"
                f"\n\n{lasts_report}"
            )

            await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')

    except Exception as e:
        logging.error(f'error in wallet page: {e}')
        if "specified new message content and reply markup are exactly the same" in str(e):
            return await query.answer()
        return await query.answer(await ft_instance.find_text('error_message'))


async def financial_transactions_wallet(update, context):
    query = update.callback_query
    chat_id = update.effective_chat.id
    ft_instance = FindText(update, context)

    try:
        with SessionLocal() as session:
            get_financial_reports = crud.get_financial_reports(session, chat_id, 20)

            if get_financial_reports:
                lasts_report = await ft_instance.find_text('recent_transactions') + '\n'
                for report in get_financial_reports:
                    lasts_report += f"\n\n{await ft_instance.find_text('recive_money') if report.operation == 'recive' else
                    await ft_instance.find_text('spend_money')} {report.value:,} {await ft_instance.find_text('irt')} - {human_readable(report.register_date, await ft_instance.find_user_language())}"
            else:
                lasts_report = await ft_instance.find_text('no_transaction_yet')

            keyboard = [
                [InlineKeyboardButton(await ft_instance.find_keyboard('refresh'), callback_data='financial_transactions_wallet')],
                [InlineKeyboardButton(await ft_instance.find_keyboard('back_button'), callback_data='wallet_page')]]

            text_ = f"\n\n{lasts_report}"
            await query.edit_message_text(text=text_, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')

    except Exception as e:
        logging.error(f'error in wallet page: {e}')
        if "specified new message content and reply markup are exactly the same" in str(e):
            return await query.answer()
        return await query.answer(await ft_instance.find_text('error_message'))


async def buy_credit_volume(update, context):
    query = update.callback_query
    ft_instance = FindText(update, context)

    try:
        text = await ft_instance.find_text('add_crredit_to_wallet_title')

        keyboard = [
            [InlineKeyboardButton(f"50,000 {await ft_instance.find_text('irt')}", callback_data="create_invoice__increase_wallet_balance__1000"),
             InlineKeyboardButton(f"100,000 {await ft_instance.find_text('irt')}", callback_data="create_invoice__increase_wallet_balance__100000")],
            [InlineKeyboardButton(f"200,000 {await ft_instance.find_text('irt')}", callback_data="create_invoice__increase_wallet_balance__200000"),
             InlineKeyboardButton(f"500,000 {await ft_instance.find_text('irt')}", callback_data="create_invoice__increase_wallet_balance__500000")],
            [InlineKeyboardButton(await ft_instance.find_keyboard('back_button'), callback_data='wallet_page')]
        ]

        await query.edit_message_text(text=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    except Exception as e:
        logging.error(f'error in buy credit volume: {e}')
        return await query.answer(await ft_instance.find_text('error_message'))


@handle_error.handle_functions_error
@message_token.check_token
async def create_invoice(update, context):
    query = update.callback_query
    chat_id = update.effective_chat.id
    ft_instance = FindText(update, context)
    pay_by_wallet = True
    service_id = None
    action, *extra_data = query.data.replace('create_invoice__', '').split('__')

    with SessionLocal() as session:
        with session.begin():

            if action == "increase_wallet_balance":
                pay_by_wallet = False
                amount = int(extra_data[0])
                operation = 'recive'
                back_button_callback = 'buy_credit_volume'
                invoice_extra_data = await ft_instance.find_text('charge_wallet')

            elif action == "buy_vpn_service":
                period, traffic = extra_data
                amount = (int(traffic) * setting.PRICE_PER_GB) + (int(period) * setting.PRICE_PER_DAY)
                product_id, back_button_callback= 1, 'vpn_set_period_traffic__30_40'
                operation = 'spend'
                invoice_extra_data = (f"{await ft_instance.find_text('charge_wallet')}"
                                      f"\n{await ft_instance.find_text('traffic')} {traffic} {await ft_instance.find_keyboard('gb_lable')}"
                                      f"\n{await ft_instance.find_text('period')} {period} {await ft_instance.find_keyboard('day_lable')}")

                purchase = crud.creatcreate_purchase(session, product_id, chat_id, traffic, period)
                service_id = purchase.purchase_id

            finacial_report = crud.create_financial_report(session, operation, chat_id, amount, action, service_id, 'not paid')

            keyboard = [
                [InlineKeyboardButton(await ft_instance.find_keyboard('iran_payment_getway'), callback_data=f"pay_by_zarinpal__{action}__{finacial_report.financial_id}")],
                [InlineKeyboardButton(await ft_instance.find_keyboard('pay_with_wallet_balance'), callback_data=f"pay_by_wallet__{action}__{finacial_report.financial_id}") if pay_by_wallet else [],
                 InlineKeyboardButton(await ft_instance.find_keyboard('cryptomus_payment_getway'), callback_data=f"pay_by_cryptomus__{action}__{finacial_report.financial_id}")],
                [InlineKeyboardButton(await ft_instance.find_keyboard('back_button'), callback_data=back_button_callback)],
            ]
            keyboard = [list(filter(None, row)) for row in keyboard]

            text = (f"<b>{await ft_instance.find_text('invoice_title')}"
                    f"\n\n{await ft_instance.find_text('price')} {amount:,} {await ft_instance.find_text('irt')}"
                    f"\n\n{await ft_instance.find_text('invoice_extra_data')}\n{invoice_extra_data}"
                    f"\n\n{await ft_instance.find_text('payment_option_title')}</b>")

            await query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))


@handle_error.handle_functions_error
@message_token.check_token
async def pay_by_zarinpal(update, context):
    query = update.callback_query
    ft_instance = FindText(update, context)
    action, financial_id = query.data.replace('pay_by_zarinpal__', '').split('__')

    with SessionLocal() as session:
        with session.begin():
            get_financial = crud.get_financial_report_by_id(session, financial_id)

            instance = zarinPalAPI.SendInformation(setting.zarinpal_merchant_id)

            create_zarinpal_invoice = await instance.execute(
                merchant_id=setting.zarinpal_merchant_id,
                amount=get_financial.amount,
                currency='IRT',
                description=action.replace('vpn', 'vps'),
                callback_url=setting.zarinpal_url_callback,
                metadata={"mobile": str(get_financial.owner.phone_number), "email": get_financial.owner.email}
            )

            if not create_zarinpal_invoice:
                return await query.answer(await ft_instance.find_text('fail_to_create_payment_getway'), show_alert=True)

            crud.update_financial_report(
                session, get_financial.financial_id,
                payment_getway='zarinpal',
                authority=create_zarinpal_invoice.authority,
                currency=create_zarinpal_invoice.currency,
                url_callback=create_zarinpal_invoice.url_callback,
            )

            keyboard = [
                [InlineKeyboardButton(await ft_instance.find_keyboard('login_to_payment_getway'), url=f'https://payment.zarinpal.com/pg/StartPay/{create_zarinpal_invoice.authority}')],
                [InlineKeyboardButton(await ft_instance.find_keyboard('back_button'), callback_data="start_in_new_message")]
            ]

            text = (
                f"<b>{await ft_instance.find_text('payment_getway_title')}</b>"
                f"\n{await ft_instance.find_text('zarinpal_payment_getway_body')}"
                f"\n\n{await ft_instance.find_text('payment_getway_lable')} {await ft_instance.find_text('zarinpal_lable')}"
                f"\n{await ft_instance.find_text('price')} {get_financial.amount:,} {await ft_instance.find_text('irt')}"
                f"\n\n<b>{await ft_instance.find_text('payment_getway_tail')}</b>"
            )

            await query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))


@handle_error.handle_functions_error
@message_token.check_token
async def pay_by_cryptomus(update, context):
    query = update.callback_query
    ft_instance = FindText(update, context)
    action, financial_id = query.data.replace('pay_by_cryptomus__', '').split('__')
    order_id = uuid.uuid4().hex

    with SessionLocal() as session:
        with session.begin():
            get_financial = crud.get_financial_report_by_id(session, financial_id)
            amount = convert_irt_to_usd.convert_irt_to_usd_by_teter(get_financial.amount)

            instance = cryptomusAPI.CreateInvoice(setting.cryptomus_api_key, setting.cryptomus_merchant_id)
            create_cryptomus_invoice = await instance.execute(
                amount=str(amount),
                order_id=order_id,
                lifetime=3600,
                currency='USD',
                url_callback=setting.cryptomus_url_callback
            )

            if not create_cryptomus_invoice:
                return await query.answer(await ft_instance.find_text('fail_to_create_payment_getway'), show_alert=True)

            invoice_link = create_cryptomus_invoice.get('result', {}).get('url')
            if not invoice_link:
                return await query.answer(await ft_instance.find_text('fail_to_create_payment_getway'), show_alert=True)

            crud.update_financial_report(
                session, get_financial.financial_id,
                payment_getway='cryptomus',
                authority=order_id,
                currency='USD',
                url_callback=setting.zarinpal_url_callback,
                additional_data=json.dumps({'amount_in_usd': amount})
            )

            keyboard = [
                [InlineKeyboardButton(await ft_instance.find_keyboard('login_to_payment_getway'), url=invoice_link)],
                [InlineKeyboardButton(await ft_instance.find_keyboard('back_button'), callback_data="start_in_new_message")]
            ]

            text = (
                f"<b>{await ft_instance.find_text('payment_getway_title')}</b>"
                f"\n{await ft_instance.find_text('cryptomus_payment_getway_body')}"
                f"\n\n{await ft_instance.find_text('payment_getway_lable')} {await ft_instance.find_text('cryptomus_lable')}"
                f"\n{await ft_instance.find_text('price')} {amount:,} {await ft_instance.find_text('usd')}"
                f"\n\n<b>{await ft_instance.find_text('payment_getway_tail')}</b>"
            )

            await query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))


async def increase_wallet_balance(update, context, session, financial_id: int):
    get_financial = crud.get_financial_report_by_id(session, financial_id)

    ft_instance = FindText(update, context)

    crud.add_credit_to_wallet(session, get_financial)
    text = await ft_instance.find_text('amount_added_to_wallet_successfully')
    text = text.format(f"{get_financial.amount:,}")

    await context.bot.send_message(text=text, chat_id=get_financial.chat_id)
