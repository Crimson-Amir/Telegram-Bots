import random
import uuid
from datetime import datetime, timedelta
import telegram.error
from utilities import (human_readable, something_went_wrong,
                       ready_report_problem_to_admin, format_traffic, record_operation_in_file,
                       send_service_to_customer_report, report_status_to_admin, report_problem,
                       init_name, ranking_manage)
import admin_task
from private import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
import utilities
from admin_task import (add_client_bot, api_operation, second_to_ms, message_to_user, wallet_manage, sqlite_manager, ticket_manager)
import qrcode
from io import BytesIO
import pytz
import functools
from sqlite_manager import ManageDb
import json
import traceback

GET_EVIDENCE, GET_EVIDENCE_PER, GET_EVIDENCE_CREDIT, GET_TICKET, GET_CONVER, REPLY_TICKET = 0, 0, 0, 0, 0, 0
allow_user_in_server = 260

class Task(ManageDb):
    def __init__(self):
        super().__init__('v2ray')

    @staticmethod
    def handle_exceptions(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                side = 'Task Func'
                print   (f"[{side}] An error occurred in {func.__name__}: {e}")
                report_problem(func.__name__, e, side, extra_message='')

        return wrapper

    @handle_exceptions
    def upgrade_service(self, context, service_id, by_list=None):
        get_client = sqlite_manager.select(table='Purchased', where=f'id = {service_id}')

        get_server_domain = sqlite_manager.select(column='server_domain', table='Product', where=f'id = {get_client[0][6]}')

        if not by_list:
            user_db = sqlite_manager.select(table='User', where=f'chat_id = {get_client[0][4]}')
            price = ranking_manage.discount_calculation(user_db[0][3], user_db[0][5], user_db[0][6])
        else:
            user_db = by_list
            price = 0

        # client_id = get_client[0][10]
        client_email = get_client[0][9]
        inbound_id = get_client[0][7]

        now = datetime.now(pytz.timezone('Asia/Tehran'))

        ret_conf = api_operation.get_inbound(inbound_id, get_server_domain[0][0])
        client_list = json.loads(ret_conf['obj']['settings'])['clients']

        for client in client_list:
            if client['email'] == client_email:
                client_id = client['id']
                get_client_status = api_operation.get_client(client_email, get_server_domain[0][0])

                if get_client_status['obj']['enable']:
                    tra = client['totalGB']
                    traffic = int((user_db[0][5] * (1024 ** 3)) + tra)
                    expiry_timestamp = client['expiryTime']
                    expiry_datetime = datetime.fromtimestamp(expiry_timestamp / 1000)
                    new_expiry_datetime = expiry_datetime + timedelta(days=user_db[0][6])
                    my_data = int(new_expiry_datetime.timestamp() * 1000)
                else:
                    traffic = int(user_db[0][5] * (1024 ** 3))
                    my_data = now + timedelta(days=user_db[0][6])
                    my_data = int(my_data.timestamp() * 1000)
                    print(api_operation.reset_client_traffic(int(get_client[0][7]), client_email, get_server_domain[0][0]))

                data = {
                    "id": int(get_client[0][7]),
                    "settings": "{{\"clients\":[{{\"id\":\"{0}\",\"alterId\":0,"
                                "\"email\":\"{1}\",\"limitIp\":0,\"totalGB\":{2},\"expiryTime\":{3},"
                                "\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}}]}}".format(client_id, client_email,
                                                                                           traffic, my_data)}

                print(api_operation.update_client(client_id, data, get_server_domain[0][0]))

                sqlite_manager.update({'Purchased': {'status': 1, 'date': datetime.now(pytz.timezone('Asia/Tehran')),
                                                     'notif_day': 0, 'notif_gb': 0, 'client_id': client_id}}
                                      , where=f'client_email = "{get_client[0][9]}"')

                record_operation_in_file(chat_id=get_client[0][4], price=price,
                                         name_of_operation=f'تمدید یا ارتقا سرویس {get_client[0][9]}', operation=0,
                                         status_of_pay=1, context=context)

                report_status_to_admin(context, text=f'User Upgrade Service\nService Name: {get_client[0][9]}'
                                                     f'\nTraffic: {user_db[0][5]}GB\nPeriod: {user_db[0][6]}day',
                                       chat_id=get_client[0][4])

                break

        return get_client[0][4], price


task = Task()
rate_list = []


def handle_telegram_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except telegram.error.BadRequest as e:
            if 'specified new message content and reply markup are exactly the same as a current content and reply markup of the message' in e:
                pass
        except Exception as e:
            side = 'Telgram Func'
            print(f"[{side}] An error occurred in {func.__name__}: {e}")
            report_problem(func.__name__, e, side, extra_message=traceback.format_exc())
            something_went_wrong(*args)

    return wrapper


def handle_telegram_exceptions_without_user_side(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            report_problem(func.__name__, e, 'Telgram Func', extra_message=traceback.format_exc())

    return wrapper


def handle_telegram_conversetion_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            report_problem(func.__name__, e, 'Telegram Conversetion Func', extra_message=traceback.format_exc())
            something_went_wrong(*args)
            return ConversationHandler.END

    return wrapper

@handle_telegram_exceptions
def get_service_of_server(update, context):
    query = update.callback_query
    country = query.data

    plans = sqlite_manager.select(table='Product', where=f'active = 1 and country = "{country}"')
    country_flag = plans[0][3][:2]

    text = (f"<b>• {country_flag} سرویس مناسب خودتون رو انتخاب کنید:"
            f"\n\n• با انتخاب گزینه دلخواه میتونید یک سرویس شخصی سازی شده بسازید.</b>"
            "\n\n<b>• سرویس ساعتی به شما اجازه میده به اندازه مصرف در هر ساعت پرداخت کنید.</b>")

    country_unic = {name[4] for name in plans}

    for country in country_unic:
        if query.data == country:
            service_list = [service for service in plans if service[4] == country]
            keyboard = [[InlineKeyboardButton(
                f"سرویس {pattern[5]} روزه - {pattern[6]} گیگابایت - {ranking_manage.discount_calculation(query.from_user['id'], direct_price=pattern[7]):,} تومان",
                callback_data=f"service_{pattern[0]}")] for pattern in service_list]

            keyboard.append([InlineKeyboardButton("✪ سرویس دلخواه", callback_data=f"personalization_service_{plans[0][0]}")])

            keyboard.append([InlineKeyboardButton("برگشت ↰", callback_data="select_server")])

            query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')


@handle_telegram_exceptions
def hide_buttons(update, context):
    query = update.callback_query
    query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([]))
    query.answer('OK')


@handle_telegram_exceptions
def payment_page(update, context):
    query = update.callback_query
    id_ = int(query.data.replace('service_', ''))
    package = sqlite_manager.select(table='Product', where=f'id = {id_}')
    price = ranking_manage.discount_calculation(query.from_user['id'], direct_price=package[0][7], more_detail=True)
    # [InlineKeyboardButton("کارت به کارت", callback_data=f'payment_by_card_{id_}')],

    if package[0][7]:
        keyboard = [[InlineKeyboardButton("درگاه پرداخت بانکی", callback_data=f"zarinpall_page_buy_{id_}")],
                    [InlineKeyboardButton("پرداخت از کیف پول", callback_data=f'payment_by_wallet_{id_}'),
                     InlineKeyboardButton("پرداخت با کریپتو", callback_data=f"cryptomus_page_{id_}")],
                    [InlineKeyboardButton("برگشت ↰", callback_data=f"{package[0][4]}")]]

    else:
        free_service_is_taken = sqlite_manager.select(column='free_service', table='User', where=f'chat_id = {query.message.chat_id}')[0][0]

        if free_service_is_taken:
            keyboard_free = [[InlineKeyboardButton("🎁 دریافت هدیه از کانال", url='https://t.me/FreeByte_Channel/1380')],
                             [InlineKeyboardButton("برگشت ↰", callback_data=f"main_menu")]]
            query.edit_message_text(
                text='<b>شما یک بار این سرویس رو دریافت کردید!\n\n • با استفاده از گزینه زیر روزانه هدیه دریافت کنید!</b>',
                parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard_free))
            return

        else:
            keyboard = [[InlineKeyboardButton("دریافت ⤓", callback_data=f'get_free_service')],
                        [InlineKeyboardButton("برگشت ↰", callback_data="main_menu")]]

    check_off = f'\n<b>تخفیف: {price[1]} درصد</b>' if price[1] and price[0] else ''

    text = (f"<b>❋ بسته انتخابی شامل مشخصات زیر میباشد:</b>\n"
            f"\nسرور: {package[0][3]}"
            f"\nدوره زمانی: {package[0][5]} روز"
            f"\nترافیک (حجم): {package[0][6]} گیگابایت"
            f"\nحداکثر کاربر مجاز: ♾️"
            f"\n<b>قیمت: {price[0]:,} تومان</b>"
            f"{check_off}"
            f"\n\n<b>⤶ برای پرداخت میتونید یکی از روش های زیر رو استفاده کنید:</b>")

    query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))


def send_clean_for_customer(query, context, id_, max_retries=2):
    create = add_client_bot(id_)
    if create[0]:
        get_client = sqlite_manager.select(table='Purchased', where=f'id = {id_}')
        try:
            get_product = sqlite_manager.select(column='price,domain,server_domain,inbound_host,inbound_header_type', table='Product', where=f'id = {get_client[0][6]}')
            get_user_detail = sqlite_manager.select(column='invited_by', table='User', where=f'chat_id={get_client[0][4]}')

            get_domain = get_product[0][1]
            get_server_domain = get_product[0][2]
            inbound_host = get_product[0][3]
            inbound_header_type = get_product[0][4]

            returned = api_operation.get_client_url(client_email=get_client[0][9], inbound_id=get_client[0][7],
                                                    domain=get_domain, server_domain=get_server_domain, host=inbound_host,
                                                    header_type=inbound_header_type)
            if returned:
                returned_copy = f'`{returned}`'
                qr_code = qrcode.make(returned)
                qr_image = qr_code.get_image()
                buffer = BytesIO()
                qr_image.save(buffer, format='PNG')
                binary_data = buffer.getvalue()
                keyboard = [[InlineKeyboardButton("دریافت فایل سرویس", callback_data=f"create_txt_file_{id_}"),
                             InlineKeyboardButton("🎛 سرویس های من", callback_data=f"my_service")],
                            [InlineKeyboardButton("صفحه اصلی ربات ↵", callback_data=f"main_menu_in_new_message")]]
                context.user_data['v2ray_client'] = returned

                context.bot.send_photo(photo=binary_data,
                                       caption=f' سرویس شما با موفقیت فعال شد✅\n\n*• میتونید جزئیات سرویس رو از بخش "سرویس های من" مشاهده کنید.\n\n✪ لطفا سرویس رو به صورت مستقیم از طریق پیام رسان های ایرانی یا پیامک ارسال نکنید، با کلیک روی گزینه "دریافت فایل" سرویس را به صورت فایل یا کیوآرکد ارسال کنید.* \n\n\nلینک:\n{returned_copy}',
                                       chat_id=get_client[0][4], reply_markup=InlineKeyboardMarkup(keyboard),
                                       parse_mode='markdown')

                price = ranking_manage.discount_calculation(direct_price=get_product[0][0], user_id=get_client[0][4])

                record_operation_in_file(chat_id=get_client[0][4], price=price,
                                         name_of_operation=f'خرید سرویس {get_client[0][9]}', operation=0,
                                         status_of_pay=1, context=context)

                send_service_to_customer_report(context, status=1, chat_id=get_client[0][4],
                                                service_name=get_client[0][9])

                invite_chat_id = get_user_detail[0][0]
                subcategory_auto(context, invite_chat_id, price)

                return {'success': True, 'msg': 'config created successfull', 'purchased_id': id_}
            else:
                send_service_to_customer_report(context, status=0, chat_id=get_client[0][4],
                                                service_name=get_client[0][9],
                                                more_detail=create)
                return {'success': False, 'msg': returned}

        except Exception as e:
            send_service_to_customer_report(context, status=0, chat_id=get_client[0][4], service_name=get_client[0][9],
                                            more_detail='ERROR IN SEND CLEAN FOR CUSTOMER', error=e)
            return {'success': False, 'msg': str(e)}

    elif not create[0] and create[2] == 'service do not create':
        send_service_to_customer_report(context, status=0, chat_id=None, service_name=None,
                                        more_detail=f'SERVICE DONT CREATED SUCCESSFULL AND TRY ONE MORE TIME (SEND CLEAN FOR CUSTOMER)\n{create}')
        if max_retries > 0:
            return send_clean_for_customer(query, context, id_, max_retries - 1)
        else:
            return {'success': False, 'msg': 'Maximum retries exceeded'}

    else:
        send_service_to_customer_report(context, status=0, chat_id=None, service_name=None,
                                        more_detail=f'EEROR IN ADD CLIENT (SEND CLEAN FOR CUSTOMER)\n{create}')
        return Exception(f'Error: {create}')


