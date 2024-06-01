import json
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from admin_task import sqlite_manager, ranking_manage
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utilities import init_name, report_status_to_admin
from cryptomus import get_teter_price, cryptomusApi
from tasks import handle_telegram_exceptions, send_clean_for_customer, task, add_credit_to_wallet
from private import cryptomus_api_key, cryptomus_merchant_id
import uuid


status_fa = {
    'wrong_amount': 'کمتر از مقدار مورد نیاز پرداخت شده',
    'process': 'درحال بررسی پرداخت',
    'confirm_check': 'ما تراکنش را در بلاک چین دیده‌ایم و منتظر تأیید هستیم',
    'wrong_amount_waiting': 'کمتر از مقدار مورد نیاز پرداخت شده، با امکان پرداخت اضافی',
    'check': 'در حال انتظار برای نمایش تراکنش در بلاک چین',
    'fail': 'پرداخت با مشکل مواجه شده است',
    'cancel': 'پرداخت منقضی شده است، پرداختی انجام نشد',
    'system_fail': 'یک خطای سیستم رخ داده است',
    'refund_process	': 'بازپرداخت درحال پردازش است',
    'refund_fail': 'هنگام بازپرداخت خطایی رخ داد',
    'refund_paid': 'باز پرداخت با موفقیت انجام شد',
    'locked': 'به دلیل AML Program قفل شده است',

}

text = ("<b>• اطلاعات زیر رو بررسی کنید و در صورت تایید پرداخت رو نهایی کنید:</b>"
        "\n\nمدت اعتبار فاکتور: 60 دقیقه"
        "\nسرویس: {0} روز - {1} گیگابایت"
        "\n\n<b>قیمت</b>:"
        "<b> {2} $</b>"
        "{3}"
        "\n\n<b>وارد درگاه شوید و ارز مورد نظر خودر را انتخاب کنید.</b>"
        "\n<b>لطفا به شبکه، آدرس و مبلغ دقت کنید.</b>"
        "\n\n<b>• در صورتی که کمتر از مبلغ اعلام شده پرداخت کنید تراکنش شما تایید نمیشود</b>"
        "\n\n<b>بعد از پرداخت و تایید شدن پرداخت توسط سایت، دکمه پرداخت کردم را بزنید.</b>"
        )


def initialization_payment(price, user):
    dollar_price_now = get_teter_price.get_teter_price_in_rial()

    if dollar_price_now == 0:
        raise ValueError('dollar price is zero')

    dollar_price = round((price / dollar_price_now), 2)

    currency = 'USD'
    lifetime = 3600
    order_id = str(uuid.uuid4()).split('-')[0]

    additional_data = {
        'first_name': user.first_name,
        'user_name': user.username,
        'last_name': user.last_name,
        'chat_id': user.id
    }

    sqlite_manager.insert('Cryptomus', rows={'amount': str(dollar_price),
                                             'currency': currency,
                                             'lifetime': lifetime,
                                             'order_id': order_id,
                                             'chat_id': int(user["id"])})


    create_api = cryptomusApi.client(cryptomus_api_key, cryptomus_merchant_id, cryptomusApi.CreateInvoice,
                                     amount=str(dollar_price), currency=currency,
                                     order_id=order_id, lifetime=lifetime, additional_data=json.dumps(additional_data))

    if create_api:
        invoice_link = create_api[0].get('result', {}).get('url')
        if not invoice_link:
            raise ValueError(f'cryptomus url does not exist. result -> {create_api}')
    else:
        raise ValueError(f'cryptomus is empty. result -> {create_api}')


    return dollar_price, invoice_link, order_id


order_check_pay = {}
maximum_try = 3

def check_pay(order_id):
    retry = order_check_pay.get(order_id, 0)

    if retry < maximum_try:
        check_invoic = cryptomusApi.client(cryptomus_api_key, cryptomus_merchant_id, cryptomusApi.InvoiceInfo,
                                           order_id=order_id, uuid=None)

        if check_invoic:
            payment_status = check_invoic[0].get('result', {}).get('payment_status')

            if payment_status in ('paid', 'paid_over'):
                order_check_pay[order_id] = maximum_try
                fnial_payment_status = True

            elif payment_status in ('fail', 'cancel', 'system_fail'):
                order_check_pay[order_id] = maximum_try
                fnial_payment_status = False

            else:
                order_check_pay[order_id] = retry + 1
                fnial_payment_status = False

        else:
            raise ValueError(f'cryptomus is empty. result -> {check_invoic}')

    else:
        payment_status = 'request_limited'
        fnial_payment_status = False

    return fnial_payment_status, payment_status


