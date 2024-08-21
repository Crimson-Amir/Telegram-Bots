from datetime import datetime, timedelta
import pytz, requests, random, json, qrcode
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from private import ADMIN_CHAT_ID, telegram_bot_token, merchent_id, infinity_name
from utilities import sqlite_manager, api_operation, second_to_ms, traffic_to_gb, ranking_manage, wallet_manage
from io import BytesIO


error_reasons = {
    -9: "خطای اعتبار سنجی: مرچنت کد داخل تنظیمات وارد نشده باشد - آدرس بازگشت وارد نشده باشد - توضیحات بیش از حد مجاز - مبلغ پرداختی کمتر یا بیشتر از حد مجاز است",
    -10: "ای پی یا مرچنت كد پذیرنده صحیح نیست.",
    -11: "مرچنت کد فعال نیست، پذیرنده مشکل خود را به امور مشتریان زرین‌پال ارجاع دهد.",
    -12: "تلاش بیش از دفعات مجاز در یک بازه زمانی کوتاه به امور مشتریان زرین پال اطلاع دهید",
    -15: "درگاه پرداخت به حالت تعلیق در آمده است، پذیرنده مشکل خود را به امور مشتریان زرین‌پال ارجاع دهد.",
    -16: "سطح تایید پذیرنده پایین تر از سطح نقره ای است.",
    -17: "محدودیت پذیرنده در سطح آبی",
    100: "عملیات موفق",
    -30: "پذیرنده اجازه دسترسی به سرویس تسویه اشتراکی شناور را ندارد.",
    -31: "حساب بانکی تسویه را به پنل اضافه کنید. مقادیر وارد شده برای تسهیم درست نیست.",
    -32: "مبلغ وارد شده از مبلغ کل تراکنش بیشتر است.",
    -33: "درصدهای وارد شده صحیح نیست.",
    -34: "مبلغ وارد شده از مبلغ کل تراکنش بیشتر است.",
    -35: "تعداد افراد دریافت کننده تسهیم بیش از حد مجاز است.",
    -36: "حداقل مبلغ جهت تسهیم باید ۱۰۰۰۰ ریال باشد.",
    -37: "یک یا چند شماره شبای وارد شده برای تسهیم از سمت بانک غیر فعال است.",
    -38: "خطا٬عدم تعریف صحیح شبا٬لطفا دقایقی دیگر تلاش کنید.",
    -39: "خطایی رخ داده است به امور مشتریان زرین پال اطلاع دهید.",
    -40: "خطا در پارامترهای اضافی. پارامتر expire_in معتبر نیست.",
    -41: "حداکثر مبلغ پرداختی ۱۰۰ میلیون تومان است.",
    -50: "مبلغ پرداخت شده با مقدار مبلغ ارسالی در متد وریفای متفاوت است.",
    -51: "پرداخت ناموفق.",
    -52: "خطای غیر منتظره‌ای رخ داده است. پذیرنده مشکل خود را به امور مشتریان زرین‌پال ارجاع دهد.",
    -53: "پرداخت متعلق به این مرچنت کد نیست.",
    -54: "اتوریتی نامعتبر است.",
    -55: "تراکنش مورد نظر یافت نشد.",
    -60: "امکان ریورس کردن تراکنش با بانک وجود ندارد.",
    -61: "تراکنش موفق نیست یا قبلا ریورس شده است.",
    -62: "آی پی درگاه ست نشده است.",
    -63: "حداکثر زمان (۳۰ دقیقه) برای ریورس کردن این تراکنش منقضی شده است.",
    101: "تراکنش وریفای شده است.",
    404: "وریفای با موفقیت انجام نشده است"
}



def report_status_to_admin(text, chat_id):
    try:
        text = (f'🔵 Report Status:'
                f'\nUser Chat ID: {chat_id}'
                f'\n{text}')

        telegram_bot_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
        requests.post(telegram_bot_url, data={'chat_id': ADMIN_CHAT_ID, 'text': text})
    except Exception as e:
        print(f'Failed to send message to ADMIN {e}')

def report_status_to_user(text, chat_id):
    try:
        telegram_bot_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
        requests.post(telegram_bot_url, data={'chat_id': chat_id, 'text': text})
    except Exception as e:
        report_status_to_admin(f'Failed to message to User [WEB SERVER]\ntext: {text}\nerror: {e}', chat_id)

