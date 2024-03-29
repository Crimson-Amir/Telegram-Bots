import random
import uuid
from datetime import datetime, timedelta
import telegram.error
from utilities import (human_readable,something_went_wrong,
                       ready_report_problem_to_admin,format_traffic,record_operation_in_file,
                       send_service_to_customer_report, report_status_to_admin, find_next_rank,
                       change_service_server, get_rank_and_emoji, report_problem_by_user_utilitis, report_problem)
import admin_task
from private import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
import ranking
import utilities
from admin_task import (add_client_bot, api_operation, second_to_ms, message_to_user, wallet_manage, sqlite_manager, ranking_manage)
import qrcode
from io import BytesIO
import pytz
import re
import functools
from sqlite_manager import ManageDb
import json


class Task(ManageDb):
    def __init__(self): super().__init__('v2ray')


    @staticmethod
    def handle_exceptions(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                side = 'Task Func'
                print(f"[{side}] An error occurred in {func.__name__}: {e}")
                report_problem(func.__name__, e, side)
        return wrapper

    @staticmethod
    def get_flag(text):
        return text[:2]

    @handle_exceptions
    def return_server_countries(self):
        plans = self.select(table='Product', where='active = 1')
        unic_plans = {name[3]: name[4] for name in plans}
        if not unic_plans:
            raise IndexError('There Is No Product!')
        return unic_plans

    @handle_exceptions
    def upgrade_service(self, context, service_id):
        get_client = sqlite_manager.select(table='Purchased', where=f'id = {service_id}')

        get_server_domain = sqlite_manager.select(column='server_domain', table='Product',
                                                  where=f'id = {get_client[0][6]}')

        user_db = sqlite_manager.select(table='User', where=f'chat_id = {get_client[0][4]}')

        price = ranking_manage.discount_calculation(user_db[0][3], user_db[0][5], user_db[0][6])

        client_id = get_client[0][10]
        client_email = get_client[0][9]
        inbound_id = get_client[0][7]
        now = datetime.now(pytz.timezone('Asia/Tehran'))

        ret_conf = api_operation.get_inbound(inbound_id, get_server_domain[0][0])
        client_list = json.loads(ret_conf['obj']['settings'])['clients']

        for client in client_list:
            if client['email'] == client_email:
                client_id = client['id']

                if client['enable']:
                    tra = client['totalGB']
                    traffic = (user_db[0][5] * (1024 ** 3)) + tra
                    expiry_timestamp = client['expiryTime']
                    expiry_datetime = datetime.fromtimestamp(expiry_timestamp / 1000)
                    new_expiry_datetime = expiry_datetime + timedelta(days=user_db[0][6])
                    human_data = new_expiry_datetime
                    my_data = int(new_expiry_datetime.timestamp() * 1000)
                else:
                    traffic = user_db[0][5] * (1024 ** 3)
                    my_data = now + timedelta(days=user_db[0][6])
                    human_data = my_data
                    my_data = int(my_data.timestamp() * 1000)
                    print(api_operation.reset_client_traffic(client_id, client_email, get_server_domain[0][0]))

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
                                                     f'\nTraffic: {user_db[0][5]}GB\nPeriod: {human_data.day}day',
                                       chat_id=get_client[0][4])

                break

        return get_client[0][4], price

task = Task()

def handle_telegram_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            side = 'Telgram Func'
            print(f"[{side}] An error occurred in {func.__name__}: {e}")
            report_problem(func.__name__, e, side)
            something_went_wrong(*args)

    return wrapper


@handle_telegram_exceptions
def show_servers(update, context):
    query = update.callback_query

    get_all_country = task.return_server_countries()

    keyboard = [[InlineKeyboardButton(key, callback_data=value)] for key, value in get_all_country.items()]
    keyboard.append([InlineKeyboardButton("برگشت ↰", callback_data="main_menu")])

    text = ("<b>• سرور مورد نظر خودتون رو انتخاب کنید:"
            "\n\n• بعد از خرید، لوکیشن سرویس قابل تغییر است.</b>")

    query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='html'
    )


@handle_telegram_exceptions
def get_service_of_server(update, context):
    query = update.callback_query
    country = query.data

    plans = sqlite_manager.select(table='Product', where=f'active = 1 and country = "{country}"')
    country_flag = task.get_flag(plans[0][3])

    text = (f"<b>• {country_flag} سرویس مناسب خودتون رو انتخاب کنید:"
            f"\n\n• با انتخاب گزینه دلخواه میتونید یک سرویس شخصی سازی شده بسازید.</b>"
            "\n\n<b>• سرویس ساعتی به شما اجازه میده به اندازه مصرف در هر ساعت پرداخت کنید.</b>")

    country_unic = {name[4] for name in plans}

    for country in country_unic:
        if query.data == country:
            service_list = [service for service in plans if service[4] == country]
            keyboard = [[InlineKeyboardButton(f"سرویس {pattern[5]} روزه - {pattern[6]} گیگابایت - {ranking_manage.discount_calculation(query.from_user['id'], direct_price=pattern[7]):,} تومان",
                                              callback_data=f"service_{pattern[0]}")] for pattern in service_list]

            keyboard.append([InlineKeyboardButton("✪ سرویس دلخواه", callback_data=f"personalization_service_{plans[0][0]}"),
                             InlineKeyboardButton("✪ سرویس ساعتی", callback_data=f"pay_per_use_{plans[0][0]}")])

            keyboard.append([InlineKeyboardButton("برگشت ↰", callback_data="select_server")])

            query.edit_message_text(text= text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')


@handle_telegram_exceptions
def hide_buttons(update, context):
    query = update.callback_query
    text = query.message.text
    query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([]))
    query.answer('OK')

def payment_page(update, context):
    query = update.callback_query
    id_ = int(query.data.replace('service_', ''))
    try:
        package = sqlite_manager.select(table='Product', where=f'id = {id_}')
        price = ranking_manage.discount_calculation(query.from_user['id'], direct_price=package[0][7], more_detail=True)

        if package[0][7]:
            keyboard = [
                [InlineKeyboardButton("پرداخت از کیف پول", callback_data=f'payment_by_wallet_{id_}'),
                 InlineKeyboardButton("کارت به کارت", callback_data=f'payment_by_card_{id_}')],
                [InlineKeyboardButton("برگشت ↰", callback_data=f"{package[0][4]}")]
            ]
        else:
            free_service_is_taken = sqlite_manager.select(column='free_service', table='User', where=f'chat_id = {query.message.chat_id}')[0][0]
            if free_service_is_taken:
                keyboard_free = [
                    [InlineKeyboardButton("🔰 رتبه‌بندی", callback_data='rank_page')],
                    [InlineKeyboardButton("برگشت ↰", callback_data=f"main_menu")]
                ]
                query.edit_message_text(
                    text='<b>شما یک بار این سرویس رو دریافت کردید!\n\n • با ارتقا رتبه خودتون، قابلیت دریافت سرویس تست به صورت هفتگی رو به دست بیارید!</b>',
                    parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard_free))
                return
            else:
                keyboard = [
                    [InlineKeyboardButton("دریافت ⤓", callback_data=f'get_free_service')],
                    [InlineKeyboardButton("برگشت ↰", callback_data="main_menu")]
                ]

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
    except Exception as e:
        ready_report_problem_to_admin(context, 'PAYMENT PAGE', query.message.chat_id, e)
        something_went_wrong(update, context)


def get_card_pay_evidence(update, context):
    query = update.callback_query
    user = query.from_user
    id_ = int(query.data.replace('payment_by_card_', ''))
    try:
        package = sqlite_manager.select(table='Product', where=f'id = {id_}')

        price = ranking_manage.discount_calculation(query.from_user['id'], direct_price=package[0][7], more_detail=True)

        context.user_data['package'] = package
        keyboard = [[InlineKeyboardButton("ساخت ", callback_data="send_main_message")],
                    [InlineKeyboardButton("صفحه اصلی ⤶", callback_data="send_main_message")]]

        ex = sqlite_manager.select('id', 'Purchased', where=f'active = 0 and chat_id = {user["id"]}', limit=1)

        if not ex:
            ex = sqlite_manager.insert('Purchased',rows= [{'active': 0,'status': 0, 'name': user["first_name"],'user_name': user["username"],
                                                           'chat_id': int(user["id"]), 'product_id': id_, 'notif_day': 0, 'notif_gb': 0}])
        else:
            sqlite_manager.update({'Purchased':
                                       {'active': 0, 'status': 0, 'name': user["first_name"], 'user_name': user["username"],
                                        'chat_id': int(user["id"]), 'product_id': id_, 'notif_day': 0, 'notif_gb': 0}}, where=f'id = {ex[0][0]}')
            ex = ex[0][0]

        check_off = f'\n<b>تخفیف: {price[1]} درصد</b>' if price[1] else ''

        context.user_data['purchased_id'] = ex

        text = (f"<b>اطلاعات زیر رو بررسی کنید و در صورت تایید پرداخت رو نهایی کنید:</b>"
                f"\n\nمدت اعتبار فاکتور: 10 دقیقه"
                f"\nسرویس: {package[0][5]} روز - {package[0][6]} گیگابایت"
                f"\n<b>قیمت</b>:"
                f"<code>{price[0]:,}</code>"
                f"<b> تومان </b>"
                f"{check_off}"
                f"\n\n<b>• لطفا مبلغ رو به شماره‌حساب زیر واریز کنید و اسکرین‌شات یا شماره‌پیگیری رو بعد از همین پیام ارسال کنید، اطمینان حاصل کنید ربات درخواست رو ثبت کنه.</b>"
                f"\n\n<code>6219861938619417</code> - امیرحسین نجفی"
                f"\n\n<b>• بعد از تایید شدن پرداخت، سرویس برای شما ارسال میشه، زمان تقریبی یک دقیقه تا 3 ساعت.</b>")

        query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))
        return GET_EVIDENCE
    except Exception as e:
        ready_report_problem_to_admin(context, 'GET CARD PAY EVIDENCE', query.message.chat_id, e)
        something_went_wrong(update, context)


def send_evidence_to_admin(update, context):
    user = update.message.from_user
    try:
        package = context.user_data['package']
        purchased_id = context.user_data['purchased_id']
        price = ranking_manage.discount_calculation(user['id'], direct_price=package[0][7])

        if not ranking_manage.enough_rank('GET_SERVICE_WITHOUT_CONFIRM', user['id']):
            keyboard = [[InlineKeyboardButton("Accept ✅", callback_data=f"accept_card_pay_{purchased_id}"),
                         InlineKeyboardButton("Refuse ❌", callback_data=f"refuse_card_pay_{purchased_id}")],
                        [InlineKeyboardButton("Hide buttons", callback_data=f"hide_buttons")]]
            text_ = f'درخواست شما با موفقیت ثبت شد✅\nنتیجه از طریق همین ربات بهتون اعلام میشه'
            text = "- Check the new payment to the card [Buy A Service]:\n\n"

        else:
            send_clean_for_customer(None, context, purchased_id)
            keyboard = []
            text_ = f'سرویس با موفقیت برای شما ارسال شد✅'
            text = '- The user rank was sufficient to get the service without confirm [Buy A Service]\n\n'

        text += f"Name: {user['first_name']}\nUserName: @{user['username']}\nID: {user['id']}\n\n"
        service_detail = f"\n\nServer: {package[0][4]}\nInbound id: {package[0][1]}\nPeriod: {package[0][5]} Day\nTraffic: {package[0][6]}GB\nPrice: {price:,} Toman"

        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            text += f"caption: {update.message.caption}" or 'Witout caption!'
            text += service_detail
            context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=file_id, caption=text , reply_markup=InlineKeyboardMarkup(keyboard))
            update.message.reply_text(text_)

        elif update.message.text:
            text += f"Text: {update.message.text}{service_detail}"
            context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, reply_markup=InlineKeyboardMarkup(keyboard))
            update.message.reply_text(text_)

        else:
            update.message.reply_text('مشکلی وجود داره! فقط متن یا عکس قابل قبوله.')

        context.user_data.clear()
        return ConversationHandler.END
    except Exception as e:
        ready_report_problem_to_admin(context,'SEND EVIDENCE TO ADMIN', user['id'], e)
        text = ("مشکلی وجود داشت!"
                "گزارش به ادمین ها ارسال شد، نتیجه بهتون اعلام میشه")
        keyboard = [[InlineKeyboardButton("برگشت ↰", callback_data="main_menu")]]
        update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END