@handle_telegram_exceptions
def cryptomus_page(update, context):
    query = update.callback_query
    user = query.from_user
    product_id = int(query.data.replace('cryptomus_page_', ''))
    package = sqlite_manager.select(table='Product', where=f'id = {product_id}')

    price = ranking_manage.discount_calculation(query.from_user['id'], direct_price=package[0][7], more_detail=True)

    if price[0] < 10_000:
        query.answer("حداقل مبلغ برای استفاده از این درگاه 10 هزارتومن است", show_alert=True)
        return

    ex = sqlite_manager.select('id', 'Purchased', where=f'active = 0 and chat_id = {user["id"]}', limit=1)

    if not ex:
        ex = sqlite_manager.insert('Purchased', rows={'active': 0, 'status': 0, 'name': init_name(user["first_name"]), 'user_name': user["username"],
                                                      'chat_id': int(user["id"]), 'product_id': product_id, 'notif_day': 0, 'notif_gb': 0})
    else:
        sqlite_manager.update({'Purchased': {'active': 0, 'status': 0, 'name': init_name(user["first_name"]),
                                             'user_name': user["username"], 'chat_id': int(user["id"]),
                                             'product_id': product_id, 'notif_day': 0, 'notif_gb': 0}}, where=f'id = {ex[0][0]}')
        ex = ex[0][0]

    check_off = f'\n<b>تخفیف: {price[1]} درصد</b>' if price[1] else ''

    dollar_price, invoice_link, order_id = initialization_payment(price[0], user)

    final_text = text.format(package[0][5], package[0][6], f'{dollar_price:,}', check_off)

    keyboard = [
        [InlineKeyboardButton("ورود به درگاه ↶", url=invoice_link)],
        [InlineKeyboardButton("پرداخت کردم ✅", callback_data=f"check_cryptomus_payment_{ex}_{order_id}")],
        [InlineKeyboardButton("صفحه اصلی ⤶", callback_data="send_main_message")]
    ]

    query.edit_message_text(text=final_text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))


def check_cryptomus_payment(update, context):
    query = update.callback_query
    user = query.from_user
    data = query.data.replace('check_cryptomus_payment_', '').split('_')
    purchased_id = int(data[0])
    order_id = data[1]

    check = check_pay(order_id)

    if check[0]:
        send_clean_for_customer(query, context, purchased_id)
        report_status_to_admin(context, f'User Buy Service By Crypto.\nOrder id: {order_id}', user.id)
    else:

        if check[1] == 'request_limited':
            query.answer('شما بیش از حد مجاز تلاش کردید!\n اگر فکر میکنید مشکلی وجود دارد، با پشتیبانی در ارتباط باشید.', show_alert=True)
        else:
            query.answer(f'پرداخت تایید نشد!\nوضعیت: {status_fa.get(check[1])} - {order_check_pay.get(order_id)}/{maximum_try}', show_alert=True)


@handle_telegram_exceptions
def cryptomus_page_upgrade(update, context):

    query = update.callback_query
    user = query.from_user
    purchased_id = int(query.data.replace('cryptomus_page_upgrade_', ''))

    package = sqlite_manager.select(table='User', where=f'chat_id = {user.id}')

    price = ranking_manage.discount_calculation(user.id, package[0][5], package[0][6], more_detail=True)

    check_off = f'\n<b>تخفیف: {price[1]} درصد</b>' if price[1] else ''

    if price[0] < 10_000:
        query.answer("حداقل مبلغ برای استفاده از این درگاه 10 هزارتومن است", show_alert=True)
        return

    dollar_price, invoice_link, order_id = initialization_payment(price[0], user)

    final_text = text.format(package[0][5], package[0][6], f'{dollar_price:,}', check_off)

    keyboard = [
        [InlineKeyboardButton("ورود به درگاه ↶", url=invoice_link)],
        [InlineKeyboardButton("پرداخت کردم ✅", callback_data=f"check_cryptomus_payment_upgrade_{purchased_id}_{order_id}")],
        [InlineKeyboardButton("صفحه اصلی ⤶", callback_data="send_main_message")]
    ]

    query.edit_message_text(text=final_text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))


