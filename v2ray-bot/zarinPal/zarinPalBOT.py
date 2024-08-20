import sys, os

import private

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from admin_task import sqlite_manager, ranking_manage
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utilities import init_name
from tasks import handle_telegram_exceptions
from zarinPal.zarinPalAPI import create_invoice

# buy_service, upgrade_service, charge_wallet


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
        "\nدرگاه پرداخت: زرین پال"
        "\n\nمدت اعتبار فاکتور: 10 دقیقه"
        "\nسرویس: {0} روز - {1} گیگابایت"
        "\n\n<b>قیمت</b>:"
        "<b> {2} تومان</b>"
        "{3}"
        "\n\n<b>با واردن شدن به درگاه و پرداخت مبلغ، خرید شما به صورت خودکار تایید میشود.</b>"
        )


def initialization_payment(chat_id, action, amount, id_holder=None):
    try:
        send_information = create_invoice(merchent_id=private.merchent_id, amount=amount, currency='IRT',
                                          description=action, callback_url=private.callback_url)

        print(send_information)

        if not send_information:
            return False

        sqlite_manager.custom(f"""
            INSERT INTO iraIranPaymentGeway(authority, action, id_holder, amount, currency, url_callback, chat_id, fee_type, fee) 
            VALUES ("{send_information.authority}", "{action}", "{id_holder}",
            {send_information.amount}, "{send_information.currency}" ,"{send_information.callback_url}",
            {chat_id},"{send_information.fee_type}",{send_information.fee})
        """)

        return send_information

    except Exception as e:
        print(e)
        return False


@handle_telegram_exceptions
def zarinpall_page_buy(update, context):
    query = update.callback_query
    user = query.from_user
    product_id = int(query.data.replace('zarinpall_page_buy_', ''))
    package = sqlite_manager.custom('SELECT period,traffic,price FROM Product WHERE id = {product_id}')

    price = ranking_manage.discount_calculation(query.from_user['id'], direct_price=package[0][2], more_detail=True)

    purchased_id = sqlite_manager.select('id', 'Purchased', where=f'active = 0 and chat_id = {user["id"]}', limit=1)

    if not purchased_id:
        purchased_id = sqlite_manager.insert('Purchased', rows={'active': 0, 'status': 0, 'name': init_name(user["first_name"]), 'user_name': user["username"],
                                                                'chat_id': int(user["id"]), 'product_id': product_id, 'notif_day': 0, 'notif_gb': 0})
    else:
        sqlite_manager.update({'Purchased': {'active': 0, 'status': 0, 'name': init_name(user["first_name"]),
                                             'user_name': user["username"], 'chat_id': int(user["id"]),
                                             'product_id': product_id, 'notif_day': 0, 'notif_gb': 0}}, where=f'id = {purchased_id[0][0]}')
        purchased_id = purchased_id[0][0]

    check_off = f'\n<b>تخفیف: {price[1]} درصد</b>' if price[1] else ''

    final_text = text.format(package[0][0], package[0][1], f'{price[0]:,}', check_off)
    get_data = initialization_payment(user.id, 'buy_service', price, purchased_id)

    keyboard = [
        [InlineKeyboardButton("ورود به درگاه ↶", url=f'https://payment.zarinpal.com/pg/StartPay/{get_data.authority}')],
        [InlineKeyboardButton("صفحه اصلی ⤶", callback_data="send_main_message")]
    ]

    query.edit_message_text(text=final_text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))


@handle_telegram_exceptions
def zarinpall_page_upgrade(update, context):

    query = update.callback_query
    user = query.from_user
    purchased_id = int(query.data.replace('zarinpall_page_upgrade_', ''))
    package = sqlite_manager.custom(f'SELECT period,traffic FROM User WHERE chat_id = {user.id}')

    price = ranking_manage.discount_calculation(user.id, package[0][0], package[0][1], more_detail=True)
    check_off = f'\n<b>تخفیف: {price[1]} درصد</b>' if price[1] else ''

    get_data = initialization_payment(user.id, 'upgrade_service', price, purchased_id)
    final_text = text.format(package[0][0], package[0][1], f'{price:,}', check_off)

    keyboard = [
        [InlineKeyboardButton("ورود به درگاه ↶", url=f'https://payment.zarinpal.com/pg/StartPay/{get_data.authority}')],
        [InlineKeyboardButton("صفحه اصلی ⤶", callback_data="send_main_message")]]

    query.edit_message_text(text=final_text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))


@handle_telegram_exceptions
def zarinpall_page_wallet(update, context):

    query = update.callback_query
    user = query.from_user
    credit_id = int(query.data.replace('zarinpall_page_wallet_', ''))

    package = sqlite_manager.custom(f'SELECT value FROM Credit_History where id = {credit_id}')
    price = ranking_manage.discount_calculation(query.message.chat_id, direct_price=package[0][0], without_off=True)

    get_data = initialization_payment(user.id, 'churge_wallet', price, credit_id)

    final_text = ("<b>• اطلاعات زیر رو بررسی کنید و در صورت تایید پرداخت رو نهایی کنید:</b>"
                  "\n\nمدت اعتبار فاکتور: 60 دقیقه"
                  "\n\n<b>قیمت</b>:"
                  f"<b> {price:,} تومان</b>"
                  "\n\n<b>با واردن شدن به درگاه و پرداخت مبلغ، خرید شما به صورت خودکار تایید میشود.</b>")

    keyboard = [
        [InlineKeyboardButton("ورود به درگاه ↶", url=f'https://payment.zarinpal.com/pg/StartPay/{get_data.authority}')],
        [InlineKeyboardButton("صفحه اصلی ⤶", callback_data="send_main_message")]
    ]

    query.edit_message_text(text=final_text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))