@handle_telegram_exceptions
def apply_card_pay(update, context):
    query = update.callback_query
    if 'accept_card_pay_' in query.data or 'refuse_card_pay_' in query.data:
        status = query.data.replace('card_pay_', '')
        keyboard = [[InlineKeyboardButton("YES", callback_data=f"ok_card_pay_{status}")]
            , [InlineKeyboardButton("NO", callback_data=f"cancel_pay")]]
        query.answer('Confirm Pleas!')
        context.bot.send_message(text='Are You Sure?', reply_markup=InlineKeyboardMarkup(keyboard),
                                 chat_id=ADMIN_CHAT_ID)

    elif 'ok_card_pay_accept_' in query.data:
        id_ = int(query.data.replace('ok_card_pay_accept_', ''))
        send_clean_for_customer(query, context, id_)
        query.delete_message()

    elif 'ok_card_pay_refuse_' in query.data:
        id_ = int(query.data.replace('ok_card_pay_refuse_', ''))
        get_client = sqlite_manager.select(table='Purchased', where=f'id = {id_}')
        context.bot.send_message(
            text=f'متاسفانه درخواست شما برای ثبت سرویس پذیرفته نشد❌\n ارتباط با پشتیبانی: \n @Fupport ',
            chat_id=get_client[0][4])
        query.answer('Done ✅')
        query.delete_message()
        record_operation_in_file(chat_id=get_client[0][4], price=0,
                                 name_of_operation=f'خرید سرویس {get_client[0][9]}', operation=0,
                                 status_of_pay=0, context=context)

    elif 'cancel_pay' in query.data:
        query.answer('Done ✅')
        query.delete_message()