def cancel(update, context):
    query = update.callback_query
    keyboard = [[InlineKeyboardButton("صفحه اصلی ↰", callback_data=f"main_menu")]]
    query.edit_message_text(text="با موفقیت کنسل شد!", reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END


get_service_con = ConversationHandler(
    entry_points=[CallbackQueryHandler(get_card_pay_evidence, pattern=r'payment_by_card_\d+')],
    states={
        GET_EVIDENCE: [MessageHandler(Filters.all, send_evidence_to_admin)]
    },
    fallbacks=[CallbackQueryHandler(cancel, pattern='cancel')],
    conversation_timeout=1500,
    per_chat=True,
    allow_reentry=True,
)


def subcategory_auto(context, invite_chat_id, price):
    if invite_chat_id and price:
        wallet_manage.add_to_wallet(invite_chat_id, (int(price * 10 / 100)),
                                    user_detail={'name': invite_chat_id, 'username': invite_chat_id})
        text = (f"{int(price * 10 / 100):,} تومان به کیف پول شما اضافه شد."
                "\n\nاز طریق ارسال لینک دعوت توسط شما، کاربر جدیدی به ربات ما اضافه شده و خرید انجام داده است. به عنوان تشکر، 10 درصد از مبلغ خرید او به کیف پول شما اضافه شد."
                "\nمتشکریم!")
        utilities.message_to_user(None, context, message=text, chat_id=invite_chat_id)


def send_clean_for_customer(query, context, id_):
    create = add_client_bot(id_)
    if create[0]:
        get_client = sqlite_manager.select(table='Purchased', where=f'id = {id_}')
        try:
            get_product = sqlite_manager.select(table='Product', where=f'id = {get_client[0][6]}')
            get_user_detail = sqlite_manager.select(column='invited_by', table='User', where=f'chat_id={get_client[0][4]}')

            get_domain = get_product[0][10]
            get_server_domain = get_product[0][11]
            returned = api_operation.get_client_url(client_email=get_client[0][9], inbound_id=get_client[0][7],
                                                    domain=get_domain, server_domain=get_server_domain)
            if returned:
                returned_copy = f'`{returned}`'
                qr_code = qrcode.make(returned)
                qr_image = qr_code.get_image()
                buffer = BytesIO()
                qr_image.save(buffer, format='PNG')
                binary_data = buffer.getvalue()
                keyboard = [[InlineKeyboardButton("دریافت فایل سرویس", callback_data=f"create_txt_file"),
                             InlineKeyboardButton("🎛 سرویس های من", callback_data=f"my_service")],
                            [InlineKeyboardButton("صفحه اصلی ربات ↵", callback_data=f"main_menu_in_new_message")]]
                context.user_data['v2ray_client'] = returned

                context.bot.send_photo(photo=binary_data,
                                       caption=f' سرویس شما با موفقیت فعال شد✅\n\n*• میتونید جزئیات سرویس رو از بخش "سرویس های من" مشاهده کنید.\n\n✪ لطفا سرویس رو به صورت مستقیم از طریق پیام رسان های ایرانی یا پیامک ارسال نکنید، با کلیک روی گزینه "دریافت فایل" سرویس را به صورت فایل یا کیوآرکد ارسال کنید.* \n\n\nلینک:\n{returned_copy}',
                                       chat_id=get_client[0][4], reply_markup=InlineKeyboardMarkup(keyboard),
                                       parse_mode='markdown')

                price = ranking_manage.discount_calculation(direct_price=get_product[0][7], user_id=get_client[0][4])

                record_operation_in_file(chat_id=get_client[0][4], price=price,
                                         name_of_operation=f'خرید سرویس {get_client[0][9]}', operation=0,
                                         status_of_pay=1, context=context)


                send_service_to_customer_report(context, status=1, chat_id=get_client[0][4], service_name=get_client[0][9])


                invite_chat_id = get_user_detail[0][0]
                subcategory_auto(context, invite_chat_id, price)

                return True
            else:
                send_service_to_customer_report(context, status=0, chat_id=get_client[0][4], service_name=get_client[0][9],
                                                more_detail=create)
                print('wrong: ', returned)
                return False

        except Exception as e:
            print(e)
            send_service_to_customer_report(context, status=0, chat_id=get_client[0][4], service_name=get_client[0][9],
                                            more_detail='ERROR IN SEND CLEAN FOR CUSTOMER', error=e)
            return False
    else:
        send_service_to_customer_report(context, status=0, chat_id=None, service_name=None,
                                        more_detail=f'EEROR IN ADD CLIENT (SEND CLEAN FOR CUSTOMER)\n{create}')
        raise Exception(f'Error: {create}')


def apply_card_pay(update, context):
    query = update.callback_query
    try:
        if 'accept_card_pay_' in query.data or 'refuse_card_pay_' in query.data:
            status = query.data.replace('card_pay_', '')
            keyboard = [[InlineKeyboardButton("YES", callback_data=f"ok_card_pay_{status}")]
                , [InlineKeyboardButton("NO", callback_data=f"cancel_pay")]]
            query.answer('Confirm Pleas!')
            context.bot.send_message(text='Are You Sure?', reply_markup=InlineKeyboardMarkup(keyboard), chat_id=ADMIN_CHAT_ID)
        elif 'ok_card_pay_accept_' in query.data:
            id_ = int(query.data.replace('ok_card_pay_accept_', ''))
            send_clean_for_customer(query, context, id_)
            query.delete_message()

        elif 'ok_card_pay_refuse_' in query.data:
            id_ = int(query.data.replace('ok_card_pay_refuse_', ''))
            get_client = sqlite_manager.select(table='Purchased', where=f'id = {id_}')
            context.bot.send_message(text=f'متاسفانه درخواست شما برای ثبت سرویس پذیرفته نشد❌\n ارتباط با پشتیبانی: \n @Fupport ', chat_id=get_client[0][4])
            query.answer('Done ✅')
            query.delete_message()
            record_operation_in_file(chat_id=get_client[0][4], price=0,
                                     name_of_operation=f'خرید سرویس {get_client[0][9]}', operation=0,
                                     status_of_pay=0, context=context)

        elif 'cancel_pay' in query.data:
            query.answer('Done ✅')
            query.delete_message()
    except Exception as e:
        ready_report_problem_to_admin(context,'APLLY CARD PAY', query.message.chat_id, e)
        query.answer('Fail')
        print('errot:', e)


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
    get_purchased = get_all_purchased[get_limit-number_in_page:get_limit]

    if get_purchased:
        disable_service = enable_service = all_service = 0

        keyboard = [[InlineKeyboardButton(f"{'✅' if ser[11] == 1 else '❌'} {ser[9]}", callback_data=f"view_service_{ser[9]}")] for ser in get_purchased]

        for service in get_all_purchased:
            if service[11] == 1:
                enable_service += 1
            else:
                disable_service += 1

            all_service += 1

        if len(get_all_purchased) > number_in_page:
            keyboard_backup = []
            keyboard_backup.append(InlineKeyboardButton("قبل ⤌", callback_data=f"my_service{get_limit - number_in_page}")) if get_limit != number_in_page else None
            keyboard_backup.append(InlineKeyboardButton(f"صفحه {int(get_limit / number_in_page)}", callback_data="just_for_show"))
            keyboard_backup.append(InlineKeyboardButton("⤍ بعد", callback_data=f"my_service{get_limit + number_in_page}")) if get_limit < len(get_all_purchased) else None
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
        query.edit_message_text('<b>• درحال حاضر شما صاحب سرویس نیستید\n\nدرمورد سرویس ها مطالعه کنید و یک سرویس بخرید! :</b>',
                                reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')


def server_detail_customer(update, context):
    query = update.callback_query
    email = update.callback_query.data.replace('view_service_', '')
    try:
        get_data = sqlite_manager.select(table='Purchased', where=f'client_email = "{email}"')
        get_server_country = sqlite_manager.select(column='name,server_domain', table='Product', where=f'id = {get_data[0][6]}')
        get_server_domain = get_server_country[0][1]
        get_server_country = get_server_country[0][0].replace('سرور ','').replace('pay_per_use_', '')

        expiry_month = '♾️'
        total_traffic = '♾️'
        exist_day = '(بدون محدودیت زمانی)'

        ret_conf = api_operation.get_client(email, get_server_domain)

        upload_gb = round(int(ret_conf['obj']['up']) / (1024 ** 3), 2)
        download_gb = round(int(ret_conf['obj']['down']) / (1024 ** 3), 2)
        usage_traffic = round(upload_gb + download_gb, 2)

        change_active, advanced_option_pattern = ('فعال ✅', f'advanced_option_{email}') if ret_conf['obj']['enable'] else ('غیرفعال ❌', 'not_for_depleted_service')

        purchase_date = datetime.strptime(get_data[0][12], "%Y-%m-%d %H:%M:%S.%f%z").replace(tzinfo=None)
        auto_renwal_emoji = 'فعال ✓' if get_data[0][15] else 'غیرفعال ✗'
        auto_renwal = f'\n\n🔄 تمدیدخودکار: {auto_renwal_emoji}'

        keyboard = [[InlineKeyboardButton("تمدید و ارتقا ↟", callback_data=f"upgrade_service_customize_{get_data[0][0]}")]]

        if int(ret_conf['obj']['total']) != 0:
            total_traffic = int(round(ret_conf['obj']['total'] / (1024 ** 3), 2))

        if int(ret_conf['obj']['expiryTime']) != 0:
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
            keyboard = [[InlineKeyboardButton(service_activate_status, callback_data=f"change_infiniti_service_status_{get_data[0][0]}_{ret_conf['obj']['enable']}")]]


        keyboard.append([InlineKeyboardButton("حذف سرویس ⇣", callback_data=f"remove_service_{email}"),
                         InlineKeyboardButton("تازه سازی ↻", callback_data=f"view_service_{email}")])

        keyboard.append([InlineKeyboardButton("گزینه های پیشرفته ⥣", callback_data=advanced_option_pattern)])  # advanced_option_{email}
        keyboard.append([InlineKeyboardButton("برگشت ↰", callback_data="my_service")])

        text_ = (
            f"<b>اطلاعات سرویس انتخاب شده:</b>"
            f"\n\n🔷 نام سرویس: {email}"
            f"\n💡 وضعیت: {change_active}"
            f"\n🗺 موقعیت سرور: {get_server_country}"
            f"\n📅 تاریخ انقضا: {expiry_month} {exist_day}"
            f"\n\n🔼 آپلود↑: {format_traffic(upload_gb)}"
            f"\n🔽 دانلود↓: {format_traffic(download_gb)}"
            f"\n📊 مصرف کل: {usage_traffic}/{total_traffic}{'GB' if isinstance(total_traffic, int) else ''}"
            f"{auto_renwal}"
            f"\n⏰ تاریخ خرید/تمدید: {purchase_date.strftime('%H:%M:%S | %Y/%m/%d')}"
            f"\n\n🌐 آدرس سرویس:\n <code>{get_data[0][8]}</code>"
        )

        query.edit_message_text(text=text_, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
        sqlite_manager.update({'Purchased': {'status': 1 if ret_conf['obj']['enable'] else 0}}, where=f'client_email = "{email}"')

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
                f'{e}'
                )
        query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='markdown')
        ready_report_problem_to_admin(context, text='SERVICE DETAIL FOR CUSTOMER', error=e, chat_id=query.message.chat_id,
                                      detail=f'Service Email: {email}')
        query.answer('مشکلی وجود دارد!')
        print(e)


def change_infiniti_service_status(update, context):
    query = update.callback_query

    get_callback = query.data.replace('change_infiniti_service_status_', '')
    data_clean = get_callback.split('_')
    change_to, status = (0, 'فعال') if data_clean[1] == 'False' else (second_to_ms(datetime.now()), 'غیرفعال')
    get_data = sqlite_manager.select(table='Purchased', where=f'id = {data_clean[0]}')
    get_server_domain = sqlite_manager.select(column='server_domain', table='Product', where=f'id = {get_data[0][6]}')

    if 'accept' in data_clean:

        data = {
            "id": int(get_data[0][7]),
            "settings": "{{\"clients\":[{{\"id\":\"{0}\",\"alterId\":0,"
                        "\"email\":\"{1}\",\"limitIp\":0,\"totalGB\":0,\"expiryTime\":{2},"
                        "\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}}]}}".format(get_data[0][10], get_data[0][9], change_to)}

        print(api_operation.update_client(get_data[0][10], data, get_server_domain[0][0]))
        report_status_to_admin(context, text=f'Service With Email {get_data[0][9]} Has Be Changed Activity By User To {change_to}', chat_id=get_data[0][4])

        query.answer(f'سرویس با موفقیت {status} شد')
        keyboard = [
            [InlineKeyboardButton("برگشت ↰", callback_data=f"view_service_{get_data[0][9]}")]]

        query.edit_message_text(f'سرویس با موفقیت {status} شد✅', reply_markup=keyboard)

    else:
        get_credit = sqlite_manager.select(column='wallet', table='User', where=f'chat_id = {get_data[0][4]}')[0][0]

        if get_credit >= PRICE_PER_DAY:
            text = f'آیا از {status} کردن این سرویس مطمئن هستید؟'
            keyboard = [
                [InlineKeyboardButton(f"بله، {status} کن", callback_data=f"{query.data}_accept")],
                [InlineKeyboardButton("برگشت ↰", callback_data=f"view_service_{get_data[0][9]}")]]
        else:
            text = (f'برای فعال کردن این سرویس، کیف پول خودتون رو شارژ کنید.'
                    f'\n\nاعتبار شما: {get_credit:,}'
                    f'\nحداقل اعتبار برای فعال کردن سرویس: {PRICE_PER_DAY:,}')
            keyboard = [
                [InlineKeyboardButton("افزایش موجودی ↟", callback_data=f"buy_credit_volume")],
                [InlineKeyboardButton("برگشت ↰", callback_data=f"view_service_{get_data[0][9]}")]]
        query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


def remove_service_from_db(update, context):
    query = update.callback_query
    try:
        email = query.data.replace('remove_service_from_db_', '')
        sqlite_manager.delete({'Purchased': ['client_email', email]})
        text = '<b>سرویس با موفقیت حذف شد ✅</b>'
        keyboard = [[InlineKeyboardButton("برگشت ⤶", callback_data="main_menu")]]
        query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
    except Exception as e:
        query.answer('مشکلی در حذف این سرویس وجود داشت!')
        ready_report_problem_to_admin(context,'REMOVE SERVICE FROM DATABASE', query.message.chat_id, e)
        print(e)


def create_file_and_return(update, context):
    query = update.callback_query
    try:
        config_ = context.user_data['v2ray_client']
        random_number = random.randint(0, 5)
        with open(f'text_file/create_v2ray_file_with_id_{random_number}.txt', 'w', encoding='utf-8') as f:
            f.write(config_)
        with open(f'text_file/create_v2ray_file_with_id_{random_number}.txt', 'rb') as document_file:
            context.bot.send_document(document=document_file, chat_id=query.message.chat_id, filename='Open_And_Copy_Service.txt')
        query.answer('فایل ارسال شد.')
        context.user_data.clear()
    except Exception as e:
        query.answer('مشکلی وجود دارد!')
        print(e)


def personalization_service(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id

    if 'personalization_service_' in query.data:
        context.user_data['personalization_service_id'] = int(query.data.replace('personalization_service_', ''))

    get_data_from_db = sqlite_manager.select(table='User', where=f'chat_id = {chat_id}')

    try:
        traffic = abs(get_data_from_db[0][5])
        period = abs(get_data_from_db[0][6])
        price = ranking_manage.discount_calculation(chat_id, traffic, period, more_detail=True)
        check_off = f'\n\n*تخفیف: {price[1]} درصد*' if price[1] else ''

        if 'traffic_low_' in query.data:
            traffic_t = int(query.data.replace('traffic_low_', ''))
            traffic = traffic - traffic_t
            traffic = traffic if traffic >= 1 else 1
        elif 'traffic_high_' in query.data:
            traffic_t = int(query.data.replace('traffic_high_', ''))
            traffic = traffic + traffic_t
            traffic = traffic if traffic <= 500 else 500
        elif 'period_low_' in query.data:
            period_t = int(query.data.replace('period_low_', ''))
            period = period - period_t
            period = period if period >= 1 else 1
        elif 'period_high_' in query.data:
            period_t = int(query.data.replace('period_high_', ''))
            period = period + period_t
            period = period if period <= 500 else 500

        elif 'accept_personalization' in query.data:
            id_ = context.user_data['personalization_service_id']

            inbound_id = sqlite_manager.select(column='inbound_id,name,country,server_domain,domain,country', table='Product', where=f'id = {id_}')

            check_available = sqlite_manager.select(table='Product', where=f'is_personalization = {query.message.chat_id} and country = "{inbound_id[0][5]}"')

            get_data = {'inbound_id': inbound_id[0][0], 'active': 0,
                        'name': inbound_id[0][1], 'country': inbound_id[0][2],
                        'period': period, 'traffic': traffic,
                        'price': price[2], 'date': datetime.now(pytz.timezone('Asia/Tehran')),
                        'is_personalization': query.message.chat_id,'domain': inbound_id[0][4],
                        'server_domain': inbound_id[0][3], 'status': 1}

            if check_available:
                sqlite_manager.update({'Product': get_data}, where=f'id = {check_available[0][0]}')
                new_id = check_available[0][0]
            else:
                new_id = sqlite_manager.insert('Product', [get_data])


            texted = ('*• شخصی سازی را تایید میکنید؟:*'
                      f'\n\nحجم سرویس: {traffic}GB'
                      f'\nدوره زمانی: {period} روز'
                      f'\n*قیمت: {price[0]:,}*'
                      f'{check_off}')
            keyboard = [[InlineKeyboardButton("بله", callback_data=f"service_{new_id}"),
                         InlineKeyboardButton("خیر", callback_data=f"personalization_service_{id_}")]]

            query.edit_message_text(text=texted, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
            context.user_data.clear()
            return


        sqlite_manager.update({'User': {'traffic':traffic, 'period': period}},where=f'chat_id = {query.message.chat_id}')
        price = ranking_manage.discount_calculation(chat_id, traffic, period)

        text = ('*• تو این بخش میتونید سرویس مورد نظر خودتون رو شخصی سازی کنید:*'
                f'\n\nحجم سرویس: {traffic}GB'
                f'\nدوره زمانی: {period} روز'
                f'\n*قیمت:* {price:,} *تومان*'
                f'{check_off}')
        keyboard = [
            [InlineKeyboardButton("«", callback_data="traffic_low_10"),
             InlineKeyboardButton("‹", callback_data="traffic_low_1"),
             InlineKeyboardButton(f"{traffic}GB", callback_data="just_for_show"),
             InlineKeyboardButton("›", callback_data="traffic_high_1"),
             InlineKeyboardButton("»", callback_data="traffic_high_10")],
            [InlineKeyboardButton("«", callback_data="period_low_10"),
             InlineKeyboardButton("‹", callback_data="period_low_1"),
             InlineKeyboardButton(f"{period}Day", callback_data="just_for_show"),
             InlineKeyboardButton("›", callback_data="period_high_1"),
             InlineKeyboardButton("»", callback_data="period_high_10")],
            [InlineKeyboardButton("✓ تایید", callback_data="accept_personalization")],
            [InlineKeyboardButton("برگشت ↰", callback_data="select_server")]
        ]
        query.edit_message_text(text=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        ready_report_problem_to_admin(context, text='personalization_service', chat_id=query.message.chat_id, error=e)
        query.answer('مشکلی وجود دارد')


def personalization_service_lu(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id

    if 'upgrade_service_customize_' in query.data:
        if 'period_for_upgrade' in context.user_data and 'traffic_for_upgrade' in context.user_data:
            period_for_upgrade = context.user_data['period_for_upgrade']
            traffic_for_upgrade = context.user_data['traffic_for_upgrade']

            sqlite_manager.update({'User': {'period': int(period_for_upgrade), 'traffic': int(traffic_for_upgrade)}},
                                  where=f'chat_id = {query.message.chat_id}')

        context.user_data['personalization_client_lu_id'] = int(query.data.replace('upgrade_service_customize_', ''))

    id_ = context.user_data['personalization_client_lu_id']
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


    sqlite_manager.update({'User': {'traffic':traffic, 'period': period}},where=f'chat_id = {chat_id}')
    price = ranking_manage.discount_calculation(chat_id, traffic, period)

    text = ('*• تو این بخش میتونید سرویس مورد نظر خودتون رو تمدید کنید و یا ارتقا دهید:*'
            '\n*نکته: اگر سرویس شما به اتمام نرسیده، مشخصات زیر به سرویس اضافه میشن.*'
            f'\n\nحجم سرویس: {traffic}GB'
            f'\nدوره زمانی: {period} روز'
            f'\n*قیمت: {price:,}*')
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
    query.edit_message_text(text=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))


def payment_page_upgrade(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    id_ = int(query.data.replace('service_upgrade_', ''))
    try:
        package = sqlite_manager.select(table='User', where=f'chat_id = {chat_id}')
        keyboard = [
            [InlineKeyboardButton("پرداخت از کیف پول", callback_data=f'payment_by_wallet_upgrade_service_{id_}'),
             InlineKeyboardButton("کارت به کارت", callback_data=f'upg_ser_by_card{id_}')],
            [InlineKeyboardButton("برگشت ↰", callback_data="my_service")]
        ]

        price = ranking_manage.discount_calculation(chat_id, package[0][5], package[0][6])
        text = (f"<b>❋ بسته انتخابی شامل مشخصات زیر میباشد:</b>\n"
                f"\nدوره زمانی: {package[0][6]} روز"
                f"\nترافیک (حجم): {package[0][5]} گیگابایت"
                f"\nحداکثر کاربر مجاز: ♾️"
                f"\n<b>قیمت: {price:,} تومان</b>"
                f"\n\nموجودی کیف پول: {int(package[0][10]):,}"
                f"\n\n<b>⤶ برای پرداخت میتونید یکی از روش های زیر رو استفاده کنید:</b>")
        query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        print(e)
        ready_report_problem_to_admin(context, text='PAYMENT PAGER FOR UPGRADE (payment_page_upgrade)', chat_id=chat_id, error=e)
        something_went_wrong(update, context)


def pay_page_get_evidence_for_upgrade(update, context):
    query = update.callback_query
    id_ = int(query.data.replace('upg_ser_by_card', ''))
    chat_id = query.message.chat_id

    try:
        package = sqlite_manager.select(table='User', where=f'chat_id = {chat_id}')
        context.user_data['package'] = package
        context.user_data['purchased_id'] = id_
        keyboard = [[InlineKeyboardButton("صفحه اصلی ⤶", callback_data="send_main_message")]]
        price = ranking_manage.discount_calculation(chat_id, package[0][5], package[0][6])
        text = (f"\n\nمدت اعتبار فاکتور: 10 دقیقه"
                f"\nسرویس: {package[0][6]} روز - {package[0][5]} گیگابایت"
                f"\n*قیمت*: `{price:,}`* تومان *"
                f"\n\n*• لطفا مبلغ رو به شماره‌حساب زیر واریز کنید و اسکرین‌شات یا شماره‌پیگیری رو بعد از همین پیام ارسال کنید، اطمینان حاصل کنید ربات درخواست رو ثبت کنه.*"
                f"\n\n`6219861938619417` - امیرحسین نجفی"
                f"\n\n*• بعد از تایید شدن پرداخت، سرویس برای شما ارسال میشه، زمان تقریبی 5 دقیقه الی 3 ساعت.*")
        context.bot.send_message(chat_id=query.message.chat_id, text=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        query.answer('فاکتور برای شما ارسال شد.')
        return GET_EVIDENCE
    except Exception as e:
        print(e)
        ready_report_problem_to_admin(context, text='PAY PAGE GET EVIDENCE UPGRADE', chat_id=query.message.chat_id, error=e)
        something_went_wrong(update, context)


def send_evidence_to_admin_for_upgrade(update, context):
    user = update.message.from_user

    try:
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
            upgrade_service = task.upgrade_service(context, purchased_id)
            keyboard = []
            text_ = f'سرویس با موفقیت ارتقا یافت✅'
            text = '- The user rank was sufficient to get the service without confirm [UPGRADE SERVICE]\n\n'

        text += f"Name: {user['first_name']}\nUserName: @{user['username']}\nID: {user['id']}\n\n"
        service_detail = f"\n\nPeriod: {package[0][6]} Day\nTraffic: {package[0][5]}GB\nPrice: {price:,} T"

        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            text += f"caption: {update.message.caption}" or 'Witout caption!'
            text += service_detail
            context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=file_id, caption=text, reply_markup=InlineKeyboardMarkup(keyboard))
            update.message.reply_text(text_, parse_mode='html')

        elif update.message.text:
            text += f"Text: {update.message.text}{service_detail}"
            context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, reply_markup=InlineKeyboardMarkup(keyboard))
            update.message.reply_text(text_, parse_mode='html')

        else:
            update.message.reply_text('مشکلی وجود داره!')

        context.user_data.clear()
        return ConversationHandler.END

    except Exception as e:
        ready_report_problem_to_admin(context, 'SEND EVIDENCE TO ADMIN', user['id'], e)
        text = ("مشکلی وجود داشت!"
                "گزارش به ادمین ها ارسال شد، نتیجه به زودی بهتون اعلام میشه")
        keyboard = [[InlineKeyboardButton("برگشت ↰", callback_data="main_menu")]]
        update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
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

def apply_card_pay_lu(update, context):
    query = update.callback_query
    try:
        if 'accept_card_pay_lu_' in query.data or 'refuse_card_pay_lu_' in query.data:
            status = query.data.replace('card_pay_lu_', '')
            keyboard = [[InlineKeyboardButton("YES", callback_data=f"ok_card_pay_lu_{status}")]
                , [InlineKeyboardButton("NO", callback_data=f"cancel_pay")]]
            query.answer('Confirm Pleas!')
            context.bot.send_message(text='Are You Sure?', reply_markup=InlineKeyboardMarkup(keyboard), chat_id=ADMIN_CHAT_ID)
        elif 'ok_card_pay_lu_accept_' in query.data:
            id_ = int(query.data.replace('ok_card_pay_lu_accept_', ''))
            upgrade_service = task.upgrade_service(context, id_)
            context.bot.send_message(text='سفارش شما برای تمدید و یا ارتقا با موفقیت تایید شد ✅', chat_id=upgrade_service[0])
            query.answer('Done ✅')
            query.delete_message()

        elif 'ok_card_pay_lu_refuse_' in query.data:
            id_ = int(query.data.replace('ok_card_pay_lu_refuse_', ''))
            get_client = sqlite_manager.select(table='Purchased', where=f'id = {id_}')

            keyboard = [[InlineKeyboardButton("پشتیبانی", url="@Fupport")]]

            context.bot.send_message(text='درخواست شما برای سفارش یا ارتقا سرویس تایید نشد!\nاگر فکر میکنید خطایی رخ داده با پشتیبانی در ارتباط باشید:', chat_id=get_client[0][4], reply_markup=InlineKeyboardMarkup(keyboard))
            query.answer('Done ✅')
            query.delete_message()

            record_operation_in_file(chat_id=get_client[0][4], price=0,
                                     name_of_operation=f'تمدید یا ارتقا سرویس {get_client[0][9]}', operation=0,
                                     status_of_pay=0, context=context)

        elif 'cancel_pay' in query.data:
            query.answer('Done ✅')
            query.delete_message()
    except Exception as e:
        ready_report_problem_to_admin(context, text='APPLY CARD PAY LU (FOR UPGRADE)', chat_id=query.message.chat_id, error=e)
        print('errot:', e)


def get_free_service(update, context):
    query = update.callback_query
    user = query.from_user
    try:
        sqlite_manager.update({'User': {'free_service': 1}}, where=f"chat_id = {user['id']}")
        ex = sqlite_manager.insert('Purchased', rows=[
            {'active': 1, 'status': 1, 'name': user["first_name"], 'user_name': user["username"],
             'chat_id': int(user["id"]), 'product_id': 1, 'inbound_id': 1, 'date': datetime.now(),
             'notif_day': 0, 'notif_gb': 0}])
        send_clean_for_customer(update.callback_query, context, ex)
        context.bot.send_message(ADMIN_CHAT_ID, f'🟢 User {user["name"]} With ID: {user["id"]} TAKE A FREE SERVICE')
        keyboard = [[InlineKeyboardButton("برگشت ⤶", callback_data="main_menu")]]
        query.edit_message_text('سرویس تست با موفقیت برای شما ارسال شد ✅', reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        ready_report_problem_to_admin(context, text='TAKE A FREE SERVICE', chat_id=query.message.chat_id, error=e)
        query.answer('ببخشید، مشکلی وجود داشت!')


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
         InlineKeyboardButton("اضافه کردن تیکت", callback_data=f"ticket_send_ticket")],
        [InlineKeyboardButton("برگشت ⤶", callback_data="main_menu")]
    ]
    query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')


def show_help(update, context):
    query = update.callback_query
    help_what = query.data.replace('_help', '')
    if help_what == 'apps':
        text = "<b>از طریق گزینه های زیر به صفحه رسمی نرم افزار برید \nو نسخه مرتبط با دستگاه خودتون رو دانلود کنید.</b>"
        keyboard = [
            [InlineKeyboardButton("V2RayNG", url="https://play.google.com/store/apps/details?id=com.v2ray.ang&hl=en&gl=US"),
             InlineKeyboardButton("اندروید:", callback_data="just_for_show")],
            [InlineKeyboardButton("V2Box", url="https://apps.apple.com/us/app/v2box-v2ray-client/id6446814690"),
             InlineKeyboardButton("آیفون و مک:", callback_data="just_for_show")],
            [InlineKeyboardButton("V2RayN (core)", url="https://github.com/2dust/v2rayN/releases"),
             InlineKeyboardButton("ویندوز:", callback_data="just_for_show")],
            [InlineKeyboardButton("برگشت ⤶", callback_data="guidance")]
        ]
    elif help_what == 'personalize':
        text = ("<b>شخصی سازی ربات از قسمت تنظیمات قابل انجام است</b>"
                f"\n\n<b>• کیف پول:</b>"
                f"\nبا شارژ کردن کیف پول خودتون میتونید تمام تراکنش ها رو بدون نیاز به تایید و بدون تاخیر انجام بدید."
                f"\nهمچنین بازپرداخت حذف سرویس به کیف پولتون برمیگرده."
                f"\nاگر سرویس شما قطع بشه و مشکل از سمت سرور باشه، مبلغ خسارت محاسبه و به کیف پول اضافه میشه."
                f"\n\n<b>• نوتیفیکبشن:</b>"
                f"\nبا تنظیم نوتیفیکیشن ربات اعلان های مربوط به تاریخ انقضا سرویس و همچنین حجم ترافیک باقیمونده شما رو به اطلاعاتون میرسونه."
                f"\nربات 5 دقیقه یک بار اطلاعات رو بررسی میکنه."
                f"\n\n<b>• تراکنش ها:</b>"
                f"\nهمه تراکنش های شما توسط ربات ثبت میشه و همیشه میتونید بهشون دسترسی داشته باشید."
                )
        keyboard = [
            [InlineKeyboardButton("تنظیمات ⚙️", callback_data="setting")],
            [InlineKeyboardButton("برگشت ⤶", callback_data="guidance")]]

    elif help_what == 'robots_service':
        text = ("<b>ربات سرویس های مختلفی ارائه میده، لطفا سرویس ها رو بررسی کنید و مطمئن بشید کدوم مناسب شماست</b>"
                "\n\n<b>• سرویس های آماده:</b>"
                "\nاین سرویس ها حجم و ترافیک مشخصی دارن و انتخاب راحتی هستن، مانند:\n - سرویس 30 روزه - 15 گیگابایت - 45,000 تومن"
                "\n\n<b>• سرویس دلخواه:</b>"
                "\nاین سرویس به شما اجازه میده حجم و ترافیک رو مطابق میل خودتون تنظیم کنید و انتخاب شخصی سازی شده داشته باشید"
                "\n\n<b>• سرویس ساعتی:</b>"
                "\nاین سرویس براساس مصرف ترافیک شما در هر ساعت هزینه رو از کیف پول کم میکنه، محدودیت حجم و زمان نداره و با تموم شدن اعتبار کیف پول، غیرفعال میشه."
                )

        keyboard = [
            [InlineKeyboardButton("🛒 خرید سرویس", callback_data="select_server")],
            [InlineKeyboardButton("برگشت ⤶", callback_data="guidance")]]

    else:  # help_what == 'people_ask'
        text = "<b>در این قسمت میتونید جواب سوالات متداول رو پیدا کنید:</b>"

        keyboard = [
            [InlineKeyboardButton("استفاده از vpn مصرف اینترنت را افزایش میدهد؟", callback_data="ask_vpn_increase_traffic")],
            [InlineKeyboardButton("میتوانم سرویس خریداری شده را حذف و مبلغ رو برگردانم؟", callback_data="ask_can_i_remove_service")],
            [InlineKeyboardButton("در صورت قطعی و فیلتر شدن سرویس، تکلیف چیست؟", callback_data="ask_what_if_service_blocked")],
            [InlineKeyboardButton("چرا با سرویس ها، نمیتوانم وارد سایت های ایرانی شوم؟", callback_data="ask_persian_web_dont_open")],
            [InlineKeyboardButton("برگشت ⤶", callback_data="guidance")]]

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')


def people_ask(update, context):
    query = update.callback_query
    help_what = query.data.replace('ask_', '')

    if help_what == 'vpn_increase_traffic':
        text = ("<b>خیر، به طول کلی استفاده از vpn باعث افزایش مصرف ترافیک نمیشه!"
                "\n\nدر جهان، vpn برای افزایش امنیت استفاده میشه، بعضی از vpn ها رمزنگاری رو به درخواست های شما اضافه میکنن"
                " که باعث امنیت بالاتر میشه و حجم مصرف رو مقدار خیلی کمی افزایش میده."
                "\n\nدر دیگر موارد، vpn ها مصرف ترافیک رو افزایش نمیدن</b>")

    elif help_what == 'can_i_remove_service':
        text = "<b>بله، میتونید به هر دلیلی سرویس مورد نظر خودتون رو بعد از خرید حذف کنید و مبلغ باقی مونده از سرویس به حساب شما برمیگرده.</b>"

    elif help_what == 'what_if_service_blocked':
        text = ("<b>اگر سرویس شما بلاک بشه، بعد از حل مشکل مبلغ خسارت حساب میشه و به کیف پول شما اضافه میشه."
                "همچنین فورا یک سرویس جدید از طریق ایمیل و ربات براتون ارسال میشه که میتونید استفاده کنید.</b>")

    else:  # help_what == 'persian_web_dont_open'
        text = "<b>دلیل این امر، افزایش امنیت سرویس ها است، بعضی از سایت های ایرانی ip شمارو در صورتی که از ایران نباشه گزارش میکنن و این باعث فیلتر شدن سرور ها میشه.</b>"

    keyboard = [
        [InlineKeyboardButton("برگشت ⤶", callback_data="people_ask_help")]
    ]
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')


def support(update, context):
    query = update.callback_query
    keyboard = [[InlineKeyboardButton("پرایوت", url="https://t.me/fupport")],
                [InlineKeyboardButton("برگشت ⤶", callback_data="main_menu")]]
    query.edit_message_text('از طریق روش های زیر میتونید با پشتیبان صحبت کنید', reply_markup=InlineKeyboardMarkup(keyboard))


def disable_service_in_data_base(context, list_of_notification, user, not_enogh_credit=False):
    print(list_of_notification, user)
    text = ("🔴 اطلاع رسانی اتمام سرویس"
            f"\nدرود {list_of_notification[0][3]} عزیز، سرویس شما با نام {user[2]} به پایان رسید!"
            f"\nدر صورتی که تمایل دارید نسبت به بررسی و یا تمدید سرویس اقدام کنید.")

    if not_enogh_credit:
        text = ("🔴 اطلاع رسانی اتمام سرویس و تمدید خودکار ناموفق"
                f"\nدرود {list_of_notification[0][3]} عزیز، سرویس شما با نام {user[2]} به پایان رسید!"
                f"\nاعتبار شما برای تمدید خودکار سرویس کافی نبود!")

    keyboard = [
        [InlineKeyboardButton("خرید سرویس جدید", callback_data=f"select_server"),
         InlineKeyboardButton("تمدید همین سرویس", callback_data=f"upgrade_service_customize_{user[0]}")],
        [InlineKeyboardButton("❤️ تجربه استفاده از فری‌بایت رو به اشتراک بگذارید:", callback_data=f"just_for_show")],
        [InlineKeyboardButton("معمولی بود",
                              callback_data=f"rate_ok&{list_of_notification[0][0]}_{user[0]}"),
         InlineKeyboardButton("عالی بود",
                              callback_data=f"rate_perfect&{list_of_notification[0][0]}_{user[0]}")],
        [InlineKeyboardButton("ناامید شدم",
                              callback_data=f"rate_bad&{list_of_notification[0][0]}_{user[0]}"),
         InlineKeyboardButton("نظری ندارم",
                              callback_data=f"rate_haveNotIdea&{list_of_notification[0][0]}_{user[0]}")]
    ]
    context.bot.send_message(user[1], text=text, reply_markup=InlineKeyboardMarkup(keyboard))
    sqlite_manager.update({'Purchased': {'status': 0}}, where=f'id = {user[0]}')

    utilities.report_status_to_admin(context, text=f'The user service has ended.\n'
                                                   f'User Name: {list_of_notification[0][3]}'
                                                   f'\nService id: {user[0]}', chat_id=list_of_notification[0][0])


def check_all_configs(context, context_2=None):
    if context_2:
        context = context_2

    get_all = api_operation.get_all_inbounds()
    get_from_db = sqlite_manager.select(column='id,chat_id,client_email,status,date,notif_day,notif_gb,auto_renewal,product_id,inbound_id,client_id', table='Purchased', where='active=1')
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
                                period = datetime.now(pytz.timezone('Asia/Tehran')) + timedelta(days=new_expiry_datetime)
                                my_data = int(period.timestamp() * 1000)
                                price = ranking_manage.discount_calculation(list_of_notification[0][0], admin_task.traffic_to_gb(client['total']), new_expiry_datetime)

                                if list_of_notification[0][6] >= price:
                                    get_server_domain = sqlite_manager.select(column='server_domain', table='Product',
                                                                              where=f'id = {user[8]}')

                                    text = ("🟢 اطلاع رسانی اتمام سرویس و تمدید خودکار"
                                            f"\nدرود {list_of_notification[0][3]} عزیز، سرویس شما با نام {user[2]} به پایان رسید!"
                                            f"\nسرویس شما به صورت خودکار تمدید شد، میتونید جزئیات سرویس رو بررسی کنید.")
                                    keyboard = [[InlineKeyboardButton("مشاهده جزئیات سرویس", callback_data=f"view_service_{user[2]}")]]

                                    # print(api_operation.reset_client_traffic(user[9], user[2], get_server_domain[0][0]))

                                    data = {
                                        "id": int(user[9]),
                                        "settings": "{{\"clients\":[{{\"id\":\"{0}\",\"alterId\":0,"
                                                    "\"email\":\"{1}\",\"limitIp\":0,\"totalGB\":{2},\"expiryTime\":{3},"
                                                    "\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}}]}}".format(
                                            user[10], user[2],
                                            traffic, my_data)}

                                    print(api_operation.update_client(user[10], data, get_server_domain[0][0]))

                                    wallet_manage.less_from_wallet(list_of_notification[0][0], price, user_detail={'name': list_of_notification[0][0],'username': list_of_notification[0][0]})

                                    sqlite_manager.update({'Purchased': {'date': datetime.now(
                                        pytz.timezone('Asia/Tehran')), 'notif_day': 0, 'notif_gb': 0}}
                                        , where=f'client_email = "{user[2]}"')

                                    context.bot.send_message(text=text, chat_id=list_of_notification[0][0], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')

                                    record_operation_in_file(chat_id=list_of_notification[0][0], price=price,
                                                             name_of_operation=f'تمدید یا ارتقا سرویس {user[2]}',
                                                             operation=0,
                                                             status_of_pay=1, context=context)

                                    report_status_to_admin(context,
                                                           text=f'User Upgrade Service automate\nService Name: {user[2]}',
                                                           chat_id=list_of_notification[0][0])
                                else:
                                    disable_service_in_data_base(context, list_of_notification, user, not_enogh_credit=True)


                        elif client['enable'] and not user[3]:
                            sqlite_manager.update(
                                {'Purchased': {'status': 1, 'date': datetime.now(pytz.timezone('Asia/Tehran')), 'notif_day': 0, 'notif_gb': 0}}
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
                            traffic_left = total_traffic - usage_traffic

                            keyboard = [[InlineKeyboardButton("مشاهده جزئیات سرویس", callback_data=f"view_service_{user[2]}"),
                                         InlineKeyboardButton("تمدید یا ارتقا سرویس", callback_data=f"upgrade_service_customize_{user[0]}")]]

                            if not user[5] and time_left <= list_of_notification[0][2]:
                                text = ("🔵 اطلاع رسانی تاریخ انقضا سرویس"
                                        f"\nدرود {list_of_notification[0][3]} عزیز، از سرویس شما با نام {user[2]} کمتر از {int(time_left) + 1} روز باقی مونده."
                                        f"\nدر صورتی که تمایل دارید نسبت به بررسی و یا تمدید سرویس اقدام کنید.")
                                context.bot.send_message(user[1], text=text, reply_markup=InlineKeyboardMarkup(keyboard))
                                sqlite_manager.update({'Purchased': {'notif_day': 1}},where=f'id = "{user[0]}"')

                            if not user[6] and traffic_percent >= list_of_notification[0][1]:
                                text = ("🔵 اطلاع رسانی حجم سرویس"
                                        f"\nدرود {list_of_notification[0][3]} عزیز، شما {int(traffic_percent)} درصد حجم ترافیک سرویس {user[2]} رو مصرف کردید، "
                                        f"\nحجم باقی مونده از سرویس {format_traffic(traffic_left)} است. "
                                        f"\nدر صورتی که تمایل دارید نسبت به بررسی و یا تمدید سرویس اقدام کنید.")
                                context.bot.send_message(user[1], text=text, reply_markup=InlineKeyboardMarkup(keyboard))
                                sqlite_manager.update({'Purchased': {'notif_gb': 1}},where=f'id = "{user[0]}"')


def rate_service(update, context):
    query = update.callback_query
    try:
        purchased_id = int(re.sub(r'rate_(.*)_', '', query.data))
        check = query.data.replace('_', ' ').replace('&', ' ').split(' ')
        text = ('The user rated the service\n'
                f'User Rate: {check[1]}\n'
                f'Service Id: {check[3]}')
        utilities.report_status_to_admin(context, text, chat_id=check[2])

        server_name = sqlite_manager.select(column='client_email', table='Purchased', where=f'id = {purchased_id}')[0][0]
        text = ("🔴 اطلاع رسانی اتمام سرویس"
                f"\nدرود {query.from_user['name']} عزیز، سرویس شما با نام {server_name} به پایان رسید!"
                f"\nدر صورتی که تمایل دارید نسبت به بررسی و یا تمدید سرویس اقدام کنید.")

        keyboard = [
            [InlineKeyboardButton("خرید سرویس جدید", callback_data=f"select_server"),
             InlineKeyboardButton("تمدید همین سرویس", callback_data=f"upgrade_service_customize_{purchased_id}")]]
        query.answer('متشکریم ❤️')
        query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        keyboard = [
            [InlineKeyboardButton("خرید سرویس جدید", callback_data=f"select_server")]]
        query.edit_message_text(text='مشکلی وجود داشت!', reply_markup=InlineKeyboardMarkup(keyboard))
        ready_report_problem_to_admin(context, 'RATE SERVICE', query.message.chat_id, e)


def setting(update, context):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("نوتیفیکیشن سرویس", callback_data="service_notification"),
         InlineKeyboardButton("نوتیفیکیشن کیف‌پول", callback_data="wallet_notification")],
        [InlineKeyboardButton("• تراکنش های مالی", callback_data="financial_transactions")],
        [InlineKeyboardButton("برگشت ↰", callback_data="main_menu")]
    ]
    query.edit_message_text(text='*در این قسمت میتونید تنظیمات ربات رو مشاهده و یا شخصی سازی کنید:*', parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))


def change_notif(update, context):
    query = update.callback_query
    get_data_from_db = sqlite_manager.select(table='User', where=f'chat_id = {query.message.chat_id}')
    text = keyboard = None

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

        sqlite_manager.update({'User': {'notification_gb':traffic, 'notification_day': period,
                                        'notification_wallet': wallet_notif}},where=f'chat_id = {query.message.chat_id}')

        if any(query.data.startswith(prefix) for prefix in ['service_notification', 'notif_traffic_low_', 'notif_traffic_high_', 'notif_day_low_', 'notif_day_high_']):

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

        elif any(query.data.startswith(call) for call in ['wallet_notification', 'notif_wallet_low_', 'notif_wallet_high_']):
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
        query.answer('شما نمیتونید ولوم رو کمتر یا بیشتر از مقدار مجاز قرار بدید!')
        print(e)


def get_pay_file(update, context):
    query = update.callback_query
    with open(f'financial_transactions/{query.message.chat_id}.txt', 'r', encoding='utf-8') as file:
        context.bot.send_document(chat_id=query.message.chat_id, document= file,
                                  filename=f'All transactions of {query.from_user["name"]}.txt')
    query.answer('فایل برای شما ارسال شد!')


def financial_transactions(update, context):
    query = update.callback_query
    try:
        keyboard = [
            [InlineKeyboardButton("دریافت فایل کامل", callback_data="get_pay_file")]
        ]
        with open(f'financial_transactions/{query.message.chat_id}.txt', 'r', encoding='utf-8') as e:
            get_factors = e.read()

        data = query.data.replace('financial_transactions', '')
        number_in_page = 15
        get_limit = int(data) if data else number_in_page

        list_of_t = get_factors.split('\n\n')
        list_of_t.reverse()

        get_purchased = list_of_t[get_limit - number_in_page:get_limit]
        get_purchased.reverse()


        if len(list_of_t) > number_in_page:
            keyboard_backup = []
            keyboard_backup.append(InlineKeyboardButton("قبل ⤌", callback_data=f"financial_transactions{get_limit - number_in_page}")) if get_limit != number_in_page else None
            keyboard_backup.append(InlineKeyboardButton(f"صفحه {int(get_limit / number_in_page)}", callback_data="just_for_show"))
            keyboard_backup.append(InlineKeyboardButton("⤍ بعد", callback_data=f"financial_transactions{get_limit + number_in_page}")) if get_limit < len(list_of_t) else None
            keyboard.append(keyboard_backup)

        keyboard.append([InlineKeyboardButton("برگشت ↰", callback_data="setting")])

        query.edit_message_text(text=f"لیست تراکنش های مالی شما: \n" + "\n\n".join(get_purchased), reply_markup=InlineKeyboardMarkup(keyboard))


    except FileNotFoundError:
        query.answer('شما تا به حال تراکنشی نداشتید!')
    except Exception as e:
        query.answer('مشکلی وجود داشت!')
        ready_report_problem_to_admin(context,chat_id=query.message.chat_id, error=e, text='Error In Financial Transactions')


def start_timer(update, context):
    context.job_queue.run_repeating(check_all_configs, interval=300, first=0, context=context.user_data)
    update.message.reply_text('Timer started! ✅')


def wallet_page(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    try:
        get_credit = sqlite_manager.select(column='wallet', table='User', where=f'chat_id = {chat_id}')[0][0]
        lasts_operation = sqlite_manager.select(table='Credit_History', where=f'chat_id = {chat_id} and active = 1',
                                                order_by='id DESC', limit=5)

        if lasts_operation:
            last_op = human_readable(f'{lasts_operation[0][7]}')
            last_5 = "• تراکنش های اخیر:\n"
            last_5 += "\n".join([f"{'💰 دریافت' if op[4] else '💸 برداشت'} {int(op[5]):,} تومان - {human_readable(op[7])}" for op in lasts_operation])

        else:
            last_op ='شما تا به حال تراکنشی در کیف پول نداشتید!'
            last_5 = ''

        keyboard = [
            [InlineKeyboardButton("تازه سازی ⟳", callback_data=f"wallet_page"),
             InlineKeyboardButton("افزایش موجودی ↟", callback_data=f"buy_credit_volume")],
            [InlineKeyboardButton("مشاهده تراکنش های کیف پول", callback_data=f"financial_transactions_wallet")],
            [InlineKeyboardButton("برگشت ↰", callback_data="main_menu")]]

        text_ = (
            f"<b>اطلاعات کیف پول شما:</b>"
            f"\n\n• موجودی حساب: {int(get_credit):,} تومان"
            f"\n• آخرین تراکنش: {last_op}"
            f"\n\n{last_5}"
        )
        query.edit_message_text(text=text_, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
    except Exception as e:
        if "specified new message content and reply markup are exactly the same" in str(e):
            print(e)
            return query.answer('بروزرسانی نشد، احتمالا اطلاعات تغییری نکرده')
        query.answer('مشکلی وجود داشت، گزارش به ادمین ارسال شد')
        ready_report_problem_to_admin(context, chat_id=query.message.chat_id, error=e, text='WALLET PAGE')


def financial_transactions_wallet(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    try:
        lasts_operation = sqlite_manager.select(table='Credit_History', where=f'chat_id = {chat_id} and active = 1',
                                                order_by='id DESC', limit=100)

        if lasts_operation:
            last_5 = "• تراکنش های کیف پول شما:\n\n"
            last_5 += "\n".join([f"{'💰 دریافت' if op[4] else '💸 برداشت'} {op[5]:,} تومان - {human_readable(op[7])}" for op in lasts_operation])
        else:
            last_5 = 'شما تا به حال تراکنشی در کیف پول نداشتید!'

        keyboard = [
            [InlineKeyboardButton("تازه سازی ⟳", callback_data=f"financial_transactions_wallet")],
            [InlineKeyboardButton("برگشت ↰", callback_data="wallet_page")]]

        text_ = f"\n\n{last_5}"
        query.edit_message_text(text=text_, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')

    except Exception as e:
        query.answer('بروزرسانی نشد، احتمالا اطلاعات تغییری نکرده')
        print(e)


def buy_credit_volume(update, context):
    query = update.callback_query
    try:
        if query.data == "buy_credit_volume":
            sqlite_manager.insert(table='Credit_History', rows=[{'active': 0, 'chat_id': query.message.chat_id, 'value': 25_000,
                                                                 'name': query.from_user.name, 'user_name': query.from_user.username,
                                                                 'operation': 1}])

        get_credit = sqlite_manager.select(column='value, id', table='Credit_History', where=f'chat_id = {query.message.chat_id}',
                                           order_by='id DESC', limit=1)
        credit_id = get_credit[0][1]
        value = get_credit[0][0]

        if 'value_low_5000' in query.data:
            value_low = int(query.data.replace('value_low_', ''))
            value = value - value_low
            value = value if value >= 1 else 5000
        elif 'value_high_5000' in query.data:
            value_high = int(query.data.replace('value_high_', ''))
            value = value + value_high
            value = value if value <= 2_000_000 else 2_000_000
        elif 'set_credit_' in query.data:
            value = int(query.data.replace('set_credit_', ''))

        sqlite_manager.update({'Credit_History': {'value':value}},where=f'id = {credit_id}')

        text = ('*• مشخص کنید چه مقدار اعتبار به کیف پولتون اضافه بشه:*'
                f'*\n\n• مبلغ: {value:,} *تومان'
                )
        keyboard = [
            [InlineKeyboardButton("«", callback_data="value_low_50000"),
             InlineKeyboardButton("‹", callback_data="value_low_5000"),
             InlineKeyboardButton(f"{value:,}", callback_data="just_for_show"),
             InlineKeyboardButton("›", callback_data="value_high_5000"),
             InlineKeyboardButton("»", callback_data="value_high_50000")],
            [InlineKeyboardButton("250,000 تومن", callback_data="set_credit_250000"),
             InlineKeyboardButton("100,000 تومن", callback_data="set_credit_100000")],
            [InlineKeyboardButton("1,000,000 تومن", callback_data="set_credit_1000000"),
             InlineKeyboardButton("500,000 تومن", callback_data="set_credit_500000")],
            [InlineKeyboardButton("✓ تایید و ادامه", callback_data=f"pay_way_for_credit_{credit_id}")],
            [InlineKeyboardButton("برگشت ↰", callback_data="wallet_page")]
        ]
        query.edit_message_text(text=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        query.answer('بروزرسانی نشد، احتمالا اطلاعات تغییری نکرده')
        print(e)


def pay_way_for_credit(update, context):
    query = update.callback_query
    id_ = int(query.data.replace('pay_way_for_credit_', ''))
    try:
        package = sqlite_manager.select(column='value', table='Credit_History', where=f'id = {id_}')
        keyboard = [
            [InlineKeyboardButton("کارت به کارت", callback_data=f'pay_by_card_for_credit_{id_}')],
            [InlineKeyboardButton("برگشت ↰", callback_data="buy_credit_volume")]
        ]

        text = (f"<b>❋ مبلغ انتخاب شده رو برای اضافه کردن به کیف پول تایید میکنید؟:</b>\n"
                f"\n<b>مبلغ: {package[0][0]:,} تومان</b>"
                f"\n\n<b>⤶ برای پرداخت میتونید یکی از روش های زیر رو استفاده کنید:</b>")
        query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        print(e)
        something_went_wrong(update, context)


def pay_by_card_for_credit(update, context):
    query = update.callback_query
    id_ = int(query.data.replace('pay_by_card_for_credit_', ''))
    try:
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
        context.bot.send_message(chat_id=query.message.chat_id, text=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        query.answer('فاکتور برای شما ارسال شد.')
        return GET_EVIDENCE_CREDIT
    except Exception as e:
        print(e)
        something_went_wrong(update, context)


def pay_by_card_for_credit_admin(update, context):
    user = update.message.from_user
    try:
        package = context.user_data['credit_package']
        credit_id = context.user_data['credit_id']
        price = ranking_manage.discount_calculation(user['id'], direct_price=package[0][0], without_off=True)


        if not ranking_manage.enough_rank('GET_SERVICE_WITHOUT_CONFIRM', user['id']):
            keyboard = [[InlineKeyboardButton("Accept ✅", callback_data=f"accept_card_pay_credit_{credit_id}")],
                        [InlineKeyboardButton("Refuse ❌", callback_data=f"refuse_card_pay_credit_{credit_id}")],
                        [InlineKeyboardButton("Hide buttons", callback_data=f"hide_buttons")]]
            text_ = f'<b>درخواست شما با موفقیت ثبت شد✅\nنتیجه از طریق همین ربات بهتون اعلام میشه</b>'
            text = "- Check the new payment to the card [CHARGE CREDIT WALLET]:\n\n"

        else:
            add_credit = add_credit_to_wallet(context, credit_id)
            keyboard = []
            text_ = f'کیف پول شما با موفقیت شارژ شد✅'
            text = '- The user rank was sufficient to get the service without confirm [CHARGE CREDIT WALLET]\n\n'

        text += f"Name: {user['first_name']}\nUserName: @{user['username']}\nID: {user['id']}\n\n"

        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            text += f"caption: {update.message.caption}" or 'Witout caption!'
            text += f"\n\nPrice: {price:,} T"
            context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=file_id, caption=text, reply_markup=InlineKeyboardMarkup(keyboard))
            update.message.reply_text(text_, parse_mode='html')
        elif update.message.text:
            text += f"Text: {update.message.text}\n\nPrice: {price:,} T"
            context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, reply_markup=InlineKeyboardMarkup(keyboard))
            update.message.reply_text(text_, parse_mode='html')
        else:
            update.message.reply_text('مشکلی وجود داره!')

        context.user_data.clear()
        return ConversationHandler.END
    except Exception as e:
        ready_report_problem_to_admin(context, 'SEND EVIDENCE FOR CHARGE CREDIT TO ADMIN', update.message.from_user['id'], e)
        update.message.reply_text('مشکلی در ارسال پیش اومد!\nگزارش به ادمین ارسلا شد و به زودی نتیجه بهتون اعلام میشه.')


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


def add_credit_to_wallet(context, id_):
    get_credit = sqlite_manager.select(column='chat_id,value', table='Credit_History', where=f'id = {id_}')
    wallet_manage.add_to_wallet_without_history(get_credit[0][0], get_credit[0][1])

    sqlite_manager.update({'Credit_History': {'active': 1, 'date': datetime.now(pytz.timezone('Asia/Tehran'))}}
                          , where=f'id = "{id_}"')

    record_operation_in_file(chat_id=get_credit[0][0], price=get_credit[0][1],
                             name_of_operation=f'واریز به کیف پول', operation=1,
                             status_of_pay=1, context=context)

    context.bot.send_message(ADMIN_CHAT_ID, '🟢 WALLET OPERATOIN SUCCESSFULL')
    return get_credit[0][0]


def apply_card_pay_credit(update, context):
    query = update.callback_query
    try:
        if 'accept_card_pay_credit_' in query.data or 'refuse_card_pay_credit_' in query.data:
            status = query.data.replace('card_pay_credit_', '')
            keyboard = [[InlineKeyboardButton("YES", callback_data=f"ok_card_pay_credit_{status}")]
                , [InlineKeyboardButton("NO", callback_data=f"cancel_pay")]]
            query.answer('Confirm Pleas!')
            context.bot.send_message(text='Are You Sure?', reply_markup=InlineKeyboardMarkup(keyboard), chat_id=ADMIN_CHAT_ID)
        elif 'ok_card_pay_credit_accept_' in query.data:
            id_ = int(query.data.replace('ok_card_pay_credit_accept_', ''))

            return_chat_id = add_credit_to_wallet(context, id_)

            context.bot.send_message(text='سفارش شما برای واریز وجه به کیف پول با موفقیت تایید شد ✅', chat_id=return_chat_id)
            query.answer('Done ✅')
            query.delete_message()


        elif 'ok_card_pay_credit_refuse_' in query.data:
            id_ = int(query.data.replace('ok_card_pay_credit_refuse_', ''))
            get_credit = sqlite_manager.select(column='chat_id,value', table='Credit_History', where=f'id = {id_}')
            context.bot.send_message(text=f'متاسفانه درخواست شما برای واریز به کیف پول پذیرفته نشد❌\n ارتباط با پشتیبانی: \n @Fupport ', chat_id=get_credit[0][0])
            query.answer('Done ✅')
            query.delete_message()

            record_operation_in_file(chat_id=get_credit[0][0], price=get_credit[0][1],
                                     name_of_operation=f'واریز به کیف پول', operation=1,
                                     status_of_pay=0, context=context)

            sqlite_manager.delete({'Credit_History': ["id", id_]})
        elif 'cancel_pay' in query.data:
            query.answer('Done ✅')
            query.delete_message()
    except Exception as e:
        ready_report_problem_to_admin(context, 'APPLY CARD PAY FOR CREDIT', query.message.chat_id, e)
        print('errot:', e)


def pay_from_wallet(update, context):
    query = update.callback_query
    user = query.from_user
    try:
        get_wallet = sqlite_manager.select(table='User', column='wallet', where=f'chat_id = {user["id"]}')

        if 'payment_by_wallet_upgrade_service_' in query.data:
            id_ = query.data.replace('payment_by_wallet_upgrade_service_', '')
            package = sqlite_manager.select(table='User', where=f'chat_id = {query.message.chat_id}')
            context.user_data['package'] = package
            context.user_data['purchased_id'] = id_

            price = ranking_manage.discount_calculation(user['id'], package[0][5], package[0][6])

            keyboard = [[InlineKeyboardButton("تایید و پرداخت ✅", callback_data=f"accept_wallet_upgrade_pay_{id_}")]
                        if get_wallet[0][0] >= price else [InlineKeyboardButton("افزایش موجودی ↟", callback_data=f"buy_credit_volume")],
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

                wallet_manage.less_from_wallet(query.from_user['id'], upgrade_serv[1], user_detail=query.from_user)

                keyboard = [[InlineKeyboardButton("برگشت ⤶", callback_data="my_service")]]
                query.edit_message_text(text='سرویس شما با موفقیت ارتقا یافت.✅', reply_markup=InlineKeyboardMarkup(keyboard))

            except Exception as e:
                ready_report_problem_to_admin(context, 'PAY FROM WAWLLET FOR UPGRADE',
                                              query.from_user['id'], e)
                print(e)
                query.answer('مشکلی وجود دارد! گزارش مشکل به ادمین ارسال شد')
        elif 'payment_by_wallet_' in query.data:

            id_ = int(query.data.replace('payment_by_wallet_', ''))

            package = sqlite_manager.select(table='Product', where=f'id = {id_}')
            context.user_data['package'] = package

            price = ranking_manage.discount_calculation(query.from_user['id'], direct_price=package[0][7], more_detail=True)

            keyboard = [[InlineKeyboardButton("تایید و پرداخت ✅", callback_data=f"accept_wallet_pay_{id_}")]
                        if get_wallet[0][0] >= price[0] else [InlineKeyboardButton("افزایش موجودی ↟", callback_data=f"buy_credit_volume")],
                        [InlineKeyboardButton("برگشت ⤶", callback_data="select_server")]]

            available_or_not = "اطلاعات زیر رو بررسی کنید و در صورت تایید پرداخت رو نهایی کنید:" \
                if get_wallet[0][0] >= price[0] else "متاسفانه موجودی کیف پول شما کافی نیست، میتونید با گزینه افزایش موجودی اعتبار خودتون رو افزایش بدید."

            ex = sqlite_manager.select('id', 'Purchased', where=f'active = 0 and chat_id = {user["id"]}', limit=1)

            if not ex:
                ex = sqlite_manager.insert('Purchased', rows=[
                    {'active': 0, 'status': 0, 'name': user["first_name"], 'user_name': user["username"],
                     'chat_id': int(user["id"]), 'product_id': id_, 'notif_day': 0, 'notif_gb': 0}])
            else:
                sqlite_manager.update({'Purchased':
                                           {'active': 0, 'status': 0, 'name': user["first_name"], 'user_name': user["username"],
                                            'chat_id': int(user["id"]), 'product_id': id_, 'notif_day': 0, 'notif_gb': 0}}, where=f'id = {ex[0][0]}')
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

            if check:
                get_db = context.user_data['package'][0][7]

                price = ranking_manage.discount_calculation(query.from_user['id'], direct_price=get_db)

                wallet_manage.less_from_wallet(query.from_user['id'], price, query.from_user)

                keyboard = [[InlineKeyboardButton("برگشت ⤶", callback_data="select_server")]]
                query.edit_message_text(text='پرداخت با موفقیت انجام شد.✅', parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))

            else:
                query.answer('مشکلی وجود داره!')

    except Exception as e:
        print(e)
        query.answer('شکلی وجود داشت، گزارش به ادمین ها ارسال شد.')
        ready_report_problem_to_admin(context, 'PAY FROM WAWLLET', query.from_user['id'], e)
        something_went_wrong(update, context)


def remove_service(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id

    email = query.data.replace('remove_service_', '')
    email = email.replace('accept_rm_ser_', '')
    text = keyboard = None

    get_uuid = sqlite_manager.select(column='client_id,inbound_id,name,id,product_id', table='Purchased', where=f'client_email = "{email}"')

    get_server_domain = sqlite_manager.select(column='server_domain', table='Product',
                                              where=f'id = {get_uuid[0][4]}')

    ret_conf = api_operation.get_client(email, get_server_domain[0][0])

    try:
        if int(ret_conf['obj']['total']):
            upload_gb = int(ret_conf['obj']['up']) / (1024 ** 3)
            download_gb = int(ret_conf['obj']['down']) / (1024 ** 3)
            usage_traffic = round(upload_gb + download_gb, 2)
            total_traffic = int(ret_conf['obj']['total']) / (1024 ** 3)
            left_traffic = total_traffic - usage_traffic

            expiry_timestamp = ret_conf['obj']['expiryTime'] / 1000
            expiry_date = datetime.fromtimestamp(expiry_timestamp)
            days_lefts = (expiry_date - datetime.now()).days
            days_lefts = days_lefts if days_lefts >= 0 else 0
            price = ranking_manage.discount_calculation(chat_id, left_traffic, days_lefts)

        else:
            price = days_lefts = left_traffic = 0


        if 'remove_service_' in query.data :
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
                wallet_manage.add_to_wallet(chat_id, price, query.from_user)

                record_operation_in_file(chat_id=chat_id, price=price,
                                         name_of_operation=f'حذف سرویس و بازپرداخت به کیف پول {get_uuid[0][2]}', operation=1,
                                         status_of_pay=1, context=context)
            report_status_to_admin(context, f'User Deleted Service!\nEmail: {email}\nuser Name:{get_uuid[0][2]}\nuser id: {chat_id}', chat_id)

        query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='markdown')

    except Exception as e:
        print(e)
        ready_report_problem_to_admin(context, 'REMOVE SERVICE',
                                      query.message.from_user['id'], e)
        query.answer('مشکلی وجود دارد!')


def admin_reserve_service(update, context):
    # user_message = 'chat_id,product_id, message'

    user_message = update.message.text.replace('/admin_reserve_service ', '').split(',')
    try:
        user = sqlite_manager.select(column='name,user_name', table='User', where=f'chat_id = {user_message[0]}')

        ex = sqlite_manager.select('id', 'Purchased', where=f'active = 0 and chat_id = {user_message[0]}', limit=1)

        if not ex:
            ex = sqlite_manager.insert('Purchased', rows=[
                {'active': 0, 'status': 0, 'name': user[0][0], 'user_name': user[0][1],
                 'chat_id': user_message[0], 'product_id': user_message[1], 'notif_day': 0, 'notif_gb': 0}])
        else:
            sqlite_manager.update({'Purchased':
                                       {'active': 0, 'status': 0, 'name': user[0][0], 'user_name': user[0][1],
                                        'chat_id': user_message[0], 'product_id': user_message[1], 'notif_day': 0, 'notif_gb': 0}}, where=f'id = {ex[0][0]}')
            ex = ex[0][0]

        send_clean_for_customer(None, context, ex)

        if user_message[2]:
            message_to_user(update, context, user_message[2], user_message[0])
        update.message.reply_text('RESERVE SERVICE OK')
    except Exception as e:
        update.message.reply_text('something went wrong')
        ready_report_problem_to_admin(context, 'ADMIN RESERVE SERIVE', update.message.from_user['id'], e)


def pay_per_use(update, context):
    query = update.callback_query
    text = keyboard = None

    try:
        if 'pay_per_use_' in query.data:

            sqlite_manager.delete({'Product': ['status', 0]})

            get_product_id = int(query.data.replace('pay_per_use_', ''))
            product_db  = sqlite_manager.select(table='Product', where=f'id = {get_product_id}')
            country = product_db[0][4]
            server_domain = product_db[0][11]

            user_credit = wallet_manage.get_wallet_credit(query.message.chat_id)

            chrge_for_next_24_hours = PRICE_PER_DAY

            if chrge_for_next_24_hours > user_credit:
                status_of_user = ("<b>• اعتبار شما کافی نیست، اگر تمایل به فعال کردن این سرویس دارید، لطفا کیف پول خودتون رو شارژ کنید.</b>"
                                  f"\n\nاعتبار مورد نیاز برای فعال کردن سرویس: {chrge_for_next_24_hours:,} تومان ")
                keyboard = [[InlineKeyboardButton("افزایش موجودی ↟", callback_data=f"buy_credit_volume")]]

            else:

                get_infinite_product = sqlite_manager.select('id', 'Product', where=f'name = "pay_per_use_{country}" and country = "{country}"')

                if not get_infinite_product:
                    get_data = {'inbound_id': PAY_PER_USE_INBOUND_ID, 'active': 0,
                                'name': f'pay_per_use_{country}', 'country': country,
                                'period': 0, 'traffic': 0,
                                'price': 0, 'date': datetime.now(pytz.timezone('Asia/Tehran')),
                                'is_personalization': None, 'domain': PAY_PER_USE_DOMAIN,
                                'server_domain': server_domain, 'status': 0}

                    get_infinite_product_id = sqlite_manager.insert('Product', rows=[get_data])

                else:
                    get_infinite_product_id = get_infinite_product[0][0]

                status_of_user = "• با استفاده از گزینه زیر، میتونید سرویس رو فعال کنید"
                keyboard = [[InlineKeyboardButton("فعال سازی سرویس ✓", callback_data=f"active_ppu_{get_infinite_product_id}")]]

            text = ("<b>✬ این سرویس به ازای مصرف شما در هر ساعت، هزینه رو از کیف پول کم میکنه. </b>"
                    "\n\n• در این سرویس محدودیت حجم و زمان وجود نداره، سرویس شما با به پایان رسیدن اعتبار کیف پول غیرفعال میشه."
                    f"\n\n<b>اعتبار کیف پول: {user_credit:,} تومان</b>"
                    f"\n\n{status_of_user}"
                    f"\n\nهزینه روزانه سرویس: {PRICE_PER_DAY:,} تومان"
                    f"\nهزینه هر گیگابایت: {PRICE_PER_GB:,} تومان"
                    )

            keyboard.append([InlineKeyboardButton("برگشت ↰", callback_data=f"{country}")])

        elif 'active_ppu' in query.data:
            get_infinite_product_id = int(query.data.replace('active_ppu_', ''))

            sqlite_manager.update({'Product': {'status': 1}}, where=f'id = {get_infinite_product_id}')

            ex = sqlite_manager.insert('Purchased', rows=[
                {'active': 1, 'status': 1, 'name': query.from_user['name'], 'user_name': query.from_user['username'],
                 'chat_id': query.message.chat_id, 'product_id': get_infinite_product_id, 'notif_day': 0, 'notif_gb': 0}])

            send_clean_for_customer(query, context, ex)
            keyboard = [[InlineKeyboardButton("برگشت ↰", callback_data=f"main_menu")]]

            sqlite_manager.insert(table='Hourly_service', rows=[{'purchased_id': ex, 'chat_id': query.message.chat_id, 'last_traffic_usage': 0}])

            text = "سرویس با موفقیت برای شما فعال شد ✅"

        query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')

    except Exception as e:
        query.answer('مشکلی وجود داشت! گزارش به ادمین ها ارسال شد')
        ready_report_problem_to_admin(context, 'GET PAY PER USE SERVICE', query.message.from_user['id'], e)


def pay_per_use_calculator(context):
    get_all = api_operation.get_all_inbounds()

    get_from_db = sqlite_manager.select(column='id', table='Product', where=f'name LIKE "pay_per_use_%"')
    pay_per_use_products = [id_[0] for id_ in get_from_db]

    get_from_db = sqlite_manager.select(column='id,chat_id,client_email,status,date,notif_day,notif_gb,inbound_id,client_id',
                                        table='Purchased', where=f"product_id IN {tuple(pay_per_use_products)}")


    get_user_wallet = sqlite_manager.select(column='chat_id,wallet,name,notification_wallet,notif_wallet,notif_low_wallet', table='User')

    get_last_traffic_uasge = sqlite_manager.select(column='chat_id,purchased_id,last_traffic_usage', table='Hourly_service')
    try:
        for server in get_all:
            for config in server['obj']:
                for client in config['clientStats']:
                    for user in get_from_db:
                        if user[2] == client['email']:
                            user_wallet = [wallet for wallet in get_user_wallet if wallet[0] == user[1]]
                            last_traffic_usage = [last_traffic_use for last_traffic_use in get_last_traffic_uasge if last_traffic_use[1] == user[0]]
                            print(last_traffic_usage, user)
                            if client['enable']:

                                upload_gb = client['up'] / (1024 ** 3)
                                download_gb = client['down'] / (1024 ** 3)
                                usage_traffic = upload_gb + download_gb

                                time_price = PRICE_PER_DAY / 24
                                traffic_use =  (usage_traffic - last_traffic_usage[0][2]) * PRICE_PER_GB
                                cost = int(time_price + traffic_use)
                                cost = ranking_manage.discount_calculation(user[1], direct_price=cost)

                                wallet_manage.less_from_wallet_with_condition_to_make_history(user[1], cost, user_detail={'name': user_wallet[0][2], 'username': user_wallet[0][2]}, con=100)

                                sqlite_manager.update(table={'Hourly_service': {'last_traffic_usage': usage_traffic}}, where=f'purchased_id = {user[0]}')

                                credit_now = user_wallet[0][1] - cost

                            else:
                                credit_now = user_wallet[0][1]

                            if credit_now <= user_wallet[0][3] and not user_wallet[0][4]:
                                text = ("🔵 اطلاع رسانی باقی مانده اعتبار کیف پول"
                                        f"\nدرود {user_wallet[0][2]} عزیز، از اعتبار کیف پول شما {user_wallet[0][1]:,} تومان باقی مانده، "
                                        f"در صورتی که تمایل دارید نسبت به افزایش اعتبار کیف پول اقدام کنید.")

                                keyboard = [[InlineKeyboardButton("افزایش موجودی ↟", callback_data=f"buy_credit_volume")]]

                                context.bot.send_message(user[1], text=text, reply_markup=InlineKeyboardMarkup(keyboard))
                                sqlite_manager.update({'User': {'notif_wallet': 1}}, where=f'chat_id = "{user[1]}"')

                            elif credit_now <= LOW_WALLET_CREDIT and not user_wallet[0][5]:
                                text = ("🔵 اعتبار کیف پول شما رو به اتمام است"
                                        f"\nدرود {user_wallet[0][2]} عزیز، از اعتبار کیف پول شما {credit_now:,} تومان باقی مانده، "
                                        f"در صورتی که تمایل دارید نسبت به افزایش اعتبار کیف پول اقدام کنید.")

                                keyboard = [[InlineKeyboardButton("افزایش موجودی ↟", callback_data=f"buy_credit_volume")]]

                                context.bot.send_message(user[1], text=text, reply_markup=InlineKeyboardMarkup(keyboard))
                                sqlite_manager.update({'User': {'notif_low_wallet': 1}}, where=f'chat_id = "{user[1]}"')

                            if client['enable'] and user[3] and (credit_now <= 0):
                                text = ("🔴 اطلاع رسانی غیرفعال شدن سرویس ساعتی"
                                        f"\nدرود {user_wallet[0][2]} عزیز، سرویس ساعتی شما با نام {user[2]} به دلیل اتمام اعتبار کیف پول، غیرفعال شد!"
                                        f"\nدر صورتی که تمایل دارید نسبت به شارژ کردن کیف پول و فعال کردن سرویس اقدام کنید.")

                                keyboard = [
                                    [InlineKeyboardButton("افزایش موجودی ↟", callback_data=f"buy_credit_volume"),
                                     InlineKeyboardButton("مشاهده جزئیات سرویس", callback_data=f"view_service_{user[2]}")]
                                ]

                                data = {
                                    "id": int(user[7]),
                                    "settings": "{{\"clients\":[{{\"id\":\"{0}\",\"alterId\":0,"
                                                "\"email\":\"{1}\",\"limitIp\":0,\"totalGB\":0,\"expiryTime\":{2},"
                                                "\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}}]}}".format(user[8], user[2],
                                                                                                           second_to_ms(datetime.now()))}

                                get_server_domain = sqlite_manager.select(column='server_domain', table='Product',
                                                                          where=f'id = {user[7]}')

                                print(api_operation.update_client(user[8], data, get_server_domain[0][0]))

                                sqlite_manager.update({'Purchased': {'status': 0}}, where=f'id = {user[0]}')
                                context.bot.send_message(ADMIN_CHAT_ID,
                                                         text=f'Service OF {user_wallet[0][2]} Named {user[2]} Has Be Ended')

                                context.bot.send_message(user[1], text=text, reply_markup=InlineKeyboardMarkup(keyboard))

    except Exception as e:
        ready_report_problem_to_admin(context, 'PAY PER USE CALCULATOR', '', e)


def report_problem_by_user(update, context):
    query = update.callback_query
    text = keyboard = None

    if query.data == 'report_problem_by_user':
        text = '• لطفا مشکلی که باهاش مواجه هستید رو انتخاب کنید:'

        keyboard = [[InlineKeyboardButton("سرویس دچار قطعی و وصلی میشود", callback_data=f"say_to_admin_Intermittent_connection_problem")],
                    [InlineKeyboardButton("سرویس وصل نمیشود و یا کار نمیکند", callback_data=f"say_to_admin_service_dont_connected_or_dont_work")],
                    [InlineKeyboardButton("سرعت سرویس پایین است و اختلال دارد", callback_data=f"say_to_admin_server_speed_is_low")],
                    [InlineKeyboardButton("در برخی اپلیکیشن ها با مشکل مواجه هستم", callback_data=f"say_to_admin_problem_in_some_apllication")],
                    [InlineKeyboardButton("مشکلی غیر از موارد بالا دارم", callback_data=f"say_to_admin_somthingElse")],
                    [InlineKeyboardButton("برگشت", callback_data=f"guidance")]
                    ]

    elif 'say_to_admin_' in query.data:
        text = '• از اینکه مشکل رو گزارش کردید متشکریم.\n تمایل دارید مشکل رو دقیق تر توضیح بدید؟'

        problem = query.data.replace('say_to_admin_', '')

        keyboard = [[InlineKeyboardButton("بله", callback_data=f"ticket_send_{problem}")],
                    [InlineKeyboardButton("برگشت", callback_data=f"report_problem_by_user")]]

        report_problem_by_user_utilitis(context, problem.replace('_', ' '), query.from_user)

    query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


def say_to_user_send_ticket(update, context):
    query = update.callback_query
    query.answer('پیام خودتون رو بفرستید')
    problem = query.data.replace('ticket_send_', '')
    try:
        context.user_data['problem'] = problem
        text = 'پیام خودتو رو بفرستید:\nاگر مایل به فرستادن عکس هستید، توضیحات رو در کپشن ذکر کنید.'
        context.bot.send_message(chat_id=query.message.chat_id, text=text, parse_mode='markdown')
        return GET_TICKET
    except Exception as e:
        print(e)
        ready_report_problem_to_admin(context, text='say_to_user_send_ticket', chat_id=query.message.chat_id, error=e)
        something_went_wrong(update, context)
        return ConversationHandler.END


def send_ticket_to_admin(update, context):
    user = update.message.from_user
    try:
        problem = context.user_data['problem']

        text = (f"- New Ticket [{problem.replace('_', ' ')}]:\nName: {user['name']}\nUserName: {user['username']}"
                f"\nUserID: {user['id']}")

        keyboard = [[InlineKeyboardButton("صفحه اصلی", callback_data="main_menu_in_new_message")]]

        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            text += f"caption: {update.message.caption}" or 'Witout caption!'
            context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=file_id, caption=text)
            update.message.reply_text(f'پیام شما ثبت شد. متشکریم!', reply_markup=InlineKeyboardMarkup(keyboard))
        elif update.message.text:
            text += f"Text: {update.message.text}"
            context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)
            update.message.reply_text(f'پیام شما ثبت شد. متشکریم!', reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            update.message.reply_text('مشکلی وجود داشت!', reply_markup=InlineKeyboardMarkup(keyboard))

        context.user_data.clear()
        return ConversationHandler.END
    except Exception as e:
        ready_report_problem_to_admin(context, 'SEND EVIDENCE TO ADMIN', user['id'], e)
        text = ("مشکلی وجود داشت!"
                "گزارش به ادمین ها ارسال شد، نتیجه به زودی بهتون اعلام میشه")
        keyboard = [[InlineKeyboardButton("برگشت ↰", callback_data="main_menu")]]
        update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END


tickect_by_user = ConversationHandler(
    entry_points=[CallbackQueryHandler(say_to_user_send_ticket, pattern='ticket_send_')],
    states={
        GET_TICKET: [MessageHandler(Filters.all, send_ticket_to_admin)]
    },
    fallbacks=[],
    conversation_timeout=1000,
    per_chat=True,
    allow_reentry=True
)


def rank_page(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    try:
        rank = sqlite_manager.select(table='Rank', where=f'chat_id = {chat_id}')
        keyboard = [
            [InlineKeyboardButton("زیرمجموعه گیری", callback_data=f'subcategory')],
            [InlineKeyboardButton("برگشت ↰", callback_data="main_menu")]
        ]

        next_rank = find_next_rank(rank[0][5], rank[0][4])
        all_access = '\n- '.join(ranking_manage.get_all_access_fa(rank[0][5]))

        text = (f"<b>• با افزایش رتبه، به ویژگی های بیشتری از ربات و همچنین تخفیف بالاتری دسترسی پیدا میکنید!</b>"
                f"\n\n<b>❋ رتبه شما: {get_rank_and_emoji(rank[0][5])}</b>"
                f"\n❋ امتیاز: {rank[0][4]:,}"
                f"<b>\n\n• دسترسی های رتبه شما:</b>\n\n"
                f"- {all_access}"
                f"\n\n• <b>رتبه بعدی: {next_rank[0]}</b>"
                f"\n<b>• امتیاز مورد نیاز: {next_rank[1]:,}</b>")

        query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))

    except IndexError as i:
        if 'list index out of range' in str(i):
            sqlite_manager.insert('Rank', [{'name': query.from_user['name'],'user_name': query.from_user['username'],
                                            'chat_id': query.from_user['id'], 'level': 0, 'rank_name': next(iter(ranking.rank_access))}])
            query.answer('دوباره کلیک کنید')

    except Exception as e:
        print(e)
        ready_report_problem_to_admin(context, text='RANKING PAGE', chat_id=chat_id, error=e)
        something_went_wrong(update, context)


def subcategory(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    user_id = sqlite_manager.select(table='User', column='id', where=f'chat_id = {query.message.chat_id}')
    try:
        uuid_ = str(uuid.uuid5(uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8'), query.from_user['name']))[:5]
        link = f'https://t.me/Fensor_bot/?start={uuid_}_{user_id[0][0]}'
        text = f'{link}\n+50 رتبه هدیه برای اولین بار استفاده کردن از این ربات!'
        keyboard = [
            [InlineKeyboardButton("ارسال برای دوستان", url=f'https://t.me/share/url?text={text}')],
            [InlineKeyboardButton("برگشت ↰", callback_data="rank_page")]
        ]

        text = ("<b>• دوستانتون رو به ربات دعوت کنید تا با هر خریدشون، 10 درصد مبلغ به کیف‌پول شما اضافه بشه"
                f"\n\n• همچنین +50 رتبه برای شما و کسی که با لینک شما وارد ربات بشه."
                f"\n\n• لینک دعوت شما: \n{link}</b>")
        query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard), disable_web_page_preview=True)

    except Exception as e:
        print(e)
        ready_report_problem_to_admin(context, text='subcategory', chat_id=chat_id, error=e)
        something_went_wrong(update, context)


def service_advanced_option(update, context):
    query = update.callback_query
    email = query.data.replace('advanced_option_', '')
    try:

        status_1 = change_shematic = change_server_notif = ''
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
                                                                                       ret_conf['obj']['total'], ret_conf['obj']['expiryTime'])}

            api_operation.update_client(get_service_uuid, data, get_domain)
            get_address = get_data[0][8].replace(str(get_service_uuid), str(generate_key))
            sqlite_manager.update({'Purchased': {'details': get_address, 'client_id': generate_key}}, where=f'client_email = "{email}"')
            change_shematic = '\n\n↲ پیکربندی تغییر یافت، سرویس را کپی جایگزین قبلی کنید.'
            query.answer('پیکربندی سرویس تغییر یافت ✅')

            report_status_to_admin(context, f'User changed Config Shematic\nConfig Email: {email}', chat_id=query.message.chat_id)

        elif 'active_tls_encoding_' in query.data:
            data = query.data.replace('active_tls_encoding_', '').split('__')
            print(data)
            email = data[0]
            convert_to = data[1]

            active_tls = utilities.convert_service_to_tls(update, email, convert_to)

            change_shematic = '\n\n↲ پیکربندی تغییر یافت، سرویس را کپی جایگزین قبلی کنید.'
            status_1 = '\n\nبا فعال بودن رمزنگاری، اطلاعات شما به صورت رمزنگاری شده رد و بدل میشود و امنیت بالاتر میرود'
            query.answer('پیکربندی سرویس تغییر یافت ✅')

            report_status_to_admin(context, f'User Converted Service TLS [{convert_to}]\nConfig Email: {email}',
                                   chat_id=query.message.chat_id)


        elif 'change_server_' in query.data:
            email = query.data.replace('change_server_', '')

            get_data = sqlite_manager.select(table='Purchased', where=f'client_email = "{email}"')
            get_server_country = sqlite_manager.select(column='name,server_domain', table='Product',
                                                       where=f'id = {get_data[0][6]}')

            plans = sqlite_manager.select(table='Product', where='active = 1')
            unic_plans = {name[3]: name[4] for name in plans}

            print(get_server_country[0][0].replace('pay_per_use_', ''))

            keyboard_main = [[InlineKeyboardButton(f"{key} {'✅' if get_server_country[0][0] == key or get_server_country[0][0].replace('pay_per_use_', '') == value else ''}",
                                                   callback_data='alredy_have_show' if get_server_country[0][0] == key or get_server_country[0][0].replace('pay_per_use_', '') == value else f'changed_server_to_{email}__{value}')] for key, value in unic_plans.items()]

            keyboard_main.append([InlineKeyboardButton("برگشت ↰", callback_data=f"advanced_option_{email}")])

            change_server_notif = '\n\n• سروری که میخواهید را انتخاب کنید'

        elif 'changed_server_to_' in query.data:
            get_data = query.data.replace('changed_server_to_', '').split('__')
            email = get_data[0]
            country = get_data[1]

            get_new_inbound = change_service_server(context, update, email, country)

            plans = sqlite_manager.select(table='Product', where='active = 1')
            unic_plans = {name[3]: name[4] for name in plans}

            keyboard_main = [[InlineKeyboardButton(f"{key} {'✅' if get_new_inbound[0][2] == key else ''}",
                                                   callback_data='alredy_have_show' if get_new_inbound[0][2] == key else f'changed_server_to_{email}__{value}')] for key, value in unic_plans.items()]

            keyboard_main.append([InlineKeyboardButton("برگشت ↰", callback_data=f"advanced_option_{email}")])

            change_shematic = '\n\n↲ پیکربندی تغییر یافت، سرویس را کپی و جایگزین قبلی کنید.'
            query.answer('عملیات با موفقیت انجام شد ✅')

            report_status_to_admin(context, f'User changed Config Server\nConfig Email: {email}\nNew Server: {country}',
                                   chat_id=query.message.chat_id)


        get_data = sqlite_manager.select(table='Purchased', where=f'client_email = "{email}"')
        get_server_country = sqlite_manager.select(column='name,server_domain', table='Product',
                                                   where=f'id = {get_data[0][6]}')

        get_server_country = get_server_country[0][0].replace('سرور ', '').replace('pay_per_use_', '')
        auto_renewal, auto_renewal_button, chenge_to = ('فعال ✓', 'غیرفعال کردن تمدید خودکار ✗', False) if get_data[0][15] \
            else ('غیرفعال ✗', 'فعال کردن تمدید خودکار ✓', True)

        tls_encodeing, tls_status, change_to_ = ('✓', 'فعال ✓', False) if get_data[0][7] == TLS_INBOUND else ('✗', 'غیرفعال ✗', True)

        text_ = (
            "<b>🟡 با تغییر گزینه‌ها، تنظیمات سرویس تغییر می‌کند و اگر به این سرویس متصل هستید،"
            " ارتباط قطع خواهد شد. لطفاً اطمینان حاصل کنید که قادر به جایگزینی آدرس جدید هستید.</b>"
            f"\n\n🔷 نام سرویس: {email}"
            f"\n🗺 موقعیت سرور: {get_server_country}"
            f"\n🔗 تمدید خودکار: {auto_renewal}"
            f"\n🛡️ رمزگذاری اطلاعات: {tls_status}"
            f"{status_1}"
            f"\n\n🌐 آدرس سرویس:\n <code>{get_data[0][8]}</code>"
            f"{change_shematic}"
            f"{change_server_notif}"
        )

        keyboard = [[InlineKeyboardButton(f"{auto_renewal_button}", callback_data=f"change_auto_renewal_status_{email}__{chenge_to}")],
                    [InlineKeyboardButton(f" تعویض کانفیگ ⤰", callback_data=f"change_config_shematic_{email}"),
                     InlineKeyboardButton(f"تغییر لوکیشن ⇈", callback_data=f"change_server_{email}")],
                    [InlineKeyboardButton(f"رمزگذاری TLS {tls_encodeing}", callback_data=f"active_tls_encoding_{email}__{change_to_}"),
                     InlineKeyboardButton("• انتقال مالکیت", callback_data=f"change_service_ownership_{email}")],
                    [InlineKeyboardButton("برگشت ↰", callback_data=f"view_service_{email}")]]

        query.edit_message_text(text_, reply_markup=InlineKeyboardMarkup(keyboard if not keyboard_main else keyboard_main), parse_mode='html')


    except EOFError as eof:
        if 'service_is_depleted' in str(eof):
            query.answer('این ویژگی فقط برای سرویس های فعال است')
        else:
            query.answer('مشکلی وجود داشت!')

    except Exception as e:
        ready_report_problem_to_admin(context, text='service_advanced_option', chat_id=query.message.chat_id, error=e)
        something_went_wrong(update, context)


def change_service_ownership(update, context):
    query = update.callback_query
    email = query.data.replace('change_service_ownership_', '')
    try:

        context.user_data['service_email'] = email
        text = ('<b>بسیار خب، آیدی عددی کاربر مورد نظر را ارسال کنید.'
                '\n\nآیدی عددی را میتوان در صفحه اصلی راهنما ربات پیدا کرد.</b>')
        keyboard = [[InlineKeyboardButton("منصرف شدم ⤹", callback_data=f"csos_cancel")],
                    [InlineKeyboardButton("صفحه اصلی ↰", callback_data=f"main_menu")]]
        query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))
        return GET_CONVER
    except Exception as e:
        print(e)
        ready_report_problem_to_admin(context, text='change_service_ownership', chat_id=query.message.chat_id, error=e)
        something_went_wrong(update, context)
        return ConversationHandler.END


def change_service_ownership_func(update, context):
    user = update.message.from_user
    try:
        email = context.user_data['service_email']

        keyboard = [[InlineKeyboardButton("صفحه اصلی", callback_data="main_menu_in_new_message")]]

        if update.message.text:
            new_owner_chat_id = int(update.message.text)

            new_user_detail = sqlite_manager.select(table='User', where=f'chat_id = {new_owner_chat_id}')

            sqlite_manager.update({'Purchased': {'name': new_user_detail[0][1],'user_name': new_user_detail[0][2],
                                                 'chat_id': new_owner_chat_id}}, where=f'chat_id = {user["id"]} and client_email = "{email}"')

            report_status_to_admin(context, f'Change Service [{email}] OwnerShip to {new_owner_chat_id}', chat_id=user['id'])
            update.message.reply_text(f'<b>انتقال سرویس با موفقیت انجام شد ✅</b>', reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')

            message_to_user(update, context, message=f'<b>کاربر {user["first_name"]} یک سرویس برای شما فرستاد!\nنام سرویس: {email}</b>', chat_id=new_owner_chat_id)

        else:
            update.message.reply_text('مشکلی وجود داشت. فقط آیدی عددی با فرمت مناسب قابل قبول است!', reply_markup=InlineKeyboardMarkup(keyboard))

        context.user_data.clear()
        return ConversationHandler.END

    except Exception as e:
        ready_report_problem_to_admin(context, 'change_service_ownership_func', user['id'], e)
        text = ("مشکلی وجود داشت!"
                "گزارش به ادمین ها ارسال شد، نتیجه به زودی بهتون اعلام میشه")
        keyboard = [[InlineKeyboardButton("برگشت ↰", callback_data="main_menu")]]
        update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
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