def record_operation_in_file(chat_id, status_of_pay, price, name_of_operation, operation=1):
    try:
        if operation:
            pay_emoji = '💰'
            status_of_operation = 'دریافت پول'
        else:
            pay_emoji = '💸'
            status_of_operation = 'پرداخت پول'

        status_text = '🟢 تایید شده' if status_of_pay else '🔴 تایید نشده'
        date = datetime.now(pytz.timezone('Asia/Tehran')).strftime('%Y/%m/%d - %H:%M:%S')

        text = (f"\n\n{pay_emoji} {status_of_operation} | {status_text}"
                f"\nمبلغ تراکنش: {price:,} تومان"
                f"\nنام تراکنش: {name_of_operation}"
                f"\nتاریخ: {date}")

        with open(f'financial_transactions/{chat_id}.txt', 'a', encoding='utf-8') as e:
            e.write(text)
        return True
    except Exception as e:
        print(f'failed to record in file {e}')


def subcategory_auto(invite_chat_id, price):
    try:
        if invite_chat_id and price:
            calculate_price = int(price * 10 / 100)

            wallet_manage.add_to_wallet(invite_chat_id, calculate_price, user_detail={'name': invite_chat_id, 'username': invite_chat_id})
            text = (f"{calculate_price:,} تومان به کیف پول شما اضافه شد."
                    "\n\nاز طریق ارسال لینک دعوت توسط شما، کاربر جدیدی به ربات ما اضافه شده و خرید انجام داده است. به عنوان تشکر، 10 درصد از مبلغ خرید او به کیف پول شما اضافه شد."
                    "\nمتشکریم!")
            report_status_to_user(text, chat_id=invite_chat_id)
    except Exception as e:
        print(f'failed subcateory! {e}')


def upgrade_service(service_id):
    get_client = sqlite_manager.custom(f'SELECT chat_id,product_id,inboun_id,client_email FROM Purchased WHERE id = {service_id}]')

    chat_id = get_client[0][0]
    product_id = get_client[0][1]
    inbound_id = int(get_client[0][2])
    client_email = get_client[0][3]

    get_server_domain = sqlite_manager.select(column='server_domain', table='Product', where=f'id = {product_id}')

    user_db = sqlite_manager.custom(f'SELECT chat_id,traffic,period FROM User WHERE chat_id = {chat_id}')

    user_id = user_db[0][0]
    traffic_db = user_db[0][1]
    period = user_db[0][2]

    price = ranking_manage.discount_calculation(user_id, traffic_db, period)

    now = datetime.now(pytz.timezone('Asia/Tehran'))

    ret_conf = api_operation.get_inbound(inbound_id, get_server_domain[0][0])
    client_list = json.loads(ret_conf['obj']['settings'])['clients']

    for client in client_list:
        if client['email'] == client_email:
            client_id = client['id']
            get_client_status = api_operation.get_client(client_email, get_server_domain[0][0])

            if get_client_status['obj']['enable']:
                tra = client['totalGB']
                traffic = int((traffic_db * (1024 ** 3)) + tra)
                expiry_timestamp = client['expiryTime']
                expiry_datetime = datetime.fromtimestamp(expiry_timestamp / 1000)
                new_expiry_datetime = expiry_datetime + timedelta(days=period)
                my_data = int(new_expiry_datetime.timestamp() * 1000)
            else:
                traffic = int(traffic_db * (1024 ** 3))
                my_data = now + timedelta(days=period)
                my_data = int(my_data.timestamp() * 1000)
                print(api_operation.reset_client_traffic(inbound_id, client_email, get_server_domain[0][0]))

            data = {
                "id": inbound_id,
                "settings": "{{\"clients\":[{{\"id\":\"{0}\",\"alterId\":0,"
                            "\"email\":\"{1}\",\"limitIp\":0,\"totalGB\":{2},\"expiryTime\":{3},"
                            "\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}}]}}".format(client_id, client_email,
                                                                                       traffic, my_data)}

            update_client = api_operation.update_client(client_id, data, get_server_domain[0][0])
            print(update_client)

            sqlite_manager.update({'Purchased': {'status': 1, 'date': datetime.now(pytz.timezone('Asia/Tehran')),
                                                 'notif_day': 0, 'notif_gb': 0, 'client_id': client_id}} , where=f'client_email = "{client_email}"')

            record_operation_in_file(chat_id=chat_id, price=price, name_of_operation=f'تمدید یا ارتقا سرویس {client_email}', operation=0, status_of_pay=1)
            report_status_to_admin(text=f'🟢 User Upgrade Service [WEB SERVER]\nService Name: {client_email}\nTraffic: {traffic_db}GB\nPeriod: {period}day', chat_id=chat_id)
            break

    return get_client[0][4], price