@handle_telegram_exceptions
def my_service(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    number_in_page = 10
    data = query.data.replace('my_service', '')

    check = f'chat_id = {chat_id} and active = 1'

    if chat_id in ranking_manage.list_of_partner:
        check = f'chat_id = {chat_id}'

    get_limit = int(data) if data else number_in_page
    get_all_purchased = sqlite_manager.select(table='Purchased', where=check)
    get_purchased = get_all_purchased[get_limit - number_in_page:get_limit]

    if get_purchased:
        disable_service = enable_service = all_service = 0

        keyboard = [
            [InlineKeyboardButton(f"{'✅' if ser[11] == 1 else '❌'} {ser[9]}", callback_data=f"view_service_{ser[9]}")]
            for ser in get_purchased]

        for service in get_all_purchased:
            if service[11] == 1:
                enable_service += 1
            else:
                disable_service += 1

            all_service += 1

        if len(get_all_purchased) > number_in_page:
            keyboard_backup = []
            keyboard_backup.append(InlineKeyboardButton("قبل ⤌",
                                                        callback_data=f"my_service{get_limit - number_in_page}")) if get_limit != number_in_page else None
            keyboard_backup.append(
                InlineKeyboardButton(f"صفحه {int(get_limit / number_in_page)}", callback_data="just_for_show"))
            keyboard_backup.append(InlineKeyboardButton("⤍ بعد",
                                                        callback_data=f"my_service{get_limit + number_in_page}")) if get_limit < len(
                get_all_purchased) else None
            keyboard.append(keyboard_backup)

        keyboard.append([InlineKeyboardButton("برگشت ↰", callback_data="main_menu")])
        text = ("<b>برای مشاهده جزئیات، سرویس مورد نظر را انتخاب کنید:"
                f"\n\n• تعداد: {all_service}"
                f"\n• فعال: {enable_service}"
                f"\n• غیرفعال: {disable_service}"
                "</b>")
        try:
            query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
        except telegram.error.BadRequest:
            query.answer('در یک پیام جدید فرستادم!')
            context.bot.send_message(chat_id=chat_id, text=text,
                                     reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
    else:
        keyboard = [[InlineKeyboardButton("آشنایی با سرویس‌ها", callback_data="robots_service_help"),
                     InlineKeyboardButton("🛒 خرید سرویس", callback_data="select_server")],
                    [InlineKeyboardButton("برگشت ↰", callback_data="main_menu")]]
        query.edit_message_text(
            '<b>• درحال حاضر شما صاحب سرویس نیستید\n\nدرمورد سرویس ها مطالعه کنید و یک سرویس بخرید! :</b>',
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')


def server_detail_customer(update, context):
    query = update.callback_query
    email = update.callback_query.data.replace('view_service_', '')
    try:
        get_data = sqlite_manager.select(table='Purchased', where=f'client_email = "{email}"')
        get_server_country = sqlite_manager.select(column='name,server_domain', table='Product',
                                                   where=f'id = {get_data[0][6]}')
        get_server_domain = get_server_country[0][1]
        get_server_country = get_server_country[0][0].replace('سرور ', '')
        extra_text, inbound_id = '', get_data[0][7]


        expiry_month = '♾️'
        total_traffic = '♾️'
        exist_day = '(بدون محدودیت زمانی)'

        ret_conf = api_operation.get_client(email, get_server_domain)

        upload_gb = round(int(ret_conf['obj']['up']) / (1024 ** 3), 2)
        download_gb = round(int(ret_conf['obj']['down']) / (1024 ** 3), 2)
        usage_traffic = round(upload_gb + download_gb, 2)

        change_active, advanced_option_pattern = ('فعال ✅', f'advanced_option_{email}') if ret_conf['obj'][
            'enable'] else ('غیرفعال ❌', 'not_for_depleted_service')

        purchase_date = datetime.strptime(get_data[0][12], "%Y-%m-%d %H:%M:%S.%f%z").replace(tzinfo=None)
        auto_renwal_emoji = 'فعال ✓' if get_data[0][15] else 'غیرفعال ✗'
        auto_renwal = f'\n\n🔄 تمدیدخودکار: {auto_renwal_emoji}'

        keyboard = [
            [InlineKeyboardButton("تمدید و ارتقا ↟", callback_data=f"upgrade_service_customize_{get_data[0][0]}")]]

        # report_status_to_admin(context, chat_id=None, text=ret_conf['obj'])

        if ret_conf['obj']['total'] != 0:
            total_traffic = round(ret_conf['obj']['total'] / (1024 ** 3), 2)

        if int(ret_conf['obj']['expiryTime']) != 0 and int(ret_conf['obj']['total']) != 0:
            expiry_timestamp = ret_conf['obj']['expiryTime'] / 1000
            expiry_date = datetime.fromtimestamp(expiry_timestamp)
            expiry_month = expiry_date.strftime("%Y/%m/%d")
            days_lefts = (expiry_date - datetime.now())
            days_lefts_days = days_lefts.days

            days_left_2 = abs(days_lefts_days)

            if days_left_2 >= 1:
                exist_day = f"({days_left_2} روز {'مانده' if days_lefts_days >= 0 else 'گذشته'})"
            else:
                days_left_2 = abs(int(days_lefts.seconds / 3600))
                exist_day = f"({days_left_2} ساعت {'مانده' if days_left_2 >= 1 else 'گذشته'})"

            context.user_data['period_for_upgrade'] = (expiry_date - purchase_date).days
            context.user_data['traffic_for_upgrade'] = total_traffic
            keyboard = [[InlineKeyboardButton("تمدید و ارتقا ↟", callback_data=f"upgrade_service_customize_{get_data[0][0]}")]]

        elif int(ret_conf['obj']['total']) == 0:
            service_activate_status = 'غیرفعال سازی ⤈' if ret_conf['obj']['enable'] else 'فعال سازی ↟'
            keyboard = [[InlineKeyboardButton(service_activate_status,
                                              callback_data=f"change_infiniti_service_status_{get_data[0][0]}_{ret_conf['obj']['enable']}")]]

        keyboard.append([InlineKeyboardButton("حذف سرویس ⇣", callback_data=f"remove_service_{email}"),
                         InlineKeyboardButton("تازه سازی ↻", callback_data=f"view_service_{email}")])

        keyboard.append([InlineKeyboardButton("گزینه های پیشرفته ⥣",
                                              callback_data=advanced_option_pattern)])  # advanced_option_{email}
        keyboard.append([InlineKeyboardButton("برگشت ↰", callback_data="my_service")])

        text_ = (
            f"<b>اطلاعات سرویس انتخاب شده:</b>"
            f"\n\n🔷 نام سرویس: {email}"
            f"\n💡 وضعیت: {change_active}"
            f"\n🗺 موقعیت سرور: {get_server_country}"
            f"\n📅 تاریخ انقضا: {expiry_month} {exist_day}"
            f"\n\n🔼 آپلود↑: {format_traffic(upload_gb)}"
            f"\n🔽 دانلود↓: {format_traffic(download_gb)}"
            f"\n📊 مصرف کل: {usage_traffic}/{total_traffic}{'GB' if isinstance(total_traffic, float) else ''}"
            f"{auto_renwal}"
            f"\n⏰ تاریخ خرید/تمدید: {purchase_date.strftime('%H:%M:%S | %Y/%m/%d')}"
            f"\n\n🌐 آدرس سرویس:\n <code>{get_data[0][8]}</code>"
            f"\n\n{extra_text}"
        )

        query.edit_message_text(text=text_, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
        sqlite_manager.update({'Purchased': {'status': 1 if ret_conf['obj']['enable'] else 0}},
                              where=f'client_email = "{email}"')

    except TypeError as e:
        keyboard = [
            [InlineKeyboardButton("پشتیبانی", callback_data="guidance")],
            [InlineKeyboardButton("حذف سرویس ⇣", callback_data=f"remove_service_from_db_{email}"),
             InlineKeyboardButton("تازه سازی ⟳", callback_data=f"view_service_{email}")],
            [InlineKeyboardButton("برگشت ↰", callback_data="my_service")]]

        text = ('*متاسفانه مشکلی در دریافت اطلاعات این کانفیگ وجود داشت*'
                '*\n\n• اگر از انقضا این کانفیگ مدتی گذشته، احتمالا از سرور حذف شده ولی هنوز داخل دیتابیس وجود داره *'
                '*\n\n• میتونید سرویس رو پاک کنید، اگر مشکل دیگه ای وجود داره با پشتیبانی در ارتباط باشید*'
                )

        query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='markdown')
        ready_report_problem_to_admin(context, text='SERVICE DETAIL FOR CUSTOMER [EXpiry Time Probably]',
                                      error=e, chat_id=query.message.chat_id, detail=f'Service Email: {email}')

    except Exception as e:
        if "specified new message content and reply markup are exactly the same" in str(e):
            return query.answer('آپدیت نشد، احتمالا اطلاعات تغییری نکرده!')
        keyboard = [
            [InlineKeyboardButton("پشتیبانی", callback_data="guidance")],
            [InlineKeyboardButton("حذف سرویس ⇣", callback_data=f"remove_service_from_db_{email}"),
             InlineKeyboardButton("تازه سازی ⟳", callback_data=f"view_service_{email}")],
            [InlineKeyboardButton("برگشت ↰", callback_data="my_service")]]
        text = ('*متاسفانه مشکلی در دریافت اطلاعات این کانفیگ وجود داشت*'
                '*\n\n• اطلاعات این کانفیگ و مشکل به وجود اومده به ادمین ارسال شد و نتیجه بهتون اعلام میشه *'
                '*\n\n• علت خطا*'
                f'{e}')
        query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='markdown')
        ready_report_problem_to_admin(context, text='SERVICE DETAIL FOR CUSTOMER', error=e,
                                      chat_id=query.message.chat_id,
                                      detail=f'Service Email: {email}')
        query.answer('مشکلی وجود دارد!')


@handle_telegram_exceptions
def remove_service_from_db(update, context):
    query = update.callback_query
    email = query.data.replace('remove_service_from_db_', '')
    sqlite_manager.delete({'Purchased': ['client_email', email]})
    text = '<b>سرویس با موفقیت حذف شد ✅</b>'
    keyboard = [[InlineKeyboardButton("برگشت ⤶", callback_data="main_menu")]]
    query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')

@handle_telegram_exceptions
def personalization_service_lu(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id

    if 'upgrade_service_customize_' in query.data:
        service_id = int(query.data.replace('upgrade_service_customize_', ''))

        check_service_exist = sqlite_manager.select(table='Purchased', where=f'id = {service_id}')
        if not check_service_exist:
            query.answer('سرویس مورد نظر دیگر وجود ندارد!')
            return

        if 'period_for_upgrade' in context.user_data and 'traffic_for_upgrade' in context.user_data:
            period_for_upgrade = context.user_data['period_for_upgrade']
            traffic_for_upgrade = context.user_data['traffic_for_upgrade']

            sqlite_manager.update({'User': {'period': int(period_for_upgrade), 'traffic': int(traffic_for_upgrade)}},
                                  where=f'chat_id = {query.message.chat_id}')

        context.user_data['personalization_client_lu_id'] = service_id

    try:
        id_ = context.user_data['personalization_client_lu_id']
    except KeyError:
        query.answer('عملیات منقضی شده است، لطفا از اول تلاش کنید.')
        return
    except Exception as e:
        raise e

    get_data_from_db = sqlite_manager.select(table='User', where=f'chat_id = {query.message.chat_id}')

    traffic = max(abs(get_data_from_db[0][5]), 1)
    period = max(abs(get_data_from_db[0][6]), 1)

    if 'traffic_low_lu_' in query.data:
        traffic_t = int(query.data.replace('traffic_low_lu_', ''))
        traffic = traffic - traffic_t
        traffic = traffic if traffic >= 1 else 1
    elif 'traffic_high_lu_' in query.data:
        traffic_t = int(query.data.replace('traffic_high_lu_', ''))
        traffic = traffic + traffic_t
        traffic = traffic if traffic <= 500 else 500
    elif 'period_low_lu_' in query.data:
        period_t = int(query.data.replace('period_low_lu_', ''))
        period = period - period_t
        period = period if period >= 1 else 1
    elif 'period_high_lu_' in query.data:
        period_t = int(query.data.replace('period_high_lu_', ''))
        period = period + period_t
        period = period if period <= 500 else 500

    sqlite_manager.update({'User': {'traffic': traffic, 'period': period}}, where=f'chat_id = {chat_id}')

    price = ranking_manage.discount_calculation(chat_id, traffic, period, more_detail=True)
    check_off = f'\n<b>تخفیف: {price[1]} درصد</b>' if price[1] else ''

    text = (f'<b>• تو این بخش میتونید سرویس مورد نظر خودتون رو تمدید کنید و یا ارتقا دهید:</b>'
            f'\n<b>نکته: اگر سرویس شما به اتمام نرسیده، مشخصات زیر به سرویس اضافه میشن.</b>'
            f'\n\nحجم سرویس: {traffic}GB'
            f'\nدوره زمانی: {period} روز'
            f'\n<b>قیمت: {price[0]:,}</b>'
            f'\n{check_off}')


    keyboard = [
        [InlineKeyboardButton("«", callback_data="traffic_low_lu_10"),
         InlineKeyboardButton("‹", callback_data="traffic_low_lu_1"),
         InlineKeyboardButton(f"{traffic}GB", callback_data="just_for_show"),
         InlineKeyboardButton("›", callback_data="traffic_high_lu_1"),
         InlineKeyboardButton("»", callback_data="traffic_high_lu_10")],
        [InlineKeyboardButton("«", callback_data="period_low_lu_10"),
         InlineKeyboardButton("‹", callback_data="period_low_lu_1"),
         InlineKeyboardButton(f"{period}Day", callback_data="just_for_show"),
         InlineKeyboardButton("›", callback_data="period_high_lu_1"),
         InlineKeyboardButton("»", callback_data="period_high_lu_10")],
        [InlineKeyboardButton("✓ تایید", callback_data=f"service_upgrade_{id_}")],
        [InlineKeyboardButton("برگشت ↰", callback_data="my_service")]
    ]
    query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))


@handle_telegram_exceptions
def payment_page_upgrade(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    id_ = int(query.data.replace('service_upgrade_', ''))
    package = sqlite_manager.select(table='User', where=f'chat_id = {chat_id}')

    keyboard = [
        [InlineKeyboardButton("درگاه پرداخت بانکی", callback_data=f"zarinpall_page_upgrade_{id_}")],
        [InlineKeyboardButton("پرداخت از کیف پول", callback_data=f'payment_by_wallet_upgrade_service_{id_}'),
         InlineKeyboardButton("پرداخت با کریپتو", callback_data=f"cryptomus_page_upgrade_{id_}")],
        [InlineKeyboardButton("برگشت ↰", callback_data="my_service")]
    ]

    # [InlineKeyboardButton("کارت به کارت", callback_data=f'upg_ser_by_card{id_}')],

    price = ranking_manage.discount_calculation(chat_id, package[0][5], package[0][6], more_detail=True)
    check_off = f'\n<b>تخفیف: {price[1]} درصد</b>' if price[1] else ''

    text = (f"<b>❋ بسته انتخابی شامل مشخصات زیر میباشد:</b>\n"
            f"\nدوره زمانی: {package[0][6]} روز"
            f"\nترافیک (حجم): {package[0][5]} گیگابایت"
            f"\nحداکثر کاربر مجاز: ♾️"
            f"\n<b>قیمت: {price[0]:,} تومان</b>"
            f"\n{check_off}"
            f"\n\nموجودی کیف پول: {int(package[0][10]):,}"
            f"\n\n<b>⤶ برای پرداخت میتونید یکی از روش های زیر رو استفاده کنید:</b>")
    query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))


@handle_telegram_conversetion_exceptions
def pay_page_get_evidence_for_upgrade(update, context):
    query = update.callback_query
    id_ = int(query.data.replace('upg_ser_by_card', ''))
    chat_id = query.message.chat_id

    package = sqlite_manager.select(table='User', where=f'chat_id = {chat_id}')
    context.user_data['package'] = package
    context.user_data['purchased_id'] = id_
    keyboard = [[InlineKeyboardButton("صفحه اصلی ⤶", callback_data="send_main_message")]]

    price = ranking_manage.discount_calculation(chat_id, package[0][5], package[0][6], more_detail=True)
    check_off = f'\n*تخفیف: {price[1]} درصد*' if price[1] else ''

    text = (f"\n\nمدت اعتبار فاکتور: 10 دقیقه"
            f"\nسرویس: {package[0][6]} روز - {package[0][5]} گیگابایت"
            f"\n*قیمت*: `{price[0]:,}`* تومان *"
            f"\n{check_off}"
            f"\n\n*• لطفا مبلغ رو به شماره‌حساب زیر واریز کنید و اسکرین‌شات یا شماره‌پیگیری رو بعد از همین پیام ارسال کنید، اطمینان حاصل کنید ربات درخواست رو ثبت کنه.*"
            f"\n\n`6219861938619417` - امیرحسین نجفی"
            f"\n\n*• بعد از تایید شدن پرداخت، سرویس برای شما ارسال میشه، زمان تقریبی 5 دقیقه الی 3 ساعت.*")

    context.bot.send_message(chat_id=query.message.chat_id, text=text, parse_mode='markdown',
                             reply_markup=InlineKeyboardMarkup(keyboard))
    query.answer('فاکتور برای شما ارسال شد.')
    return GET_EVIDENCE


@handle_telegram_conversetion_exceptions
def send_evidence_to_admin_for_upgrade(update, context):
    user = update.message.from_user

    package = context.user_data['package']
    price = ranking_manage.discount_calculation(user_id=user['id'], traffic=package[0][5], period=package[0][6])

    purchased_id = context.user_data['purchased_id']

    if not ranking_manage.enough_rank('GET_SERVICE_WITHOUT_CONFIRM', user['id']):
        keyboard = [[InlineKeyboardButton("Accept ✅", callback_data=f"accept_card_pay_lu_{purchased_id}"),
                     InlineKeyboardButton("Refuse ❌", callback_data=f"refuse_card_pay_lu_{purchased_id}")],
                    [InlineKeyboardButton("Hide buttons", callback_data=f"hide_buttons")]]
        text_ = f'<b>درخواست شما با موفقیت ثبت شد✅\nنتیجه از طریق همین ربات بهتون اعلام میشه</b>'
        text = "- Check the new payment to the card [UPGRADE SERVICE]:\n\n"

    else:
        try:
            task.upgrade_service(context, purchased_id)
            keyboard = []
            text_ = f'سرویس با موفقیت ارتقا یافت✅'
            text = '- The user rank was sufficient to get the service without confirm [UPGRADE SERVICE]\n\n'
        except Exception as e:
            text = 'مشکلی وجود داشت!'
            ready_report_problem_to_admin(context, text, chat_id=user.id, error=e)
            raise e

    text += f"Name: {user['first_name']}\nUserName: @{user['username']}\nID: {user['id']}\n\n"
    service_detail = f"\n\nPeriod: {package[0][6]} Day\nTraffic: {package[0][5]}GB\nPrice: {price:,} T"

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        text += f"caption: {update.message.caption}" or 'Witout caption!'
        text += service_detail
        context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=file_id, caption=text,
                               reply_markup=InlineKeyboardMarkup(keyboard))
        update.message.reply_text(text_, parse_mode='html')

    elif update.message.text:
        text += f"Text: {update.message.text}{service_detail}"
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, reply_markup=InlineKeyboardMarkup(keyboard))
        update.message.reply_text(text_, parse_mode='html')

    else:
        update.message.reply_text('مشکلی وجود داره!')

    context.user_data.clear()
    return ConversationHandler.END