def check_cryptomus_payment_upgrade(update, context):

    query = update.callback_query
    user = query.from_user
    data = query.data.replace('check_cryptomus_payment_upgrade_', '').split('_')
    purchased_id = int(data[0])
    order_id = data[1]

    check = check_pay(order_id)

    if check[0]:
        task.upgrade_service(context, purchased_id)
        report_status_to_admin(context, f'User Upgrade Service By Crypto.\nOrder id: {order_id}', user.id)
    else:

        if check[1] == 'request_limited':
            query.answer('شما بیش از حد مجاز تلاش کردید!\n اگر فکر میکنید مشکلی وجود دارد، با پشتیبانی در ارتباط باشید.', show_alert=True)
        else:
            query.answer(f'پرداخت تایید نشد!\nوضعیت: {status_fa.get(check[1])} - {order_check_pay.get(order_id)}/{maximum_try}', show_alert=True)


@handle_telegram_exceptions
def cryptomus_page_wallet(update, context):

    query = update.callback_query
    user = query.from_user
    credit_id = int(query.data.replace('cryptomus_page_wallet_', ''))

    package = sqlite_manager.select(column='value', table='Credit_History', where=f'id = {credit_id}')
    price = ranking_manage.discount_calculation(query.message.chat_id, direct_price=package[0][0], without_off=True)

    if price < 10_000:
        query.answer("حداقل مبلغ برای استفاده از این درگاه 10 هزارتومن است", show_alert=True)
        return

    dollar_price, invoice_link, order_id = initialization_payment(price, user)

    final_text = ("<b>• اطلاعات زیر رو بررسی کنید و در صورت تایید پرداخت رو نهایی کنید:</b>"
            "\n\nمدت اعتبار فاکتور: 60 دقیقه"
            "\n\n<b>قیمت</b>:"
            f"<b> {dollar_price:,} $</b>"
            "\n\n<b>وارد درگاه شوید و ارز مورد نظر خودر را انتخاب کنید.</b>"
            "\n<b>لطفا به شبکه، آدرس و مبلغ دقت کنید.</b>"
            "\n\n<b>• در صورتی که کمتر از مبلغ اعلام شده پرداخت کنید تراکنش شما تایید نمیشود</b>"
            "\n\n<b>بعد از پرداخت و تایید شدن پرداخت توسط سایت، دکمه پرداخت کردم را بزنید.</b>"
                  )

    keyboard = [
        [InlineKeyboardButton("ورود به درگاه ↶", url=invoice_link)],
        [InlineKeyboardButton("پرداخت کردم ✅", callback_data=f"check_cryptomus_payment_wallet_{credit_id}_{order_id}")],
        [InlineKeyboardButton("صفحه اصلی ⤶", callback_data="send_main_message")]
    ]

    query.edit_message_text(text=final_text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))


def check_cryptomus_payment_wallet(update, context):

    query = update.callback_query
    user = query.from_user
    data = query.data.replace('check_cryptomus_payment_wallet_', '').split('_')
    credit_id = int(data[0])
    order_id = data[1]

    check = check_pay(order_id)

    if check[0]:
        add_credit_to_wallet(context, credit_id)
        report_status_to_admin(context, f'User charge wallet By Crypto.\nOrder id: {order_id}', user.id)
    else:

        if check[1] == 'request_limited':
            query.answer('شما بیش از حد مجاز تلاش کردید!\n اگر فکر میکنید مشکلی وجود دارد، با پشتیبانی در ارتباط باشید.', show_alert=True)
        else:
            query.answer(f'پرداخت تایید نشد!\nوضعیت: {status_fa.get(check[1])} - {order_check_pay.get(order_id)}/{maximum_try}', show_alert=True)