def add_client_bot(purchased_id):
    random_number = random.randint(0, 10_000_000)
    get_client_db = sqlite_manager.custom(f'SELECT chat_id,product_id FROM Purchased WHERE id = {purchased_id}]')

    get_service_db = sqlite_manager.select(
        column='inbound_id,name,period,traffic,domain,server_domain,inbound_host,inbound_header_type',
        table='Product', where=f'id = {get_client_db[0][1]}')

    inbound_id = get_service_db[0][0]
    product_name = get_service_db[0][1]
    period_db = get_service_db[0][2]
    traffic_db = get_service_db[0][3]
    domain_db = get_service_db[0][4]
    server_domain_db = get_service_db[0][5]
    inbound_host = get_service_db[0][6]
    inbound_header_type = get_service_db[0][7]

    id_ = f"{get_client_db[0][0]}_{random_number}"
    name = '_Gift' if 'gift' in product_name else ''
    email_ = f"{purchased_id}{name}"

    if traffic_db:
        traffic_to_gb_ = traffic_to_gb(traffic_db, False)
    else:
        email_ = f"{purchased_id}{infinity_name}"
        traffic_to_gb_ = 0

    if period_db:
        now = datetime.now(pytz.timezone('Asia/Tehran'))
        period = period_db
        now_data_add_day = now + timedelta(days=period)
        time_to_ms = second_to_ms(now_data_add_day)
    else:
        time_to_ms = 0

    data = {
        "id": int(inbound_id),
        "settings": "{{\"clients\":[{{\"id\":\"{0}\",\"alterId\":0,\"start_after_first_use\":true,"
                    "\"email\":\"{1}\",\"limitIp\":0,\"totalGB\":{2},\"expiryTime\":{3},"
                    "\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}}]}}".format(id_, email_, traffic_to_gb_, time_to_ms)
    }

    create = api_operation.add_client(data, server_domain_db)

    check_servise_available = api_operation.get_client(email_, domain=server_domain_db)
    if not check_servise_available['obj']: return False, create, 'service do not create'

    get_cong = api_operation.get_client_url(email_, int(inbound_id),
                                            domain=domain_db, server_domain=server_domain_db,
                                            host=inbound_host, header_type=inbound_header_type)

    sqlite_manager.update({'Purchased': {'inbound_id': int(inbound_id), 'client_email': email_,
                                         'client_id': id_, 'date': datetime.now(pytz.timezone('Asia/Tehran')),
                                         'details': get_cong, 'active': 1, 'status': 1}}, where=f'id = {purchased_id}')

    if create['success']:
        return True, create, 'service create success'
    else:
        return {'success': False, 'msg': 'Maximum retries exceeded'}