upgrade_service_by_card_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(pay_page_get_evidence_for_upgrade, pattern=r'upg_ser_by_card\d+')],
    states={
        GET_EVIDENCE_PER: [MessageHandler(Filters.all, send_evidence_to_admin_for_upgrade)]
    },
    fallbacks=[],
    conversation_timeout=1000,
    per_chat=True,
    allow_reentry=True
)


@handle_telegram_exceptions
def apply_card_pay_lu(update, context):
    query = update.callback_query
    if 'accept_card_pay_lu_' in query.data or 'refuse_card_pay_lu_' in query.data:
        status = query.data.replace('card_pay_lu_', '')
        keyboard = [[InlineKeyboardButton("YES", callback_data=f"ok_card_pay_lu_{status}")]
            , [InlineKeyboardButton("NO", callback_data=f"cancel_pay")]]
        query.answer('Confirm Pleas!')
        context.bot.send_message(text='Are You Sure?', reply_markup=InlineKeyboardMarkup(keyboard),
                                 chat_id=ADMIN_CHAT_ID)
    elif 'ok_card_pay_lu_accept_' in query.data:
        id_ = int(query.data.replace('ok_card_pay_lu_accept_', ''))
        upgrade_service = task.upgrade_service(context, id_)
        context.bot.send_message(text='سفارش شما برای تمدید و یا ارتقا با موفقیت تایید شد ✅',
                                 chat_id=upgrade_service[0])
        query.answer('Done ✅')
        query.delete_message()

    elif 'ok_card_pay_lu_refuse_' in query.data:
        id_ = int(query.data.replace('ok_card_pay_lu_refuse_', ''))
        get_client = sqlite_manager.select(table='Purchased', where=f'id = {id_}')

        keyboard = [[InlineKeyboardButton("پشتیبانی", url="@Fupport")]]

        context.bot.send_message(
            text='درخواست شما برای سفارش یا ارتقا سرویس تایید نشد!\nاگر فکر میکنید خطایی رخ داده با پشتیبانی در ارتباط باشید:',
            chat_id=get_client[0][4], reply_markup=InlineKeyboardMarkup(keyboard))
        query.answer('Done ✅')
        query.delete_message()

        record_operation_in_file(chat_id=get_client[0][4], price=0,
                                 name_of_operation=f'تمدید یا ارتقا سرویس {get_client[0][9]}', operation=0,
                                 status_of_pay=0, context=context)

    elif 'cancel_pay' in query.data:
        query.answer('Done ✅')
        query.delete_message()


@handle_telegram_exceptions
def get_free_service(update, context):
    query = update.callback_query
    user = query.from_user

    sqlite_manager.update({'User': {'free_service': 1}}, where=f"chat_id = {user['id']}")
    ex = sqlite_manager.insert('Purchased', rows=
    {'active': 1, 'status': 1, 'name': init_name(user["first_name"]), 'user_name': user["username"],
     'chat_id': int(user["id"]), 'product_id': 1, 'inbound_id': 1, 'date': datetime.now(),
     'notif_day': 0, 'notif_gb': 0})

    send_clean_for_customer(update.callback_query, context, ex)
    context.bot.send_message(ADMIN_CHAT_ID, f'🟢 User {user["name"]} With ID: {user["id"]} TAKE A FREE SERVICE')
    keyboard = [[InlineKeyboardButton("برگشت ⤶", callback_data="main_menu")]]
    query.edit_message_text('سرویس تست با موفقیت برای شما ارسال شد ✅', reply_markup=InlineKeyboardMarkup(keyboard))


@handle_telegram_exceptions
def guidance(update, context):
    query = update.callback_query
    text = ("<b>📚 به بخش راهنمای ربات خوش آمدید!"
            f"\n\n• آیدی شما: </b><code>{query.message.chat_id}</code>")
    keyboard = [
        [InlineKeyboardButton("اپلیکیشن‌های مناسب برای اتصال", callback_data=f"apps_help")],
        [InlineKeyboardButton("• سوالات متداول", callback_data=f"people_ask_help"),
         InlineKeyboardButton("آشنایی با سرویس‌ها", callback_data=f"robots_service_help")],
        [InlineKeyboardButton("شخصی‌سازی و ویژگی‌های ربات", callback_data=f"personalize_help")],
        [InlineKeyboardButton("• گزارش مشکل", callback_data=f"report_problem_by_user"),
         InlineKeyboardButton("اضافه کردن تیکت", callback_data=f"get_ticket_priority")],
        [InlineKeyboardButton("برگشت ⤶", callback_data="main_menu")]
    ]
    query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')


@handle_telegram_exceptions
def show_help(update, context):
    query = update.callback_query
    help_what = query.data.replace('_help', '')
    if help_what == 'apps':
        text = "<b>همه لینک ها، از صفحات رسمی نرم افزارها هستند. \nو نسخه مرتبط با دستگاه خودتان را دانلود کنید.</b>"
        keyboard = [
            [InlineKeyboardButton("V2RayNG",
                                  url="https://play.google.com/store/apps/details?id=com.v2ray.ang&hl=en&gl=US"),
             InlineKeyboardButton("اندروید:", callback_data="just_for_show")],
            [InlineKeyboardButton("V2Box", url="https://apps.apple.com/us/app/v2box-v2ray-client/id6446814690"),
             InlineKeyboardButton("آیفون و مک:", callback_data="just_for_show")],
            [InlineKeyboardButton("V2RayN (core)", url="https://github.com/2dust/v2rayN/releases"),
             InlineKeyboardButton("ویندوز:", callback_data="just_for_show")],
            [InlineKeyboardButton("برگشت ⤶", callback_data="guidance")]
        ]


@handle_telegram_exceptions_without_user_side
def disable_service_in_data_base(context, list_of_notification, user, not_enogh_credit=False):
    text = ("🔴 اطلاع رسانی اتمام سرویس"
            f"\nدرود {list_of_notification[0][3]} عزیز، سرویس شما با نام {user[2]} به پایان رسید!"
            f"\nدر صورتی که تمایل دارید نسبت به بررسی و یا تمدید سرویس اقدام کنید.")

    if not_enogh_credit:
        text = ("🔴 اطلاع رسانی اتمام سرویس و تمدید خودکار ناموفق"
                f"\nدرود {list_of_notification[0][3]} عزیز، سرویس شما با نام {user[2]} به پایان رسید!"
                f"\nاعتبار شما برای تمدید خودکار سرویس کافی نبود!")

    keyboard = [
        [InlineKeyboardButton("خرید سرویس جدید", callback_data=f"select_server"),
         InlineKeyboardButton("تمدید همین سرویس", callback_data=f"upgrade_service_customize_{user[0]}")]
    ]

    # if user[1] not in rate_list:
    #     keyboard.extend([[InlineKeyboardButton("❤️ تجربه استفاده از فری‌بایت رو به اشتراک بگذارید:", callback_data=f"just_for_show")],
    #                     [InlineKeyboardButton("معمولی بود", callback_data=f"rate_ok&{list_of_notification[0][0]}_{user[0]}"),
    #                      InlineKeyboardButton("عالی بود", callback_data=f"rate_perfect&{list_of_notification[0][0]}_{user[0]}")],
    #                     [InlineKeyboardButton("ناامید شدم", callback_data=f"rate_bad&{list_of_notification[0][0]}_{user[0]}"),
    #                      InlineKeyboardButton("نظری ندارم", callback_data=f"rate_haveNotIdea&{list_of_notification[0][0]}_{user[0]}")]])
    #     rate_list.append(user[1])

    sqlite_manager.update({'Purchased': {'status': 0}}, where=f'id = {user[0]}')

    utilities.report_status_to_admin(context, text=f'The user service has ended.\n'
                                                   f'User Name: {list_of_notification[0][3]}'
                                                   f'\nService id: {user[0]}', chat_id=list_of_notification[0][0])

    context.bot.send_message(user[1], text=text, reply_markup=InlineKeyboardMarkup(keyboard))


@handle_telegram_exceptions_without_user_side
def check_all_configs(context, context_2=None):
    if context_2:
        context = context_2

    get_all = api_operation.get_all_inbounds()
    get_from_db = sqlite_manager.select(
        column='id,chat_id,client_email,status,date,notif_day,notif_gb,auto_renewal,product_id,inbound_id,client_id',
        table='Purchased', where='active=1')
    get_users_notif = sqlite_manager.select(column='chat_id,notification_gb,notification_day,name,traffic,period,wallet', table='User')

    for server in get_all:
        for config in server['obj']:
            for client in config['clientStats']:
                for user in get_from_db:
                    if user[2] == client['email']:
                        list_of_notification = [notif for notif in get_users_notif if notif[0] == user[1]]

                        if not client['enable'] and user[3] and client['total']:
                            if not user[7]:
                                disable_service_in_data_base(context, list_of_notification, user)
                            else:
                                traffic = client['total'] * 2
                                expiry_timestamp = client['expiryTime']
                                expiry_datetime = datetime.fromtimestamp(expiry_timestamp / 1000)
                                new_expiry_datetime = (expiry_datetime - datetime.strptime(user[4].split('+')[0], "%Y-%m-%d %H:%M:%S.%f")).days
                                period = datetime.now(pytz.timezone('Asia/Tehran')) + timedelta(
                                    days=new_expiry_datetime)
                                my_data = int(period.timestamp() * 1000)
                                price = ranking_manage.discount_calculation(list_of_notification[0][0],
                                                                            admin_task.traffic_to_gb(client['total']),
                                                                            new_expiry_datetime)

                                if list_of_notification[0][6] >= price:
                                    get_server_domain = sqlite_manager.select(column='server_domain', table='Product',
                                                                              where=f'id = {user[8]}')

                                    text = ("🟢 اطلاع رسانی اتمام سرویس و تمدید خودکار"
                                            f"\nدرود {list_of_notification[0][3]} عزیز، سرویس شما با نام {user[2]} به پایان رسید!"
                                            f"\nسرویس شما به صورت خودکار تمدید شد، میتونید جزئیات سرویس رو بررسی کنید.")
                                    keyboard = [[InlineKeyboardButton("مشاهده جزئیات سرویس",
                                                                      callback_data=f"view_service_{user[2]}")]]

                                    print(api_operation.reset_client_traffic(user[9], user[2], get_server_domain[0][0]))

                                    data = {
                                        "id": int(user[9]),
                                        "settings": "{{\"clients\":[{{\"id\":\"{0}\",\"alterId\":0,"
                                                    "\"email\":\"{1}\",\"limitIp\":0,\"totalGB\":{2},\"expiryTime\":{3},"
                                                    "\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}}]}}".format(
                                            user[10], user[2], traffic, my_data)}


                                    wallet_manage.less_from_wallet(list_of_notification[0][0], price)

                                    sqlite_manager.update({'Purchased': {'date': datetime.now(
                                        pytz.timezone('Asia/Tehran')), 'notif_day': 0, 'notif_gb': 0}}
                                        , where=f'client_email = "{user[2]}"')

                                    context.bot.send_message(text=text, chat_id=list_of_notification[0][0],
                                                             reply_markup=InlineKeyboardMarkup(keyboard),
                                                             parse_mode='html')

                                    record_operation_in_file(chat_id=list_of_notification[0][0], price=price,
                                                             name_of_operation=f'تمدید یا ارتقا سرویس {user[2]}',
                                                             operation=0,
                                                             status_of_pay=1, context=context)

                                    report_status_to_admin(context,
                                                           text=f'User Upgrade Service automate\nService Name: {user[2]}',
                                                           chat_id=list_of_notification[0][0])
                                else:
                                    disable_service_in_data_base(context, list_of_notification, user,
                                                                 not_enogh_credit=True)


                        elif client['enable'] and not user[3]:
                            sqlite_manager.update(
                                {'Purchased': {'status': 1, 'date': datetime.now(pytz.timezone('Asia/Tehran')),
                                               'notif_day': 0, 'notif_gb': 0}}
                                , where=f'id = "{user[0]}"')

                        if client['expiryTime'] and client['total']:
                            expiry = second_to_ms(client['expiryTime'], False)
                            now = datetime.now(pytz.timezone('Asia/Tehran')).replace(tzinfo=None)
                            time_left = (expiry - now).days

                            upload_gb = client['up'] / (1024 ** 3)
                            download_gb = client['down'] / (1024 ** 3)
                            usage_traffic = upload_gb + download_gb
                            total_traffic = client['total'] / (1024 ** 3)
                            traffic_percent = (usage_traffic / total_traffic) * 100
                            traffic_left = round((total_traffic - usage_traffic), 2)

                            keyboard = [
                                [InlineKeyboardButton("مشاهده جزئیات سرویس", callback_data=f"view_service_{user[2]}"),
                                 InlineKeyboardButton("تمدید یا ارتقا سرویس", callback_data=f"upgrade_service_customize_{user[0]}")]
                            ]

                            if not user[5] and time_left <= list_of_notification[0][2]:
                                text = ("🔵 اطلاع رسانی تاریخ انقضا سرویس"
                                        f"\nدرود {list_of_notification[0][3]} عزیز، از سرویس شما با نام {user[2]} کمتر از {int(time_left) + 1} روز باقی مونده."
                                        f"\nدر صورتی که تمایل دارید نسبت به بررسی و یا تمدید سرویس اقدام کنید.")
                                sqlite_manager.update({'Purchased': {'notif_day': 1}}, where=f'id = "{user[0]}"')
                                context.bot.send_message(user[1], text=text,
                                                         reply_markup=InlineKeyboardMarkup(keyboard))

                            if not user[6] and traffic_percent >= list_of_notification[0][1]:
                                text = ("🔵 اطلاع رسانی حجم سرویس"
                                        f"\nدرود {list_of_notification[0][3]} عزیز، شما {int(traffic_percent)} درصد حجم ترافیک سرویس {user[2]} رو مصرف کردید، "
                                        f"\nحجم باقی مونده از سرویس {format_traffic(traffic_left)} است. "
                                        f"\nدر صورتی که تمایل دارید نسبت به بررسی و یا تمدید سرویس اقدام کنید.")
                                sqlite_manager.update({'Purchased': {'notif_gb': 1}}, where=f'id = "{user[0]}"')
                                context.bot.send_message(user[1], text=text,
                                                         reply_markup=InlineKeyboardMarkup(keyboard))

@handle_telegram_exceptions
def setting(update, context):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("نوتیفیکیشن سرویس", callback_data="service_notification"),
         InlineKeyboardButton("نوتیفیکیشن کیف‌پول", callback_data="wallet_notification")],
        [InlineKeyboardButton("زیرمجموعه گیری", callback_data=f'subcategory')],
        [InlineKeyboardButton("برگشت ↰", callback_data="main_menu")]
    ]
    query.edit_message_text(text='*در این قسمت میتونید تنظیمات ربات رو مشاهده و یا شخصی سازی کنید:*',
                            parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))


def change_notif(update, context):
    query = update.callback_query
    get_data_from_db = sqlite_manager.select(table='User', where=f'chat_id = {query.message.chat_id}')
    text, keyboard = None, None

    try:
        traffic = abs(get_data_from_db[0][8])
        period = abs(get_data_from_db[0][9])
        wallet_notif = abs(get_data_from_db[0][11])

        if 'notif_traffic_low_' in query.data:
            traffic_t = int(query.data.replace('notif_traffic_low_', ''))
            traffic = traffic - traffic_t
            traffic = traffic if traffic >= 1 else 5
        elif 'notif_traffic_high_' in query.data:
            traffic_t = int(query.data.replace('notif_traffic_high_', ''))
            traffic = traffic + traffic_t
            traffic = traffic if traffic <= 100 else 100

        elif 'notif_day_low_' in query.data:
            period_t = int(query.data.replace('notif_day_low_', ''))
            period = period - period_t
            period = period if period >= 1 else 1
        elif 'notif_day_high_' in query.data:
            period_t = int(query.data.replace('notif_day_high_', ''))
            period = period + period_t
            period = period if period <= 100 else 100

        elif 'notif_wallet_low_' in query.data:
            wallet_t = int(query.data.replace('notif_wallet_low_', ''))
            wallet_notif = wallet_notif - wallet_t
            wallet_notif = wallet_notif if wallet_notif >= 1_000 else 5_000
        elif 'notif_wallet_high_' in query.data:
            wallet_t = int(query.data.replace('notif_wallet_high_', ''))
            wallet_notif = wallet_notif + wallet_t
            wallet_notif = wallet_notif if wallet_notif <= 1_000_000 else 1_000_000

        sqlite_manager.update({'User': {'notification_gb': traffic, 'notification_day': period,
                                        'notification_wallet': wallet_notif}},
                              where=f'chat_id = {query.message.chat_id}')

        if any(query.data.startswith(prefix) for prefix in
               ['service_notification', 'notif_traffic_low_', 'notif_traffic_high_', 'notif_day_low_',
                'notif_day_high_']):

            keyboard = [
                [InlineKeyboardButton("«", callback_data="notif_traffic_low_5"),
                 InlineKeyboardButton(f"{traffic}%", callback_data="just_for_show"),
                 InlineKeyboardButton("»", callback_data="notif_traffic_high_5")],
                [InlineKeyboardButton("«", callback_data="notif_day_low_1"),
                 InlineKeyboardButton(f"{period} Day", callback_data="just_for_show"),
                 InlineKeyboardButton("»", callback_data="notif_day_high_1")],
                [InlineKeyboardButton("برگشت ↰", callback_data="setting")]
            ]

            text = ('*• مشخص کنید چه زمانی نوتیفیکیشن های مربوط به سرویس هارو دریافت کنید:*'
                    f'\n\nدریافت اعلان بعد مصرف {traffic}% حجم'
                    f'\nدریافت اعلان {period} روز قبل تمام شدن سرویس')

        elif any(query.data.startswith(call) for call in
                 ['wallet_notification', 'notif_wallet_low_', 'notif_wallet_high_']):
            keyboard = [
                [InlineKeyboardButton("«", callback_data="notif_wallet_low_5000"),
                 InlineKeyboardButton(f"{wallet_notif:,} تومان", callback_data="just_for_show"),
                 InlineKeyboardButton("»", callback_data="notif_wallet_high_5000")],
                [InlineKeyboardButton("برگشت ↰", callback_data="setting")]
            ]

            text = ('*• مشخص کنید چه زمانی نوتیفیکیشن مربوط به کیف پول رو دریافت کنید:*'
                    f'\n\nدریافت اعلان با رسیدن اعتبار به {wallet_notif:,} تومان')

        query.edit_message_text(text=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    except Exception as e:
        if 'specified new message content and reply markup are exactly the same' in str(e):
            query.answer('شما نمیتونید ولوم رو کمتر یا بیشتر از مقدار مجاز قرار بدید!')
        else:
            query.answer('مشکلی وجود داشت!')

@handle_telegram_conversetion_exceptions
def pay_by_card_for_credit(update, context):
    query = update.callback_query
    id_ = int(query.data.replace('pay_by_card_for_credit_', ''))
    package = sqlite_manager.select(column='value', table='Credit_History', where=f'id = {id_}')
    context.user_data['credit_package'] = package
    context.user_data['credit_id'] = id_
    keyboard = [[InlineKeyboardButton("صفحه اصلی ⤶", callback_data="send_main_message")]]

    price = ranking_manage.discount_calculation(query.message.chat_id, direct_price=package[0][0], without_off=True)

    text = (f"\n\nمدت اعتبار فاکتور: 10 دقیقه"
            f"\n*قیمت*: `{price:,}`* تومان *"
            f"\n\n*• لطفا مبلغ رو به شماره‌حساب زیر واریز کنید و اسکرین‌شات یا شماره‌پیگیری رو بعد از همین پیام ارسال کنید، اطمینان حاصل کنید ربات درخواست رو ثبت کنه.*"
            f"\n\n`6219861938619417` - امیرحسین نجفی"
            f"\n\n*• بعد از تایید شدن پرداخت، سرویس برای شما ارسال میشه، زمان تقریبی 5 دقیقه الی 3 ساعت.*")
    context.bot.send_message(chat_id=query.message.chat_id, text=text, parse_mode='markdown',
                             reply_markup=InlineKeyboardMarkup(keyboard))
    query.answer('فاکتور برای شما ارسال شد.')
    return GET_EVIDENCE_CREDIT


@handle_telegram_conversetion_exceptions
def pay_by_card_for_credit_admin(update, context):
    user = update.message.from_user
    package = context.user_data['credit_package']
    credit_id = context.user_data['credit_id']
    price = ranking_manage.discount_calculation(user['id'], direct_price=package[0][0], without_off=True)

    if not ranking_manage.enough_rank('GET_SERVICE_WITHOUT_CONFIRM', user['id']):
        keyboard = [[InlineKeyboardButton("Accept ✅", callback_data=f"accept_card_pay_credit_{credit_id}"),
                     InlineKeyboardButton("Refuse ❌", callback_data=f"refuse_card_pay_credit_{credit_id}")],
                    [InlineKeyboardButton("Hide buttons", callback_data=f"hide_buttons")]]
        text_ = f'<b>درخواست شما با موفقیت ثبت شد✅\nنتیجه از طریق همین ربات بهتون اعلام میشه</b>'
        text = "- Check the new payment to the card [CHARGE CREDIT WALLET]:\n\n"

    else:
        add_credit_to_wallet(context, credit_id)
        keyboard = []
        text_ = f'کیف پول شما با موفقیت شارژ شد✅'
        text = '- The user rank was sufficient to get the service without confirm [CHARGE CREDIT WALLET]\n\n'

    text += f"Name: {user['first_name']}\nUserName: @{user['username']}\nID: {user['id']}\n\n"

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        text += f"caption: {update.message.caption}" or 'Witout caption!'
        text += f"\n\nPrice: {price:,} T"
        context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=file_id, caption=text,
                               reply_markup=InlineKeyboardMarkup(keyboard))
        update.message.reply_text(text_, parse_mode='html')
    elif update.message.text:
        text += f"Text: {update.message.text}\n\nPrice: {price:,} T"
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, reply_markup=InlineKeyboardMarkup(keyboard))
        update.message.reply_text(text_, parse_mode='html')
    else:
        update.message.reply_text('مشکلی وجود داره!')

    context.user_data.clear()
    return ConversationHandler.END