def send_clean_for_customer(id_, max_retries=2):
    create = add_client_bot(id_)
    if create[0]:
        get_client = sqlite_manager.custom(f'SELECT chat_id,product_id,inboun_id,client_email FROM Purchased WHERE id = {id_}]')

        chat_id = get_client[0][0]
        product_id = get_client[0][1]
        inbound_id = get_client[0][2]
        client_email = get_client[0][3]

        try:
            get_product = sqlite_manager.select(column='price,domain,server_domain,inbound_host,inbound_header_type',
                                                table='Product', where=f'id = {product_id}')
            get_user_detail = sqlite_manager.select(column='invited_by', table='User', where=f'chat_id={chat_id}')

            get_domain = get_product[0][1]
            get_server_domain = get_product[0][2]
            inbound_host = get_product[0][3]
            inbound_header_type = get_product[0][4]

            returned = api_operation.get_client_url(client_email=client_email, inbound_id=inbound_id,
                                                    domain=get_domain, server_domain=get_server_domain,
                                                    host=inbound_host,
                                                    header_type=inbound_header_type)
            if returned:
                returned_copy = f'`{returned}`'
                qr_code = qrcode.make(returned)
                qr_image = qr_code.get_image()
                buffer = BytesIO()
                qr_image.save(buffer, format='PNG')
                binary_data = buffer.getvalue()

                telegram_api_url = f"https://api.telegram.org/bot{telegram_bot_token}/"

                url = telegram_api_url + "sendPhoto"
                files = {"photo": ("qr_code.png", binary_data)}
                keyboard = [[{"text": "دریافت فایل سرویس", "callback_data": f"create_txt_file_{id_}"},
                             {"text": "🎛 سرویس های من", "callback_data": f"my_service"}],
                            [{"text": "صفحه اصلی ربات ↵", "callback_data": f"main_menu_in_new_message"}]]
                reply_markup = json.dumps({"inline_keyboard": keyboard})

                data = {
                    "chat_id": chat_id,
                    "caption": (
                        f'سرویس شما با موفقیت فعال شد✅\n\n*• میتونید جزئیات سرویس رو از بخش "سرویس های من" مشاهده کنید.'
                        f'\n\n✪ لطفا سرویس رو به صورت مستقیم از طریق پیام رسان های ایرانی یا پیامک ارسال نکنید، '
                        f'با کلیک روی گزینه "دریافت فایل" سرویس را به صورت فایل یا کیوآرکد ارسال کنید.*'
                        f'\n\n\nلینک:\n{returned_copy}'),
                    "parse_mode": "Markdown",
                    "reply_markup": reply_markup
                }

                response = requests.post(url, data=data, files=files)

                if response.status_code != 200:
                    raise ConnectionError(f"Failed to send photo: {response.text}")

                price = ranking_manage.discount_calculation(direct_price=get_product[0][0], user_id=chat_id)
                record_operation_in_file(chat_id=chat_id, price=price,
                                         name_of_operation=f'خرید سرویس {client_email}', operation=0,
                                         status_of_pay=1)

                admin_report_text = f'🟢 Send service to user successful [WEB SERVER]\nClient Email: {client_email}'
                report_status_to_admin(text=admin_report_text, chat_id=chat_id)

                invite_chat_id = get_user_detail[0][0]
                subcategory_auto(invite_chat_id, price)

                return {'success': True, 'msg': 'config created successfully', 'purchased_id': id_}

            else:
                admin_report_text = f'🔴 Send service to user Failed [WEB SERVER REPORT]\nClient Email: {client_email}'
                report_status_to_admin(text=admin_report_text, chat_id=chat_id)
                raise ValueError('create service is failed')

        except Exception as e:
            admin_report_text = f'🔴 ERROR IN SEND CLEAN FOR CUSTOMER [WEB SERVER REPORT]\nClient Email: {client_email}\n{e}'
            report_status_to_admin(text=admin_report_text, chat_id=chat_id)
            raise ValueError('create service is failed')

    elif not create[0] and create[2] == 'service do not create':
        admin_report_text = f'🔴 SERVICE DONT CREATED SUCCESSFULL AND TRY ONE MORE TIME (SEND CLEAN FOR CUSTOMER) [WEB SERVER REPORT]\nClient Email: {create}'
        report_status_to_admin(text=admin_report_text, chat_id=None)

        if max_retries > 0:
            return send_clean_for_customer(id_, max_retries - 1)
        else:
            raise ValueError('create service is failed')


def add_credit_to_wallet(credit_id):
    get_credit = sqlite_manager.select(column='chat_id,value', table='Credit_History', where=f'id = {credit_id}')
    wallet_manage.add_to_wallet_without_history(get_credit[0][0], get_credit[0][1])

    sqlite_manager.update({'Credit_History': {'active': 1, 'date': datetime.now(pytz.timezone('Asia/Tehran'))}}
                          , where=f'id = "{credit_id}"')

    record_operation_in_file(chat_id=get_credit[0][0], price=get_credit[0][1],
                             name_of_operation=f'واریز به کیف پول', operation=1,
                             status_of_pay=1)

    report_status_to_admin('🟢 WALLET OPERATOIN SUCCESSFULL [WEB SERVER]', get_credit[0][0])
    return get_credit[0][0]


def add_to_user_credit(chat_id, value, tell_to_customer=True):
    sqlite_manager.custom(f'UPDATE User SET wallet = wallet + {value} WHERE chat_id = {chat_id}')
    if tell_to_customer:
        report_status_to_user('🟡 هنگام اجرای عملیات خطایی به وجود آمد!'
                              f'\nمبلغ {value:,} تومان به کیف پول شما اضافه شد.'
                              ' لطفا عملیات مورد نظر رو از طریق اعتبار کیف پول انجام بدید.', chat_id)