credit_charge = ConversationHandler(
    entry_points=[CallbackQueryHandler(pay_by_card_for_credit, pattern=r'pay_by_card_for_credit_\d+')],
    states={
        GET_EVIDENCE_CREDIT: [MessageHandler(Filters.all, pay_by_card_for_credit_admin)]
    },
    fallbacks=[],
    conversation_timeout=1000,
    per_chat=True,
    allow_reentry=True
)


@handle_telegram_exceptions_without_user_side
def add_credit_to_wallet(context, id_):
    get_credit = sqlite_manager.select(column='chat_id,value', table='Credit_History', where=f'id = {id_}')
    wallet_manage.add_to_wallet(get_credit[0][0], get_credit[0][1])

    sqlite_manager.update({'Credit_History': {'active': 1, 'date': datetime.now(pytz.timezone('Asia/Tehran'))}}
                          , where=f'id = "{id_}"')

    record_operation_in_file(chat_id=get_credit[0][0], price=get_credit[0][1],
                             name_of_operation=f'واریز به کیف پول', operation=1,
                             status_of_pay=1, context=context)

    context.bot.send_message(ADMIN_CHAT_ID, '🟢 WALLET OPERATOIN SUCCESSFULL')
    return get_credit[0][0]


@handle_telegram_exceptions
def apply_card_pay_credit(update, context):
    query = update.callback_query
    if 'accept_card_pay_credit_' in query.data or 'refuse_card_pay_credit_' in query.data:
        status = query.data.replace('card_pay_credit_', '')
        keyboard = [[InlineKeyboardButton("YES", callback_data=f"ok_card_pay_credit_{status}")]
            , [InlineKeyboardButton("NO", callback_data=f"cancel_pay")]]
        query.answer('Confirm Pleas!')
        context.bot.send_message(text='Are You Sure?', reply_markup=InlineKeyboardMarkup(keyboard),
                                 chat_id=ADMIN_CHAT_ID)
    elif 'ok_card_pay_credit_accept_' in query.data:
        id_ = int(query.data.replace('ok_card_pay_credit_accept_', ''))

        return_chat_id = add_credit_to_wallet(context, id_)

        context.bot.send_message(text='سفارش شما برای واریز وجه به کیف پول با موفقیت تایید شد ✅',
                                 chat_id=return_chat_id)
        query.answer('Done ✅')
        query.delete_message()


    elif 'ok_card_pay_credit_refuse_' in query.data:
        id_ = int(query.data.replace('ok_card_pay_credit_refuse_', ''))
        get_credit = sqlite_manager.select(column='chat_id,value', table='Credit_History', where=f'id = {id_}')
        context.bot.send_message(
            text=f'متاسفانه درخواست شما برای واریز به کیف پول پذیرفته نشد❌\n ارتباط با پشتیبانی: \n @Fupport ',
            chat_id=get_credit[0][0])
        query.answer('Done ✅')
        query.delete_message()

        record_operation_in_file(chat_id=get_credit[0][0], price=get_credit[0][1],
                                 name_of_operation=f'واریز به کیف پول', operation=1,
                                 status_of_pay=0, context=context)

        sqlite_manager.delete({'Credit_History': ["id", id_]})
    elif 'cancel_pay' in query.data:
        query.answer('Done ✅')
        query.delete_message()


@handle_telegram_exceptions
def pay_from_wallet(update, context):
    query = update.callback_query
    user = query.from_user
    get_wallet = sqlite_manager.select(table='User', column='wallet', where=f'chat_id = {user["id"]}')

    if 'payment_by_wallet_upgrade_service_' in query.data:
        id_ = query.data.replace('payment_by_wallet_upgrade_service_', '')
        package = sqlite_manager.select(table='User', where=f'chat_id = {query.message.chat_id}')
        context.user_data['package'] = package
        context.user_data['purchased_id'] = id_

        price = ranking_manage.discount_calculation(user['id'], package[0][5], package[0][6])

        keyboard = [[InlineKeyboardButton("تایید و پرداخت ✅", callback_data=f"accept_wallet_upgrade_pay_{id_}")]
                    if get_wallet[0][0] >= price else [
            InlineKeyboardButton("افزایش موجودی ↟", callback_data=f"buy_credit_volume")],
                    [InlineKeyboardButton("برگشت ⤶", callback_data="my_service")]]

        available_or_not = "اطلاعات زیر رو بررسی کنید و در صورت تایید پرداخت رو نهایی کنید:" \
            if get_wallet[0][0] >= price else "متاسفانه موجودی کیف پول شما کافی نیست، میتونید با گزینه افزایش موجودی اعتبار خودتون رو افزایش بدید."

        # price = ranking_manage.discount_calculation(user['id'], package[0][5], package[0][6])

        text = (f"{available_or_not}"
                f"\n\nسرویس: {package[0][6]} روز - {package[0][5]} گیگابایت"
                f"\n*قیمت*: `{price:,}`* تومان *"
                f"\n*موجودی کیف پول*: {get_wallet[0][0]:,}* تومان *"
                f"\n\n• همیشه میتوانید با حذف کردن سرویس در قسمت *سرویس های من*، مبلغ باقی مونده رو به کیف پول خودتون برگردونید"
                f"\n\n• با تایید کردن، سرویس شما ارتقا پیدا میکنه")
        query.edit_message_text(text=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    elif 'accept_wallet_upgrade_pay_' in query.data:
        try:
            id_ = int(query.data.replace('accept_wallet_upgrade_pay_', ''))

            upgrade_serv = task.upgrade_service(context, id_)

            wallet_manage.less_from_wallet(query.from_user['id'], upgrade_serv[1])

            keyboard = [[InlineKeyboardButton("برگشت ⤶", callback_data="my_service")]]
            query.edit_message_text(text='سرویس شما با موفقیت ارتقا یافت.✅', reply_markup=InlineKeyboardMarkup(keyboard))

        except Exception as e:
            ready_report_problem_to_admin(context, 'PAY FROM WAWLLET FOR UPGRADE', query.from_user['id'], e)
            query.answer('مشکلی وجود دارد! گزارش مشکل به ادمین ارسال شد')

    elif 'payment_by_wallet_' in query.data:

        id_ = int(query.data.replace('payment_by_wallet_', ''))

        package = sqlite_manager.select(table='Product', where=f'id = {id_}')
        context.user_data['package'] = package

        price = ranking_manage.discount_calculation(query.from_user['id'], direct_price=package[0][7],
                                                    more_detail=True)

        keyboard = [[InlineKeyboardButton("تایید و پرداخت ✅", callback_data=f"accept_wallet_pay_{id_}")]
                    if get_wallet[0][0] >= price[0] else [InlineKeyboardButton("افزایش موجودی ↟", callback_data=f"buy_credit_volume")],
                    [InlineKeyboardButton("برگشت ⤶", callback_data="select_server")]]

        available_or_not = "اطلاعات زیر رو بررسی کنید و در صورت تایید پرداخت رو نهایی کنید:" \
            if get_wallet[0][0] >= price[
            0] else "متاسفانه موجودی کیف پول شما کافی نیست، میتونید با گزینه افزایش موجودی اعتبار خودتون رو افزایش بدید."

        ex = sqlite_manager.select('id', 'Purchased', where=f'active = 0 and chat_id = {user["id"]}', limit=1)

        if not ex:
            ex = sqlite_manager.insert('Purchased', rows=
            {'active': 0, 'status': 0, 'name': init_name(user["first_name"]), 'user_name': user["username"],
             'chat_id': int(user["id"]), 'product_id': id_, 'notif_day': 0, 'notif_gb': 0})
        else:
            sqlite_manager.update({'Purchased':
                                       {'active': 0, 'status': 0, 'name': init_name(user["first_name"]),
                                        'user_name': user["username"],
                                        'chat_id': int(user["id"]), 'product_id': id_, 'notif_day': 0,
                                        'notif_gb': 0}}, where=f'id = {ex[0][0]}')
            ex = ex[0][0]

        context.user_data['purchased_id'] = ex

        check_off = f'\n*تخفیف: {price[1]} درصد*' if price[1] else ''

        text = (f"{available_or_not}"
                f"\n\nسرویس: {package[0][5]} روز - {package[0][6]} گیگابایت"
                f"\n*قیمت*: {price[0]:,}* تومان *"
                f"{check_off}"
                f"\n*موجودی کیف پول*: {get_wallet[0][0]:,}* تومان *"

                f"\n\n• همیشه میتوانید با حذف کردن سرویس در قسمت *سرویس های من*، مبلغ باقی مونده رو به کیف پول خودتون برگردونید"
                f"\n\n• با تایید کردن، سرور مستقیم برای شما فعال میشه")
        query.edit_message_text(text=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    elif 'accept_wallet_pay_' in query.data:
        get_p_id = context.user_data['purchased_id']
        check = send_clean_for_customer(query, context, get_p_id)

        if check['success']:
            get_db = context.user_data['package'][0][7]

            price = ranking_manage.discount_calculation(query.from_user['id'], direct_price=get_db)

            wallet_manage.less_from_wallet(query.from_user['id'], price)

            keyboard = [[InlineKeyboardButton("برگشت ⤶", callback_data="select_server")]]
            query.edit_message_text(text='پرداخت با موفقیت انجام شد.✅', parse_mode='markdown',
                                    reply_markup=InlineKeyboardMarkup(keyboard))

        else:
            query.answer('مشکلی وجود داره!')


@handle_telegram_exceptions
def remove_service(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id

    email = query.data.replace('remove_service_', '')
    email = email.replace('accept_rm_ser_', '')
    text = keyboard = None

    get_uuid = sqlite_manager.select(column='client_id,inbound_id,name,id,product_id', table='Purchased',
                                     where=f'client_email = "{email}"')

    get_server_domain = sqlite_manager.select(column='server_domain,price', table='Product',
                                              where=f'id = {get_uuid[0][4]}')

    ret_conf = api_operation.get_client(email, get_server_domain[0][0])

    if int(ret_conf['obj']['total']) and get_server_domain[0][1]:
        upload_gb = int(ret_conf['obj']['up']) / (1024 ** 3)
        download_gb = int(ret_conf['obj']['down']) / (1024 ** 3)
        usage_traffic = round(upload_gb + download_gb, 2)
        total_traffic = int(ret_conf['obj']['total']) / (1024 ** 3)
        left_traffic = round((total_traffic - usage_traffic), 2)

        expiry_timestamp = ret_conf['obj']['expiryTime'] / 1000
        expiry_date = datetime.fromtimestamp(expiry_timestamp)
        days_lefts = (expiry_date - datetime.now()).days
        days_lefts = days_lefts if days_lefts >= 0 else 0
        price = ranking_manage.discount_calculation(chat_id, left_traffic, days_lefts)

    else:
        price, days_lefts, left_traffic = 0, 0, 0

    if 'remove_service_' in query.data:
        keyboard = [[InlineKeyboardButton("✓ بله مطمئنم", callback_data=f"accept_rm_ser_{email}")],
                    [InlineKeyboardButton("✗ منصرف شدم", callback_data="my_service")]]

        text = ('*لطفا اطلاعات زیر رو بررسی کنید:*'
                f'\n\n• زمان باقی مانده سرویس: {days_lefts} روز'
                f'\n• ترافیک باقی مانده سرویس: {left_traffic}GB'
                f'\n• مبلغ قابل بازگشت به کیف پول:* {price:,} تومان*'
                f'\n\n*آیا از حذف این سرویس مطمئن هستید؟*'
                )

        if not ret_conf['obj']['enable'] or not price:
            text = ('*با حذف این سرویس بازپرداخت انجام نمیشود:*'
                    f'\n\n*آیا از حذف این سرویس مطمئن هستید؟*')

    elif 'accept_rm_ser_' in query.data:

        api_operation.del_client(get_uuid[0][1], get_uuid[0][0], get_server_domain[0][0])

        sqlite_manager.delete({'Purchased': ['client_email', email]})

        keyboard = [[InlineKeyboardButton("برگشت ⤶", callback_data="main_menu")]]

        text = f'*سرویس با موفقیت حذف شد و مبلغ {price:,} تومان به کیف پول شما برگشت ✅*'

        if not ret_conf['obj']['enable'] or not price:
            text = '*سرویس با موفقیت حذف شد ✅*'
            sqlite_manager.delete({'Hourly_service': ['purchased_id', get_uuid[0][3]]})
        else:
            wallet_manage.add_to_wallet(chat_id, price)

            record_operation_in_file(chat_id=chat_id, price=price,
                                     name_of_operation=f'حذف سرویس و بازپرداخت به کیف پول {get_uuid[0][2]}',
                                     operation=1,
                                     status_of_pay=1, context=context)
        report_status_to_admin(context,
                               f'User Deleted Service!\nEmail: {email}\nuser Name:{get_uuid[0][2]}\nuser id: {chat_id}',
                               chat_id)

    query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='markdown')


def refresh_login(context):
    api_operation.refresh_connecion()

@handle_telegram_exceptions
def subcategory(update, context):
    query = update.callback_query
    user_id = sqlite_manager.select(table='User', column='id', where=f'chat_id = {query.message.chat_id}')
    uuid_ = str(uuid.uuid5(uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8'), query.from_user['name']))[:5]
    link = f'https://t.me/Fensor_bot/?start={uuid_}_{user_id[0][0]}'
    text = f'{link}\n+50 رتبه هدیه برای اولین بار استفاده کردن از این ربات!'
    keyboard = [
        [InlineKeyboardButton("ارسال برای دوستان", url=f'https://t.me/share/url?text={text}')],
        [InlineKeyboardButton("برگشت ↰", callback_data="setting")]
    ]

    text = ("<b>• دوستانتون رو به ربات دعوت کنید تا با هر خریدشون، 10 درصد مبلغ به کیف‌پول شما اضافه بشه"
            f"\n\n• همچنین +50 رتبه برای شما و کسی که با لینک شما وارد ربات بشه."
            f"\n\n• لینک دعوت شما: \n{link}</b>")
    query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard),
                            disable_web_page_preview=True)


@handle_telegram_exceptions
def service_advanced_option(update, context):
    query = update.callback_query
    email = query.data.replace('advanced_option_', '')
    try:

        status_1, change_shematic, change_server_notif = '', '', ''
        keyboard_main = None

        if 'change_auto_renewal_status_' in query.data:
            data = query.data.replace('change_auto_renewal_status_', '').split('__')
            changed_to, status_1 = (1, '\n\n↲ بعد از پایان سرویس، درصورت اعتبار داشتن کیف پول، بسته به صورت خودکار تمدید میشود.') if eval(data[1]) else (0, '')
            email = data[0]
            sqlite_manager.update({'Purchased': {'auto_renewal': changed_to}}, where=f'client_email = "{email}"')
            query.answer('با موفقیت تغییر یافت ✅')

        elif 'change_config_shematic_' in query.data:
            email = query.data.replace('change_config_shematic_', '')
            get_data = sqlite_manager.select(table='Purchased', where=f'client_email = "{email}"')

            get_server_country = sqlite_manager.select(column='name,server_domain', table='Product',
                                                       where=f'id = {get_data[0][6]}')

            generate_key = f"{query.message.chat_id}_{random.randint(0, 10_000_000)}"
            get_service_uuid = get_data[0][10]
            get_domain = get_server_country[0][1]
            ret_conf = api_operation.get_client(email, get_domain)

            data = {
                "id": get_data[0][7],
                "settings": "{{\"clients\":[{{\"id\":\"{0}\",\"alterId\":0,"
                            "\"email\":\"{1}\",\"limitIp\":0,\"totalGB\":{2},\"expiryTime\":{3},"
                            "\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}}]}}".format(generate_key, get_data[0][9],
                                                                                       ret_conf['obj']['total'],
                                                                                       ret_conf['obj']['expiryTime'])}

            api_operation.update_client(get_service_uuid, data, get_domain)
            get_address = get_data[0][8].replace(str(get_service_uuid), str(generate_key))
            sqlite_manager.update({'Purchased': {'details': get_address, 'client_id': generate_key}},
                                  where=f'client_email = "{email}"')
            change_shematic = '\n\n↲ پیکربندی تغییر یافت، سرویس را کپی جایگزین قبلی کنید.'
            query.answer('پیکربندی سرویس تغییر یافت ✅')

            report_status_to_admin(context, f'User changed Config Shematic\nConfig Email: {email}',
                                   chat_id=query.message.chat_id)

        get_data = sqlite_manager.select(table='Purchased', where=f'client_email = "{email}"')
        get_server_country = sqlite_manager.select(column='name,server_domain', table='Product', where=f'id = {get_data[0][6]}')

        online_configs = api_operation.get_onlines(get_server_country[0][1])
        if not online_configs.get('obj', []):
            online_configs['obj'] = []

        get_server_country = get_server_country[0][0].replace('سرور ', '')
        auto_renewal, auto_renewal_button, chenge_to = ('فعال ✓', 'غیرفعال کردن تمدید خودکار ✗', False) if get_data[0][15] else ('غیرفعال ✗', 'فعال کردن تمدید خودکار ✓', True)

        connection_status = 'آنلاین 🟢' if email in online_configs.get('obj', []) else 'آفلاین 🔴'

        text_ = (
            "<b>🟡 با تغییر گزینه‌ها، تنظیمات سرویس تغییر می‌کند و اگر به این سرویس متصل هستید،"
            " ارتباط قطع خواهد شد. لطفاً اطمینان حاصل کنید که قادر به جایگزینی آدرس جدید هستید.</b>"
            f"\n\n🔷 نام سرویس: {email}"
            f"\n🔌 وضعیت اتصال: {connection_status}"
            f"\n🗺 موقعیت سرور: {get_server_country}"
            f"\n🔗 تمدید خودکار: {auto_renewal}"
            f"{status_1}"
            f"\n\n🌐 آدرس سرویس:\n <code>{get_data[0][8]}</code>"
            f"{change_shematic}"
            f"{change_server_notif}"
        )

        keyboard = [[InlineKeyboardButton(f"{auto_renewal_button}", callback_data=f"change_auto_renewal_status_{email}__{chenge_to}")],
                    [InlineKeyboardButton(f" تعویض کانفیگ ⤰", callback_data=f"change_config_shematic_{email}"),
                    InlineKeyboardButton("• انتقال مالکیت", callback_data=f"change_service_ownership_{email}")],
                    [InlineKeyboardButton(f"گزارش مصرف ⥮", callback_data=f"statistics_week_{get_data[0][0]}_hide"),
                     InlineKeyboardButton("تازه سازی ↻", callback_data=f"advanced_option_{email}")],
                    [InlineKeyboardButton("برگشت ↰", callback_data=f"view_service_{email}")]]

        query.edit_message_text(text_, reply_markup=InlineKeyboardMarkup(keyboard if not keyboard_main else keyboard_main), parse_mode='html')


    except EOFError as eof:
        if 'service_is_depleted' in str(eof):
            query.answer('این ویژگی فقط برای سرویس های فعال است')
        else:
            raise eof

    except Exception as e:
        if "specified new message content and reply markup are exactly the same" in str(e):
            return query.answer('آپدیت نشد، احتمالا اطلاعات تغییری نکرده!')
        else:
            ready_report_problem_to_admin(context, text='service_advanced_option', chat_id=query.message.chat_id, error=e)
            something_went_wrong(update, context)
            raise e


@handle_telegram_conversetion_exceptions
def change_service_ownership(update, context):
    query = update.callback_query
    email = query.data.replace('change_service_ownership_', '')
    context.user_data['service_email'] = email
    text = ('<b>بسیار خب، آیدی عددی کاربر مورد نظر را ارسال کنید.'
            '\n\nآیدی عددی را میتوان در صفحه اصلی راهنما ربات پیدا کرد.</b>')
    keyboard = [[InlineKeyboardButton("منصرف شدم ⤹", callback_data=f"csos_cancel")],
                [InlineKeyboardButton("صفحه اصلی ↰", callback_data=f"main_menu")]]
    query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))
    return GET_CONVER


@handle_telegram_conversetion_exceptions
def change_service_ownership_func(update, context):
    user = update.message.from_user
    email = context.user_data['service_email']

    keyboard = [[InlineKeyboardButton("صفحه اصلی", callback_data="main_menu_in_new_message")]]

    if update.message.text:
        new_owner_chat_id = int(update.message.text)

        new_user_detail = sqlite_manager.select(table='User', where=f'chat_id = {new_owner_chat_id}')

        sqlite_manager.update({'Purchased': {'name': init_name(new_user_detail[0][1]), 'user_name': new_user_detail[0][2],
                                             'chat_id': new_owner_chat_id}},
                              where=f'chat_id = {user["id"]} and client_email = "{email}"')

        report_status_to_admin(context, f'Change Service [{email}] OwnerShip to {new_owner_chat_id}',
                               chat_id=user['id'])
        update.message.reply_text(f'<b>انتقال سرویس با موفقیت انجام شد ✅</b>',
                                  reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')

        message_to_user(update, context,
                        message=f'<b>کاربر {user["first_name"]} یک سرویس برای شما فرستاد!\nنام سرویس: {email}</b>',
                        chat_id=new_owner_chat_id)

    else:
        update.message.reply_text('مشکلی وجود داشت. فقط آیدی عددی با فرمت مناسب قابل قبول است!',
                                  reply_markup=InlineKeyboardMarkup(keyboard))

    context.user_data.clear()
    return ConversationHandler.END


change_service_ownership_conver = ConversationHandler(
    entry_points=[CallbackQueryHandler(change_service_ownership, pattern='change_service_ownership_')],
    states={
        GET_CONVER: [MessageHandler(Filters.all, change_service_ownership_func)]
    },
    fallbacks=[CallbackQueryHandler(cancel, pattern='csos_cancel')],
    conversation_timeout=1000,
    per_chat=True,
    allow_reentry=True
)


@handle_telegram_exceptions
def service_statistics(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id

    get_data = query.data.split('_')
    get_page = get_data[3]
    get_period = get_data[2]


    if get_period == 'all':
        number_in_page = 10
        check = f'chat_id = {chat_id} and active = 1'

        if chat_id in ranking_manage.list_of_partner:
            check = f'chat_id = {chat_id}'

        get_limit = int(get_page)

        get_all_purchased = sqlite_manager.select(table='Purchased', where=check)
        get_purchased = get_all_purchased[get_limit - number_in_page:get_limit]

        if get_purchased:

            keyboard = [
                [InlineKeyboardButton(f"{'✅' if ser[11] == 1 else '❌'} {ser[9]}",
                                      callback_data=f"statistics_week_{ser[0]}_hide")] for ser in get_purchased]


            if len(get_all_purchased) > number_in_page:
                keyboard_backup = []
                keyboard_backup.append(InlineKeyboardButton("قبل ⤌",
                                                            callback_data=f"service_statistics_{get_limit - number_in_page}")) if get_limit != number_in_page else None
                keyboard_backup.append(
                    InlineKeyboardButton(f"صفحه {int(get_limit / number_in_page)}", callback_data="just_for_show"))
                keyboard_backup.append(InlineKeyboardButton("⤍ بعد",
                                                            callback_data=f"service_statistics_{get_limit + number_in_page}")) if get_limit < len(
                    get_all_purchased) else None
                keyboard.append(keyboard_backup)

            keyboard.append([InlineKeyboardButton("برگشت ↰", callback_data="main_menu")])
            text = "<b>برای مشاهده گزارش مصرف، سرویس مورد نظر را انتخاب کنید:</b>"

            query.delete_message()
            context.bot.send_message(chat_id=chat_id, text=text,
                                     reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')

        else:
            query.answer('شما صاحب سرویسی نیستید!')

@handle_telegram_exceptions
def delete_message(update, context):
    query = update.callback_query
    query.delete_message()
    query.answer('پیام حذف شد!')
    context.user_data.clear()
    return ConversationHandler.END


@handle_telegram_exceptions
def get_ticket_priority(update, context):
    query = update.callback_query
    query.answer('تیکت ایجاد شد!')
    text = '<b>• بسیار خب، لطفا اولویت را انتخاب کنید:</b>'
    keyboard = [
        [InlineKeyboardButton(f"بسیار مهم", callback_data=f"set_priority_necessary")],
        [InlineKeyboardButton(f"مهم", callback_data=f"set_priority_medium")],
        [InlineKeyboardButton(f"معمولی", callback_data=f"set_priority_low")],
        [InlineKeyboardButton(f"منصرف شدم", callback_data=f"delete_message")]
    ]
    context.bot.send_message(chat_id=query.message.chat_id, text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))


@handle_telegram_conversetion_exceptions
def say_to_user_send_ticket(update, context):
    query = update.callback_query
    context.user_data['priority'] = query.data.replace('set_priority_', '')
    text = ('<b>• دریافت شد! حالا پیام خود را بفرستید.'
            '\nهمچنین میتوانید عکس بفرستید و متن مورد نظر را در کپشن ذکر کنید.</b>')
    keyboard = [[InlineKeyboardButton(f"منصرف شدم", callback_data=f"delete_message")]]
    query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))
    return GET_TICKET


@handle_telegram_conversetion_exceptions
def send_ticket_to_admin(update, context):
    user = update.message.from_user
    priority = context.user_data['priority']

    file_id = update.message.photo[-1].file_id if update.message.photo else None
    user_message = update.message.text if update.message.text else update.message.caption or 'Witout Caption!'

    text = f"New Ticket | {priority}\nName: {user['name']}\nUserName: @{user['username']}\nUserID: {user['id']}\nUser Message: {user_message}"

    ticket_id = ticket_manager.create_ticket(user.id, f'{user_message[:10]} ...', user_message, priority, 'sales', file_id)

    user_responce_text = ('<b>✅ تیکت با موفقیت ایجاد شد!'
                          f'\n\nآیدی تیکت: {ticket_id}'
                          f'\nوضعیت: باز'
                          f'\n\n• پاسخ ادمین از طریق ربات به اطلاع شما میرسد.</b>')

    keyboard = [
        [InlineKeyboardButton("پیام جدید 🆕", callback_data=f"reply_ticket_{ticket_id}"),
         InlineKeyboardButton("بستن تیکت 🔒", callback_data=f"change_ticket_status_{ticket_id}")],
        [InlineKeyboardButton("صفحه اصلی", callback_data="main_menu_in_new_message")]
    ]

    admin_keyboard = [
        [InlineKeyboardButton("Anwser 🎯", callback_data=f"reply_ticket_{ticket_id}"),
         InlineKeyboardButton("Close Ticket 🔒", callback_data=f"change_ticket_status_{ticket_id}")]
    ]

    update.message.reply_text(user_responce_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')

    if file_id:
        context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=file_id, caption=text, reply_markup=InlineKeyboardMarkup(admin_keyboard))
    else:
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, reply_markup=InlineKeyboardMarkup(admin_keyboard))

    context.user_data.clear()
    return ConversationHandler.END


tickect_by_user = ConversationHandler(
    entry_points=[CallbackQueryHandler(say_to_user_send_ticket, pattern='set_priority_')],
    states={
        GET_TICKET: [MessageHandler(Filters.all, send_ticket_to_admin)]
    },
    fallbacks=[],
    conversation_timeout=1000,
    per_chat=True,
    allow_reentry=True
)

@handle_telegram_exceptions
def change_ticket_status(update, context):
    query = update.callback_query
    master_ticket_id = int(query.data.replace('change_ticket_status_', ''))
    change_to = 'close'
    keyboard = [[InlineKeyboardButton(f"باز کردن تیکت 🔓", callback_data=f"change_ticket_status_{master_ticket_id}")],
                [InlineKeyboardButton("همه تیکت ها", callback_data="all_ticket"),
                 InlineKeyboardButton("صفحه اصلی", callback_data="main_menu_in_new_message")]
                ]
    if not ticket_manager.check_ticket_status(master_ticket_id)[0]:
        change_to = 'open'
        keyboard = [
            [InlineKeyboardButton("پیام جدید 🆕", callback_data=f"reply_ticket_{master_ticket_id}"),
             InlineKeyboardButton("بستن تیکت 🔒", callback_data=f"change_ticket_status_{master_ticket_id}")],
            [InlineKeyboardButton("همه تیکت ها", callback_data="all_ticket"),
             InlineKeyboardButton("صفحه اصلی", callback_data="main_menu_in_new_message")]
        ]

    ticket_manager.change_ticket_status(master_ticket_id, change_to)
    format_ = {'open': 'باز', 'close': 'بسته'}
    ticket_status = format_.get(change_to)
    text = (f'<b>✅ تیکت با موفقیت {ticket_status} شد'
            f'\n\nآیدی تیکت: {master_ticket_id}'
            f'\nوضعیت: {ticket_status}'
            f'</b>')
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
    query.answer('عملیات با موفقیت انجام شد!')


@handle_telegram_conversetion_exceptions
def reply_to_ticket(update, context):
    query = update.callback_query
    master_ticket_id = int(query.data.replace('reply_ticket_', ''))
    context.user_data['master_ticket_id'] = master_ticket_id

    if not ticket_manager.check_ticket_status(master_ticket_id)[0]:
        query.answer('این تیکت بسته است!')
        return ConversationHandler.END

    text = ('<b>• پاسخ خود را بفرستید.'
            '\nهمچنین میتوانید عکس بفرستید و متن مورد نظر را در کپشن ذکر کنید.</b>')

    keyboard = [[InlineKeyboardButton(f"منصرف شدم", callback_data=f"delete_message")]]

    context.bot.send_message(chat_id=query.message.chat_id, text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))
    return REPLY_TICKET


@handle_telegram_conversetion_exceptions
def reply_ticket_manager(update, context):
    chat_id = update.message.chat_id
    master_ticket_id = context.user_data['master_ticket_id']

    file_id = update.message.photo[-1].file_id if update.message.photo else None
    user_message = update.message.text if update.message.text else update.message.caption or 'Witout Caption!'

    ticket_manager.reply_to_ticket(master_ticket_id, chat_id, user_message, file_id)
    ticket_owner_chat_id = int(ticket_manager.check_ticket_status(master_ticket_id)[1])

    keyboard = [
        [InlineKeyboardButton("پیام جدید 🆕", callback_data=f"reply_ticket_{master_ticket_id}"),
         InlineKeyboardButton("بستن تیکت 🔒", callback_data=f"change_ticket_status_{master_ticket_id}")],
        [InlineKeyboardButton("صفحه اصلی", callback_data="main_menu_in_new_message")]
    ]

    user_responce_text = ('<b>✅ پاسخ با موفقیت ثبت شد!'
                          f'\n\nآیدی تیکت: {master_ticket_id}'
                          f'\nوضعیت: باز'
                          f'\n\n• پاسخ از طریق ربات به اطلاع شما میرسد.</b>')

    owner_text = ('<b>🎯 تیکت شما پاسخ داده شد!'
                  f'\n\n {user_message}'
                  f'\n\nآیدی تیکت: {master_ticket_id}'
                  f'\nوضعیت: باز'
                  f'</b>')

    update.message.reply_text(text=user_responce_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')

    if ticket_owner_chat_id == chat_id:
        chat_id = ADMIN_CHAT_ID
    else:
        chat_id = ticket_owner_chat_id

    if file_id:
        context.bot.send_photo(chat_id=chat_id, photo=file_id, caption=owner_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
    else:
        context.bot.send_message(chat_id=chat_id, text=owner_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')


    context.user_data.clear()
    return ConversationHandler.END


reply_ticket = ConversationHandler(
    entry_points=[CallbackQueryHandler(reply_to_ticket, pattern='reply_ticket_')],
    states={
        REPLY_TICKET: [MessageHandler(Filters.all, reply_ticket_manager)]
    },
    fallbacks=[],
    conversation_timeout=1000,
    per_chat=True,
    allow_reentry=True
)



