import random
from datetime import datetime, timedelta
import telegram.error
import private
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from admin_task import add_client_bot, api_operation, second_to_ms, message_to_user, wallet_manage, sqlite_manager
import qrcode
from io import BytesIO
import pytz
from utilities import (human_readable,something_went_wrong,
                       ready_report_problem_to_admin,format_traffic,record_operation_in_file,
                       send_service_to_customer_report)
import re
from private import ADMIN_CHAT_ID

GET_EVIDENCE = 0
GET_EVIDENCE_PER = 0
GET_EVIDENCE_CREDIT = 0


def buy_service(update, context):
    query = update.callback_query
    try:
        plans = sqlite_manager.select(table='Product', where='active = 1')
        unic_plans = {name[3]: name[4] for name in plans}

        keyboard = [[InlineKeyboardButton(key, callback_data=value)] for key, value in unic_plans.items()]
        keyboard.append([InlineKeyboardButton("برگشت ↰", callback_data="main_menu")])

        query.edit_message_text(
            text="<b>سرور مورد نظر خودتون رو انتخاب کنید:</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='html'
        )
    except Exception as e:
        ready_report_problem_to_admin(context, 'SELECT SERVICE', query.message.chat_id, e)
        something_went_wrong(update, context)


def all_query_handler(update, context):
    query = update.callback_query
    try:
        text = "<b>سرویس مناسب خودتون رو انتخاب کنید:\n\n✪ با انتخاب گزینه 'دلخواه' میتونید یک سرویس شخصی سازی شده بسازید!</b>"
        plans = sqlite_manager.select(table='Product', where=f'active = 1 and country = "{query.data}"')
        country_unic = {name[4] for name in plans}
        for country in country_unic:
            if query.data == country:
                service_list = [service for service in plans if service[4] == country]
                keyboard = [[InlineKeyboardButton(f"سرویس {pattern[5]} روزه - {pattern[6]} گیگابایت - {pattern[7]:,} تومان",
                                                  callback_data=f"service_{pattern[0]}")] for pattern in service_list]

                keyboard.append([InlineKeyboardButton("✪ سرویس دلخواه", callback_data=f"personalization_service_{plans[0][0]}")])
                keyboard.append([InlineKeyboardButton("برگشت ↰", callback_data="select_server")])
                query.edit_message_text(text= text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
    except Exception as e:
        ready_report_problem_to_admin(context, 'FIND PLANE', query.message.chat_id, e)
        something_went_wrong(update, context)


def payment_page(update, context):
    query = update.callback_query
    id_ = int(query.data.replace('service_', ''))
    try:
        package = sqlite_manager.select(table='Product', where=f'id = {id_}')
        if package[0][7]:
            keyboard = [
                [InlineKeyboardButton("پرداخت از کیف پول", callback_data=f'payment_by_wallet_{id_}'),
                 InlineKeyboardButton("کارت به کارت", callback_data=f'payment_by_card_{id_}')],
                [InlineKeyboardButton("برگشت ↰", callback_data=f"{package[0][4]}")]
            ]
        else:
            free_service_is_taken = sqlite_manager.select(column='free_service', table='User', where=f'chat_id = {query.message.chat_id}')[0][0]
            if free_service_is_taken:
                query.answer('ببخشید، شما یک بار این بسته رو دریافت کردید!')
                return
            else:
                keyboard = [
                    [InlineKeyboardButton("دریافت ⤓", callback_data=f'get_free_service')],
                    [InlineKeyboardButton("برگشت ↰", callback_data="select_server")]
                ]

        text = (f"<b>❋ بسته انتخابی شامل مشخصات زیر میباشد:</b>\n"
                f"\nسرور: {package[0][3]}"
                f"\nدوره زمانی: {package[0][5]} روز"
                f"\nترافیک (حجم): {package[0][6]} گیگابایت"
                f"\nحداکثر کاربر مجاز: ∞"
                f"\n<b>قیمت: {package[0][7]:,} تومان</b>"
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
        context.user_data['package'] = package
        keyboard = [[InlineKeyboardButton("صفحه اصلی ⤶", callback_data="send_main_message")]]
        ex = sqlite_manager.insert('Purchased',rows= [{'active': 0,'status': 0, 'name': user["first_name"],'user_name': user["username"],
                                                       'chat_id': int(user["id"]), 'product_id': id_, 'notif_day': 0, 'notif_gb': 0}])
        context.user_data['purchased_id'] = ex
        text = (f"*اطلاعات زیر رو بررسی کنید و در صورت تایید پرداخت رو نهایی کنید:*"
                f"\n\nمدت اعتبار فاکتور: 10 دقیقه"
                f"\nسرویس: {package[0][5]} روز - {package[0][6]} گیگابایت"
                f"\n*قیمت*: `{package[0][7]:,}`* تومان *"
                f"\n\n*• لطفا مبلغ رو به شماره‌حساب زیر واریز کنید و اسکرین‌شات یا شماره‌پیگیری رو بعد از همین پیام ارسال کنید.*"
                f"\n\n`6219861938619417` - امیرحسین نجفی"
                f"\n\n*• بعد از تایید شدن پرداخت، سرویس برای شما ارسال میشه، زمان تقریبی 5 دقیقه الی 3 ساعت.*")
        query.edit_message_text(text=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return GET_EVIDENCE
    except Exception as e:
        ready_report_problem_to_admin(context, 'GET CARD PAY EVIDENCE', query.message.chat_id, e)
        something_went_wrong(update, context)


def send_evidence_to_admin(update, context):
    user = update.message.from_user
    try:
        package = context.user_data['package']
        purchased_id = context.user_data['purchased_id']
        text = "- Check the new payment to the card:\n\n"
        text += f"Name: {user['first_name']}\nUserName: @{user['username']}\nID: {user['id']}\n\n"
        keyboard = [[InlineKeyboardButton("Accept ✅", callback_data=f"accept_card_pay_{purchased_id}")]
            , [InlineKeyboardButton("Refuse ❌", callback_data=f"refuse_card_pay_{purchased_id}")]]
        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            text += f"caption: {update.message.caption}" or 'Witout caption!'
            text += f"\n\nServer: {package[0][4]}\nInbound id: {package[0][1]}\nPeriod: {package[0][5]} Day\n Traffic: {package[0][6]}GB\nPrice: {package[0][7]:,} T"
            context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=file_id, caption=text , reply_markup=InlineKeyboardMarkup(keyboard))
            update.message.reply_text(f'سفارش شما با موفقیت ثبت شد✅\nنتیجه از طریق همین ربات بهتون اعلام میشه')
        elif update.message.text:
            text += f"Text: {update.message.text}"
            text += f"\n\nServer: {package[0][4]}\nInbound id: {package[0][1]}\nPeriod: {package[0][5]} Day\n Traffic: {package[0][6]}GB\nPrice: {package[0][7]:,} T"
            context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, reply_markup=InlineKeyboardMarkup(keyboard))
            update.message.reply_text(f'درخواست شما با موفقیت ثبت شد✅\nنتیجه از طریق همین ربات بهتون اعلام میشه')
        else:
            update.message.reply_text('مشکلی وجود داره! فقط متن یا عکس قابل قبوله.')

        context.user_data.clear()
        return ConversationHandler.END
    except Exception as e:
        ready_report_problem_to_admin(context,'SEND EVIDENCE TO ADMIN', user['id'], e)
        text = ("مشکلی وجود داشت!"
                "گزارش به ادمین ها ارسال شد، نتیجه به زودی بهتون اعلام میشه")
        keyboard = [[InlineKeyboardButton("برگشت ↰", callback_data="main_menu")]]
        update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END

def cancel(update, context):
    query = update.callback_query
    query.answer(text="با موفقیت کنسل شد!", show_alert=False)
    return ConversationHandler.END


get_service_con = ConversationHandler(
    entry_points=[CallbackQueryHandler(get_card_pay_evidence, pattern=r'payment_by_card_\d+')],
    states={
        GET_EVIDENCE: [MessageHandler(Filters.all, send_evidence_to_admin)]
    },
    fallbacks=[CallbackQueryHandler(cancel, pattern='cancel')],
    conversation_timeout=600,
    per_chat=True,
    allow_reentry=True,
)


def send_clean_for_customer(query, context, id_):
    create = add_client_bot(id_)
    if create[0]:
        get_client = sqlite_manager.select(table='Purchased', where=f'id = {id_}')
        try:
            get_product = sqlite_manager.select(table='Product', where=f'id = {get_client[0][6]}')
            get_domain = get_product[0][10]
            returned = api_operation.get_client_url(client_email=get_client[0][9], inbound_id=get_client[0][7], domain=get_domain)
            if returned:
                returned_copy = f'`{returned}`'
                qr_code = qrcode.make(returned)
                qr_image = qr_code.get_image()
                buffer = BytesIO()
                qr_image.save(buffer, format='PNG')
                binary_data = buffer.getvalue()
                keyboard = [[InlineKeyboardButton("صفحه اصلی ربات", callback_data=f"main_menu_in_new_message"),
                             InlineKeyboardButton("🎛 سرویس های من", callback_data=f"my_service")],
                            [InlineKeyboardButton("دریافت به صورت فایل", callback_data=f"create_txt_file")]]
                context.user_data['v2ray_client'] = returned

                context.bot.send_photo(photo=binary_data,
                                       caption=f' سرویس شما با موفقیت فعال شد✅\n\n*• میتونید جزئیات سرویس رو از بخش "سرویس های من" مشاهده کنید.\n\n✪ لطفا سرویس رو به صورت مستقیم از طریق پیام رسان های ایرانی یا پیامک ارسال نکنید، با کلیک روی گزینه "دانلود به صورت فایل" سرویس رو به صورت فایل ارسال کنید.* \n\n\nلینک:\n{returned_copy}',
                                       chat_id=get_client[0][4], reply_markup=InlineKeyboardMarkup(keyboard),
                                       parse_mode='markdown')

                record_operation_in_file(chat_id=get_client[0][4], price=get_product[0][7],
                                         name_of_operation=f'خرید سرویس {get_client[0][2]}', operation=0,
                                         status_of_pay=1, context=context)


                send_service_to_customer_report(context, status=1, chat_id=get_client[0][4], service_name=get_client[0][2])
                return True
            else:
                send_service_to_customer_report(context, status=0, chat_id=get_client[0][4], service_name=get_client[0][2],
                                                more_detail=create)
                print('wrong: ', returned)
                return False
        except Exception as e:
            print(e)
            send_service_to_customer_report(context, status=0, chat_id=get_client[0][4], service_name=get_client[0][2],
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

        elif 'ok_card_pay_refuse_' in query.data:
            id_ = int(query.data.replace('ok_card_pay_refuse_', ''))
            get_client = sqlite_manager.select(table='Purchased', where=f'id = {id_}')
            context.bot.send_message(text=f'متاسفانه درخواست شما برای ثبت سرویس پذیرفته نشد❌\n ارتباط با پشتیبانی: \n @Fupport ', chat_id=get_client[0][4])
            query.answer('Done ✅')
            query.delete_message()
            record_operation_in_file(chat_id=get_client[0][4], price=0,
                                     name_of_operation=f'خرید سرویس {get_client[0][2]}', operation=0,
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
    get_purchased = sqlite_manager.select(table='Purchased', where=f'chat_id = {chat_id} and active = 1')
    if get_purchased:
        keyboard = [[InlineKeyboardButton(f"{'✅' if ser[11] == 1 else '❌'} {ser[9]}", callback_data=f"view_service_{ser[9]}")] for ser in get_purchased]
        keyboard.append([InlineKeyboardButton("برگشت ↰", callback_data="main_menu")])
        try:
            query.edit_message_text('<b>برای مشاهده جزئیات، سرویس مورد نظر خودتان را انتخاب کنید:</b>', reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
        except telegram.error.BadRequest:
            query.answer('در یک پیام جدید فرستادم!')
            context.bot.send_message(chat_id=chat_id, text='<b>برای مشاهده جزئیات، سرویس مورد نظر خودتان را انتخاب کنید:</b>',
                                     reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
    else:
        query.answer('سرویسی برای شما یافت نشد!')


def server_detail_customer(update, context):
    query = update.callback_query
    email = update.callback_query.data.replace('view_service_', '')
    try:
        get_data = sqlite_manager.select(table='Purchased', where=f'client_email = "{email}"')
        get_server_country = sqlite_manager.select(column='name', table='Product', where=f'id = {get_data[0][6]}')[0][0].replace('سرور ','')

        ret_conf = api_operation.get_client(email)
        keyboard = [[InlineKeyboardButton("تمدید و ارتقا ↟", callback_data=f"personalization_service_lu_{get_data[0][0]}")],
                    [InlineKeyboardButton("حذف سرویس ⇣",callback_data=f"remove_service_{email}"),
                     InlineKeyboardButton("تازه سازی ⟳",callback_data=f"view_service_{email}")],
                    [InlineKeyboardButton("برگشت ↰", callback_data="my_service")]]

        upload_gb = round(int(ret_conf['obj']['up']) / (1024 ** 3), 2)
        download_gb = round(int(ret_conf['obj']['down']) / (1024 ** 3), 2)
        usage_traffic = round(upload_gb + download_gb, 2)
        if int(ret_conf['obj']['total']) != 0:
            total_traffic = round(int(ret_conf['obj']['total']) / (1024 ** 3), 2)
        else:
            total_traffic = '∞'


        expiry_timestamp = ret_conf['obj']['expiryTime'] / 1000
        expiry_date = datetime.fromtimestamp(expiry_timestamp)
        expiry_month = expiry_date.strftime("%Y/%m/%d")
        days_lefts = (expiry_date - datetime.now())
        days_lefts_days = days_lefts.days

        change_active = 'فعال ✅' if ret_conf['obj']['enable'] else 'غیرفعال ❌'
        purchase_date = datetime.strptime(get_data[0][12], "%Y-%m-%d %H:%M:%S.%f%z").replace(tzinfo=None)
        days_left_2 = abs(days_lefts_days)
        if days_left_2 >= 1:
            exist_day = f"({days_left_2} روز {'مانده' if days_lefts_days >= 0 else 'گذشته'})"
        else:
            days_left_2 = abs(int(days_lefts.seconds / 3600))
            exist_day = f"({days_left_2} ساعت {'مانده' if days_left_2 >= 1 else 'گذشته'})"

        context.user_data['period_for_upgrade'] = (expiry_date - purchase_date).days
        context.user_data['traffic_for_upgrade'] = total_traffic

        text_ = (
            f"<b>اطلاعات سرویس انتخاب شده:</b>"
            f"\n\n🔷 نام سرویس: {email}"
            f"\n💡 وضعیت: {change_active}"
            f"\n🌎 موقعیت سرور: {get_server_country}"
            f"\n📅 تاریخ انقضا: {expiry_month} {exist_day}"
            f"\n🔼 آپلود↑: {format_traffic(upload_gb)}"
            f"\n🔽 دانلود↓: {format_traffic(download_gb)}"
            f"\n📊 مصرف کل: {usage_traffic}/{total_traffic}GB"
            f"\n\n⏰ تاریخ خرید/تمدید: {purchase_date.strftime('%H:%M:%S | %Y/%m/%d')}"
            f"\n\n🌐 آدرس سرویس:\n <code>{get_data[0][8]}</code>"
        )
        query.edit_message_text(text=text_, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
        sqlite_manager.update({'Purchased': {'status': 1 if ret_conf['obj']['enable'] else 0}}, where=f'client_email = "{email}"')
    except TypeError as e:
        keyboard = [
            [InlineKeyboardButton("پشتیبانی", callback_data="support")],
            [InlineKeyboardButton("حذف سرویس ⇣", callback_data=f"remove_service_from_db_{email}"),
             InlineKeyboardButton("تازه سازی ⟳", callback_data=f"view_service_{email}")],
            [InlineKeyboardButton("برگشت ↰", callback_data="my_service")]]
        text = ('*متاسفانه مشکلی در دریافت اطلاعات این کانفیگ وجود داشت*'
                '*\n\n• اگر از انقضا این کانفیگ مدتی گذشته، احتمالا از سرور حذف شده ولی هنوز داخل دیتابیس وجود داره *'
                '*\n\n• میتونید سرویس رو پاک کنید، اگر مشکل دیگه ای وجود داره با پشتیبانی در ارتباط باشید*'
                )
        query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='markdown')
        print(e)
    except Exception as e:
        if "specified new message content and reply markup are exactly the same" in str(e):
            return query.answer('آپدیت نشد، احتمالا اطلاعات تغییری نکرده!')
        keyboard = [
            [InlineKeyboardButton("پشتیبانی", callback_data="support")],
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
    if 'personalization_service_' in query.data:
        context.user_data['personalization_service_id'] = int(query.data.replace('personalization_service_', ''))
    get_data_from_db = sqlite_manager.select(table='User', where=f'chat_id = {query.message.chat_id}')

    traffic = abs(get_data_from_db[0][5])
    period = abs(get_data_from_db[0][6])
    price = (traffic * private.PRICE_PER_GB) + (period * private.PRICE_PER_DAY)

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
        check_available = sqlite_manager.select(table='Product', where=f'is_personalization = {query.message.chat_id}')
        inbound_id = sqlite_manager.select(column='inbound_id,name,country', table='Product', where=f'id = {id_}')

        get_data = {'inbound_id': inbound_id[0][0], 'active': 0,
                    'name': inbound_id[0][1], 'country': inbound_id[0][2],
                    'period': period, 'traffic': traffic,
                    'price': price, 'date': datetime.now(pytz.timezone('Asia/Tehran')),
                    'is_personalization': query.message.chat_id,'domain': 'human.ggkala.shop'}

        if check_available:
            sqlite_manager.update({'Product': get_data}, where=f'id = {check_available[0][0]}')
            new_id = check_available[0][0]
        else:
            new_id = sqlite_manager.insert('Product', [get_data])
        texted = ('*• شخصی سازی را تایید میکنید؟:*'
                  f'\n\nحجم سرویس: {traffic}GB'
                  f'\nدوره زمانی: {period} روز'
                  f'\n*قیمت: {price:,}*')
        keyboard = [[InlineKeyboardButton("خیر", callback_data=f"personalization_service_{id_}"),
                     InlineKeyboardButton("بله", callback_data=f"service_{new_id}"),]]

        query.edit_message_text(text=texted, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data.clear()
        return


    sqlite_manager.update({'User': {'traffic':traffic, 'period': period}},where=f'chat_id = {query.message.chat_id}')
    price = (traffic * private.PRICE_PER_GB) + (period * private.PRICE_PER_DAY)

    text = ('*• تو این بخش میتونید سرویس مورد نظر خودتون رو شخصی سازی کنید:*'
            f'\n\nحجم سرویس: {traffic}GB'
            f'\nدوره زمانی: {period} روز'
            f'\n*قیمت: {price:,}*')
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


def personalization_service_lu(update, context):
    query = update.callback_query
    if 'personalization_service_lu_' in query.data:
        if 'period_for_upgrade' in context.user_data and 'traffic_for_upgrade' in context.user_data:
            period_for_upgrade = context.user_data['period_for_upgrade']
            traffic_for_upgrade = context.user_data['traffic_for_upgrade']
            sqlite_manager.update({'User': {'period': int(period_for_upgrade), 'traffic': int(traffic_for_upgrade)}},
                                  where=f'chat_id = {query.message.chat_id}')
        context.user_data['personalization_client_lu_id'] = int(query.data.replace('personalization_service_lu_', ''))

    id_ = context.user_data['personalization_client_lu_id']
    get_data_from_db = sqlite_manager.select(table='User', where=f'chat_id = {query.message.chat_id}')

    traffic = abs(get_data_from_db[0][5])
    period = abs(get_data_from_db[0][6])

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


    sqlite_manager.update({'User': {'traffic':traffic, 'period': period}},where=f'chat_id = {query.message.chat_id}')
    price = (traffic * private.PRICE_PER_GB) + (period * private.PRICE_PER_DAY)

    text = ('*• تو این بخش میتونید سرویس مورد نظر خودتون رو تمدید کنید و یا ارتقا دهید:*'
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
             InlineKeyboardButton("کارت به کارت", callback_data=f'payment_by_card_lu_{id_}')],
            [InlineKeyboardButton("برگشت ↰", callback_data="select_server")]
        ]
        price = (package[0][5] * private.PRICE_PER_GB) + (package[0][6] * private.PRICE_PER_DAY)
        text = (f"<b>❋ بسته انتخابی شامل مشخصات زیر میباشد:</b>\n"
                f"\nدوره زمانی: {package[0][6]} روز"
                f"\nترافیک (حجم): {package[0][5]} گیگابایت"
                f"\nحداکثر کاربر مجاز: ∞"
                f"\n<b>قیمت: {price:,} تومان</b>"
                f"\n\n<b>⤶ برای پرداخت میتونید یکی از روش های زیر رو استفاده کنید:</b>")
        query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        print(e)
        ready_report_problem_to_admin(context, text='PAYMENT PAGER FOR UPGRADE (payment_page_upgrade)', chat_id=chat_id, error=e)
        something_went_wrong(update, context)


def pay_page_get_evidence_for_upgrade(update, context):
    query = update.callback_query
    id_ = int(query.data.replace('payment_by_card_lu_', ''))
    try:
        package = sqlite_manager.select(table='User', where=f'chat_id = {query.message.chat_id}')
        context.user_data['package'] = package
        context.user_data['purchased_id'] = id_
        keyboard = [[InlineKeyboardButton("صفحه اصلی ⤶", callback_data="send_main_message")]]
        price = (package[0][5] * private.PRICE_PER_GB) + (package[0][6] * private.PRICE_PER_DAY)
        text = (f"\n\nمدت اعتبار فاکتور: 10 دقیقه"
                f"\nسرویس: {package[0][6]} روز - {package[0][5]} گیگابایت"
                f"\n*قیمت*: `{price:,}`* تومان *"
                f"\n\n*• لطفا مبلغ رو به شماره‌حساب زیر واریز کنید و اسکرین‌شات یا شماره‌پیگیری رو بعد از همین پیام ارسال کنید.*"
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
        price = (package[0][5] * private.PRICE_PER_GB) + (package[0][6] * private.PRICE_PER_DAY)
        purchased_id = context.user_data['purchased_id']
        text = "- Check the new payment to the card [UPGRADE SERVICE]:\n\n"
        text += f"Name: {user['first_name']}\nUserName: @{user['username']}\nID: {user['id']}\n\n"
        keyboard = [[InlineKeyboardButton("Accept ✅", callback_data=f"accept_card_pay_lu_{purchased_id}")]
            , [InlineKeyboardButton("Refuse ❌", callback_data=f"refuse_card_pay_lu_{purchased_id}")]]
        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            text += f"caption: {update.message.caption}" or 'Witout caption!'
            text += f"\n\nPeriod: {package[0][6]} Day\n Traffic: {package[0][5]}GB\nPrice: {price:,} T"
            context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=file_id, caption=text, reply_markup=InlineKeyboardMarkup(keyboard))
            update.message.reply_text(f'*سفارش شما با موفقیت ثبت شد✅\nنتیجه از طریق همین ربات بهتون اعلام میشه*', parse_mode='markdown')
        elif update.message.text:
            text += f"Text: {update.message.text}"
            text += f"\n\nPeriod: {package[0][6]} Day\n Traffic: {package[0][5]}GB\nPrice: {price:,} T"
            context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, reply_markup=InlineKeyboardMarkup(keyboard))
            update.message.reply_text(f'*درخواست شما با موفقیت ثبت شد✅\nنتیجه از طریق همین ربات بهتون اعلام میشه*', parse_mode='markdown')
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

get_service_con_per = ConversationHandler(
    entry_points=[CallbackQueryHandler(pay_page_get_evidence_for_upgrade, pattern=r'payment_by_card_lu_\d+')],
    states={
        GET_EVIDENCE_PER: [MessageHandler(Filters.all, send_evidence_to_admin_for_upgrade)]
    },
    fallbacks=[],
    conversation_timeout=600,
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
            get_client = sqlite_manager.select(table='Purchased', where=f'id = {id_}')
            user_db = sqlite_manager.select(table='User', where=f'chat_id = {get_client[0][4]}')

            price = (user_db[0][5] * private.PRICE_PER_GB) + (user_db[0][6] * private.PRICE_PER_DAY)

            ret_conf = api_operation.get_client(get_client[0][9])
            now = datetime.now(pytz.timezone('Asia/Tehran'))

            if ret_conf['obj']['enable']:
                tra = ret_conf['obj']['total']
                traffic = (user_db[0][5] * (1024 ** 3)) + tra
                # if ret_conf['obj']['expiryTime'] != 0:
                expiry_timestamp = ret_conf['obj']['expiryTime']
                expiry_datetime = datetime.fromtimestamp(expiry_timestamp / 1000)
                new_expiry_datetime = expiry_datetime + timedelta(days=user_db[0][6])
                my_data = int(new_expiry_datetime.timestamp() * 1000)

            else:
                traffic = user_db[0][5] * (1024 ** 3)
                my_data = now + timedelta(days=user_db[0][6])
                my_data = int(my_data.timestamp() * 1000)
                print(api_operation.reset_client_traffic(get_client[0][7], get_client[0][9]))
            data = {
                "id": int(get_client[0][7]),
                "settings": "{{\"clients\":[{{\"id\":\"{0}\",\"alterId\":0,"
                            "\"email\":\"{1}\",\"limitIp\":0,\"totalGB\":{2},\"expiryTime\":{3},"
                            "\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}}]}}".format(get_client[0][10], get_client[0][9],
                                                                                       traffic, my_data)}
            # breakpoint()
            print(api_operation.update_client(get_client[0][10], data))
            sqlite_manager.update({'Purchased': {'status': 1, 'date': datetime.now(pytz.timezone('Asia/Tehran')), 'notif_day': 0, 'notif_gb': 0}}
                                  ,where=f'client_email = "{get_client[0][9]}"')
            context.bot.send_message(text='سفارش شما برای تمدید و یا ارتقا با موفقیت تایید شد ✅', chat_id=get_client[0][4])
            query.answer('Done ✅')
            query.delete_message()

            record_operation_in_file(chat_id=get_client[0][4], price=price,
                                     name_of_operation=f'تمدید یا ارتقا سرویس {get_client[0][2]}', operation=0,
                                     status_of_pay=1, context=context)

            send_service_to_customer_report(context, status=1, service_name=get_client[0][2], chat_id=get_client[0][4],)

        elif 'ok_card_pay_lu_refuse_' in query.data:
            id_ = int(query.data.replace('ok_card_pay_lu_refuse_', ''))
            get_client = sqlite_manager.select(table='Purchased', where=f'id = {id_}')

            context.bot.send_message(text=f'متاسفانه درخواست شما برای تمدید یا ارتقا سرویس پذیرفته نشد❌\n ارتباط با پشتیبانی: \n @Fupport ', chat_id=get_client[0][4])
            query.answer('Done ✅')
            query.delete_message()

            record_operation_in_file(chat_id=get_client[0][4], price=0,
                                     name_of_operation=f'تمدید یا ارتقا سرویس {get_client[0][2]}', operation=0,
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
    except Exception as e:
        ready_report_problem_to_admin(context, text='TAKE A FREE SERVICE', chat_id=query.message.chat_id, error=e)
        query.answer('ببخشید، مشکلی وجود داشت!')


def help_sec(update, context):
    query = update.callback_query
    text = ("<b>به بخش راهنمای ربات خوش آمدید!</b>"
            "\n\nمیتونید در مورد نحوه اتصال، تجربه شخصی‌سازی ربات، انواع سرویس و موارد مرتبط مطالعه کنید.")
    keyboard = [
        [InlineKeyboardButton("اپلیکیشن های مناسب برای اتصال", callback_data=f"apps_help")],
        [InlineKeyboardButton("شخصی‌سازی-ویژگی‌ها", callback_data=f"personalize_help"),
         InlineKeyboardButton("آشنایی با سرویس‌ها", callback_data=f"robots_service_help")],
        [InlineKeyboardButton("• سوالات متداول", callback_data=f"people_ask_help")],
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
                "\nاین سرویس ها حجم و ترافیک مشخصی دارن و انتخاب راحتی هستن، مانند:\n سرویس 30 روزه - 15 گیگابایت - 30,000 تومن"
                "\n\n<b>• سرویس دلخواه:</b>"
                "\nاین سرویس به شما اجازه میده حجم و ترافیک رو مطابق میل خودتون تنظیم کنید و انتخاب شخصی سازی شده داشته باشید")

        keyboard = [
            [InlineKeyboardButton("🛒 خرید سرویس", callback_data="select_server")],
            [InlineKeyboardButton("برگشت ⤶", callback_data="guidance")]]

    elif help_what == 'people_ask':
        text = "<b>در این قسمت میتونید جواب سوالات متداول رو پیدا کنید:</b>"

        keyboard = [
            [InlineKeyboardButton("استفاده از vpn مصرف اینترنت را افزایش میدهد؟", callback_data="ask_vpn_increase_traffic")],
            [InlineKeyboardButton("میتوانم سرویس خریداری شده را حذف و مبلغ رو برگردانم؟", callback_data="ask_can_i_remove_service")],
            [InlineKeyboardButton("در صورت قطعی و فیلتر شدن سرویس، تکلیف چیست؟", callback_data="ask_what_if_service_blocked")],
            [InlineKeyboardButton("چرا با v2ray، نمیتوانم وارد سایت های ایرانی شوم؟", callback_data="ask_persian_web_dont_open")],
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

    elif help_what == 'persian_web_dont_open':
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


def check_all_configs(context, context_2=None):
    if context_2:
        context = context_2

    get_all = api_operation.get_all_inbounds()
    get_from_db = sqlite_manager.select(column='id,chat_id,client_email,status,date,notif_day,notif_gb', table='Purchased')
    get_users_notif = sqlite_manager.select(column='chat_id,notification_gb,notification_day,name,traffic,period', table='User')
    for config in get_all['obj']:
        for client in config['clientStats']:
            #  check ExpiryTime
            for user in get_from_db:
                if user[2] == client['email']:
                    list_of_notification = [notif for notif in get_users_notif if notif[0] == user[1]]
                    if not client['enable'] and user[3]:
                        text = ("🔴 اطلاع رسانی اتمام سرویس"
                                f"\nدرود {list_of_notification[0][3]} عزیز، سرویس شما با نام {user[2]} به پایان رسید!"
                                f"\nدر صورتی که تمایل دارید نسبت به بررسی و یا تمدید سرویس اقدام کنید.")
                        keyboard = [
                            [InlineKeyboardButton("خرید سرویس جدید", callback_data=f"select_server"),
                             InlineKeyboardButton("تمدید همین سرویس", callback_data=f"personalization_service_lu_{user[0]}")],
                            [InlineKeyboardButton("❤️ تجربه استفاده از فری‌بایت رو به اشتراک بگذارید:", callback_data=f"just_for_show")],
                            [InlineKeyboardButton("عالی بود", callback_data=f"rate_perfect&{list_of_notification[0][3]}&{list_of_notification[0][0]}_{user[0]}")],
                            [InlineKeyboardButton("معمولی و منصفانه بود", callback_data=f"rate_ok&{list_of_notification[0][3]}&{list_of_notification[0][0]}_{user[0]}")],
                            [InlineKeyboardButton("نا امید شدم", callback_data=f"rate_bad&{list_of_notification[0][3]}&{list_of_notification[0][0]}_{user[0]}")],
                            [InlineKeyboardButton("مشکل اتصال داشتم", callback_data=f"rate_connectionProblem&{list_of_notification[0][3]}&{list_of_notification[0][0]}_{user[0]}"),
                             InlineKeyboardButton("نظری ندارم", callback_data=f"rate_haveNotIdea&{list_of_notification[0][3]}&{list_of_notification[0][0]}_{user[0]}")]
                        ]
                        context.bot.send_message(user[1], text=text, reply_markup=InlineKeyboardMarkup(keyboard))
                        sqlite_manager.update({'Purchased': {'status': 0}}, where=f'id = {user[0]}')
                        context.bot.send_message(ADMIN_CHAT_ID, text=f'Service OF {list_of_notification[0][3]} Named {user[0]} Has Be Ended')
                    elif client['enable'] and not user[3]:
                        sqlite_manager.update(
                            {'Purchased': {'status': 1, 'date': datetime.now(pytz.timezone('Asia/Tehran')), 'notif_day': 0, 'notif_gb': 0}}
                            , where=f'id = "{user[0]}"')

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
                                 InlineKeyboardButton("تمدید یا ارتقا سرویس", callback_data=f"personalization_service_lu_{user[0]}")]]

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
        check = query.data.replace('_', ' ')
        context.bot.send_message(ADMIN_CHAT_ID, text=check.replace('&', ' '))
        server_name = sqlite_manager.select(column='client_email', table='Purchased', where=f'id = {purchased_id}')[0][0]
        text = ("🔴 اطلاع رسانی اتمام سرویس"
                f"\nدرود {query.from_user['name']} عزیز، سرویس شما با نام {server_name} به پایان رسید!"
                f"\nدر صورتی که تمایل دارید نسبت به بررسی و یا تمدید سرویس اقدام کنید.")

        keyboard = [
            [InlineKeyboardButton("خرید سرویس جدید", callback_data=f"select_server"),
             InlineKeyboardButton("تمدید همین سرویس", callback_data=f"personalization_service_lu_{purchased_id}")]]
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
        [InlineKeyboardButton("• نوتیفیکیشن", callback_data="notification"),
         InlineKeyboardButton("• رتبه‌بندی", callback_data="ranking_page")],
        [InlineKeyboardButton("• تراکنش های مالی", callback_data="financial_transactions"),
         InlineKeyboardButton("• کیف پول", callback_data="wallet_page")],
        [InlineKeyboardButton("برگشت ↰", callback_data="main_menu")]
    ]
    query.edit_message_text(text='*در این قسمت میتونید تنظیمات ربات رو مشاهده و یا شخصی سازی کنید:*', parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))


def change_notif(update, context):
    query = update.callback_query
    get_data_from_db = sqlite_manager.select(table='User', where=f'chat_id = {query.message.chat_id}')

    try:
        traffic = abs(get_data_from_db[0][8])
        period = abs(get_data_from_db[0][9])

        if 'notif_traffic_low_5' in query.data:
            traffic_t = int(query.data.replace('notif_traffic_low_', ''))
            traffic = traffic - traffic_t
            traffic = traffic if traffic >= 1 else 5
        elif 'notif_traffic_high_5' in query.data:
            traffic_t = int(query.data.replace('notif_traffic_high_', ''))
            traffic = traffic + traffic_t
            traffic = traffic if traffic <= 100 else 100
        elif 'notif_day_low_1' in query.data:
            period_t = int(query.data.replace('notif_day_low_', ''))
            period = period - period_t
            period = period if period >= 1 else 1
        elif 'notif_day_high_1' in query.data:
            period_t = int(query.data.replace('notif_day_high_', ''))
            period = period + period_t
            period = period if period <= 100 else 100


        sqlite_manager.update({'User': {'notification_gb':traffic, 'notification_day': period}},where=f'chat_id = {query.message.chat_id}')

        text = ('*• تنظیمات رو مطابق میل خودتون تغییر بدید:*'
                f'\n• ربات 5 دقیقه یک بار اطلاعات رو بررسی میکنه.'
                f'\n\nدریافت اعلان بعد مصرف {traffic}% حجم'
                f'\nدریافت اعلان {period} روز قبل تمام شدن سرویس')
        keyboard = [
            [InlineKeyboardButton("«", callback_data="notif_traffic_low_5"),
             InlineKeyboardButton(f"{traffic}%", callback_data="just_for_show"),
             InlineKeyboardButton("»", callback_data="notif_traffic_high_5")],
            [InlineKeyboardButton("«", callback_data="notif_day_low_1"),
             InlineKeyboardButton(f"{period}Day", callback_data="just_for_show"),
             InlineKeyboardButton("»", callback_data="notif_day_high_1")],
            [InlineKeyboardButton("برگشت ↰", callback_data="setting")]
        ]
        query.edit_message_text(text=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        query.answer('شما نمیتونید ولوم رو کمتر یا بیشتر از مقدار مجاز قرار بدید!')
        print(e)


def get_pay_file(update, context):
    query = update.callback_query
    with open(f'financial_transactions/{query.message.chat_id}.txt', 'r', encoding='utf-8') as file:
        context.bot.send_document(chat_id=query.message.chat_id, document= file,
                                  filename=f'All transactions of {query.from_user["name"]}')
    query.answer('فایل برای شما ارسال شد!')


def financial_transactions(update, context):
    query = update.callback_query
    try:
        keyboard = [
            [InlineKeyboardButton("دریافت فایل کامل", callback_data="get_pay_file")],
            [InlineKeyboardButton("برگشت ↰", callback_data="setting")]
        ]
        with open(f'financial_transactions/{query.message.chat_id}.txt', 'r', encoding='utf-8') as e:
            get_factors = e.read()
        query.edit_message_text(text=f"لیست تراکنش های مالی شما: \n{get_factors[:4000]}", reply_markup=InlineKeyboardMarkup(keyboard))
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
        sqlite_manager.delete({'Credit_History': ["active", 0]})
        get_credit = sqlite_manager.select(column='wallet', table='User', where=f'chat_id = {chat_id}')[0][0]
        lasts_operation = sqlite_manager.select(table='Credit_History', where=f'chat_id = {chat_id} and active = 1',
                                                order_by='id DESC', limit=5)

        if lasts_operation:
            last_op = human_readable(f'{lasts_operation[0][7]}')
            last_5 = "• تراکنش های اخیر:\n"
            last_5 += "\n".join([f"{'💰 دریافت' if op[4] else '💸 برداشت'} {op[5]:,} تومان - {human_readable(op[7])}" for op in lasts_operation])

        else:
            last_op ='شما تا به حال تراکنشی در کیف پول نداشتید!'
            last_5 = ''

        keyboard = [
            [InlineKeyboardButton("تازه سازی ⟳", callback_data=f"wallet_page"),
             InlineKeyboardButton("افزایش موجودی ↟", callback_data=f"buy_credit_volume")],
            [InlineKeyboardButton("مشاهده تراکنش های کیف پول", callback_data=f"financial_transactions_wallet")],
            [InlineKeyboardButton("برگشت ↰", callback_data="setting")]]

        text_ = (
            f"<b>اطلاعات کیف پول شما:</b>"
            f"\n\n• موجودی حساب: {get_credit:,} تومان"
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
        price = package[0][0]
        text = (f"\n\nمدت اعتبار فاکتور: 10 دقیقه"
                f"\n*قیمت*: `{price:,}`* تومان *"
                f"\n\n*• لطفا مبلغ رو به شماره‌حساب زیر واریز کنید و اسکرین‌شات یا شماره‌پیگیری رو بعد از همین پیام ارسال کنید.*"
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
        price = package[0][0]
        text = "- Check the new payment to the card [CHARGE CREDIT WALLET]:\n\n"
        text += f"Name: {user['first_name']}\nUserName: @{user['username']}\nID: {user['id']}\n\n"
        keyboard = [[InlineKeyboardButton("Accept ✅", callback_data=f"accept_card_pay_credit_{credit_id}")]
            , [InlineKeyboardButton("Refuse ❌", callback_data=f"refuse_card_pay_credit_{credit_id}")]]
        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            text += f"caption: {update.message.caption}" or 'Witout caption!'
            text += f"\n\nPrice: {price:,} T"
            context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=file_id, caption=text, reply_markup=InlineKeyboardMarkup(keyboard))
            update.message.reply_text(f'*سفارش شما با موفقیت ثبت شد✅\nنتیجه از طریق همین ربات بهتون اعلام میشه*', parse_mode='markdown')
        elif update.message.text:
            text += f"Text: {update.message.text}"
            text += f"\n\nPrice: {price:,} T"
            context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, reply_markup=InlineKeyboardMarkup(keyboard))
            update.message.reply_text(f'*درخواست شما با موفقیت ثبت شد✅\nنتیجه از طریق همین ربات بهتون اعلام میشه*', parse_mode='markdown')
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
    conversation_timeout=600,
    per_chat=True,
    allow_reentry=True
)

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
            get_credit = sqlite_manager.select(column='chat_id,value', table='Credit_History', where=f'id = {id_}')

            sqlite_manager.update({'Credit_History': {'active': 1, 'date': datetime.now(pytz.timezone('Asia/Tehran'))}}
                                  ,where=f'id = "{id_}"')

            wallet_manage.add_to_wallet_without_history(get_credit[0][0], get_credit[0][1])

            context.bot.send_message(text='سفارش شما برای واریز وجه به کیف پول با موفقیت تایید شد ✅', chat_id=get_credit[0][0])
            query.answer('Done ✅')
            query.delete_message()

            record_operation_in_file(chat_id=get_credit[0][0], price=get_credit[0][1],
                                     name_of_operation=f'واریز به کیف پول', operation=1,
                                     status_of_pay=1, context=context)

            context.bot.send_message(ADMIN_CHAT_ID, '🟢 WALLET OPERATOIN SUCCESSFULL')

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

            price = (package[0][5] * private.PRICE_PER_GB) + (package[0][6] * private.PRICE_PER_DAY)

            keyboard = [[InlineKeyboardButton("تایید و پرداخت ✅", callback_data=f"accept_wallet_upgrade_pay_{id_}")]
                        if get_wallet[0][0] >= price else [InlineKeyboardButton("افزایش موجودی ↟", callback_data=f"buy_credit_volume")],
                        [InlineKeyboardButton("برگشت ⤶", callback_data="my_service")]]

            available_or_not = "اطلاعات زیر رو بررسی کنید و در صورت تایید پرداخت رو نهایی کنید:" \
                if get_wallet[0][0] >= price else "متاسفانه موجودی کیف پول شما کافی نیست، میتونید با گزینه افزایش موجودی اعتبار خودتون رو افزایش بدید."

            price = (package[0][5] * private.PRICE_PER_GB) + (package[0][6] * private.PRICE_PER_DAY)
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
                get_client = sqlite_manager.select(table='Purchased', where=f'id = {id_}')
                user_db = sqlite_manager.select(table='User', where=f'chat_id = {get_client[0][4]}')

                price = (user_db[0][5] * private.PRICE_PER_GB) + (user_db[0][6] * private.PRICE_PER_DAY)

                ret_conf = api_operation.get_client(get_client[0][9])
                now = datetime.now(pytz.timezone('Asia/Tehran'))

                if ret_conf['obj']['enable']:
                    tra = ret_conf['obj']['total']
                    traffic = (user_db[0][5] * (1024 ** 3)) + tra
                    # if ret_conf['obj']['expiryTime'] != 0:
                    expiry_timestamp = ret_conf['obj']['expiryTime']
                    expiry_datetime = datetime.fromtimestamp(expiry_timestamp / 1000)
                    new_expiry_datetime = expiry_datetime + timedelta(days=user_db[0][6])
                    my_data = int(new_expiry_datetime.timestamp() * 1000)

                else:
                    traffic = user_db[0][5] * (1024 ** 3)
                    my_data = now + timedelta(days=user_db[0][6])
                    my_data = int(my_data.timestamp() * 1000)
                    print(api_operation.reset_client_traffic(get_client[0][7], get_client[0][9]))
                data = {
                    "id": int(get_client[0][7]),
                    "settings": "{{\"clients\":[{{\"id\":\"{0}\",\"alterId\":0,"
                                "\"email\":\"{1}\",\"limitIp\":0,\"totalGB\":{2},\"expiryTime\":{3},"
                                "\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}}]}}".format(get_client[0][10], get_client[0][9],
                                                                                           traffic, my_data)}
                # breakpoint()
                print(api_operation.update_client(get_client[0][10], data))

                sqlite_manager.update({'Purchased': {'status': 1, 'date': datetime.now(pytz.timezone('Asia/Tehran')), 'notif_day': 0, 'notif_gb': 0}}
                                      ,where=f'client_email = "{get_client[0][9]}"')

                record_operation_in_file(chat_id=get_client[0][4], price=price,
                                         name_of_operation=f'تمدید یا ارتقا سرویس {get_client[0][2]}', operation=0,
                                         status_of_pay=1, context=context)

                wallet_manage.less_from_wallet(query.from_user['id'], price, user_detail=query.from_user)

                keyboard = [[InlineKeyboardButton("برگشت ⤶", callback_data="my_service")]]
                query.edit_message_text(text='سرویس شما با موفقیت ارتقا یافت.✅', reply_markup=InlineKeyboardMarkup(keyboard))

            except Exception as e:
                ready_report_problem_to_admin(context, 'PAY FROM WAWLLET FOR UPGRADE',
                                              update.message.from_user['id'], e)
                print(e)
                query.answer('مشکلی وجود دارد! گزارش مشکل به ادمین ارسال شد')
        elif 'payment_by_wallet_' in query.data:
            id_ = int(query.data.replace('payment_by_wallet_', ''))
            package = sqlite_manager.select(table='Product', where=f'id = {id_}')
            context.user_data['package'] = package

            keyboard = [[InlineKeyboardButton("تایید و پرداخت ✅", callback_data=f"accept_wallet_pay_{id_}")]
                        if get_wallet[0][0] >= package[0][7] else [InlineKeyboardButton("افزایش موجودی ↟", callback_data=f"buy_credit")],
                        [InlineKeyboardButton("برگشت ⤶", callback_data="select_server")]]

            available_or_not = "اطلاعات زیر رو بررسی کنید و در صورت تایید پرداخت رو نهایی کنید:" \
                if get_wallet[0][0] >= package[0][7] else "متاسفانه موجودی کیف پول شما کافی نیست، میتونید با گزینه افزایش موجودی اعتبار خودتون رو افزایش بدید."

            ex = sqlite_manager.insert('Purchased', rows=[
                {'active': 0, 'status': 0, 'name': user["first_name"], 'user_name': user["username"],
                 'chat_id': int(user["id"]), 'product_id': id_, 'notif_day': 0, 'notif_gb': 0}])
            context.user_data['purchased_id'] = ex
            text = (f"{available_or_not}"
                    f"\n\nسرویس: {package[0][5]} روز - {package[0][6]} گیگابایت"
                    f"\n*قیمت*: {package[0][7]:,}* تومان *"
                    f"\n*موجودی کیف پول*: {get_wallet[0][0]:,}* تومان *"

                    f"\n\n• همیشه میتوانید با حذف کردن سرویس در قسمت *سرویس های من*، مبلغ باقی مونده رو به کیف پول خودتون برگردونید"
                    f"\n\n• با تایید کردن، سرور مستقیم برای شما فعال میشه")
            query.edit_message_text(text=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        elif 'accept_wallet_pay_' in query.data:
            get_p_id = context.user_data['purchased_id']
            check = send_clean_for_customer(query, context, get_p_id)
            if check:
                get_db = context.user_data['package'][0][7]
                wallet_manage.less_from_wallet(query.from_user['id'], get_db, query.from_user)

                keyboard = [[InlineKeyboardButton("برگشت ⤶", callback_data="select_server")]]
                query.edit_message_text(text='پرداخت با موفقیت انجام شد.✅', parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                query.answer('مشکلی وجود داره!')

    except Exception as e:
        print(e)
        ready_report_problem_to_admin(context, 'PAY FROM WAWLLET', query.from_user['id'], e)
        something_went_wrong(update, context)


def remove_service(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id

    email = query.data.replace('remove_service_', '')
    email = email.replace('accept_rm_ser_', '')
    ret_conf = api_operation.get_client(email)

    try:
        upload_gb = int(ret_conf['obj']['up']) / (1024 ** 3)
        download_gb = int(ret_conf['obj']['down']) / (1024 ** 3)
        usage_traffic = round(upload_gb + download_gb, 2)
        total_traffic = int(ret_conf['obj']['total']) / (1024 ** 3)
        left_traffic = total_traffic - usage_traffic

        expiry_timestamp = ret_conf['obj']['expiryTime'] / 1000
        expiry_date = datetime.fromtimestamp(expiry_timestamp)
        days_lefts = (expiry_date - datetime.now()).days
        days_lefts = days_lefts if days_lefts >= 0 else 0

        price = int((left_traffic * private.PRICE_PER_GB) + (days_lefts * private.PRICE_PER_DAY))

        if 'remove_service_' in query.data:
            keyboard = [[InlineKeyboardButton("✓ بله مطمئنم", callback_data=f"accept_rm_ser_{email}")],
                        [InlineKeyboardButton("✗ منصرف شدم", callback_data="my_service")]]

            text = ('*لطفا اطلاعات زیر رو بررسی کنید:*'
                    f'\n\n• زمان باقی مانده سرویس: {days_lefts} روز'
                    f'\n• ترافیک باقی مانده سرویس: {left_traffic}GB'
                    f'\n• مبلغ قابل بازگشت به کیف پول:* {price:,} تومان*'
                    f'\n\n*آیا از حذف این سرویس مطمئن هستید؟*'
                    )

            if not ret_conf['obj']['enable']:

                text = ('*این سرویس تمام شده، اگر مایل به تمدید نیستید میتونید حذفش کنید:*'
                        f'\n\n*آیا از حذف این سرویس مطمئن هستید؟*'
                        )

        elif 'accept_rm_ser_' in query.data:

            get_uuid = sqlite_manager.select(column='client_id,inbound_id,name', table='Purchased', where=f'client_email = "{email}"')
            api_operation.del_client(get_uuid[0][1], get_uuid[0][0])

            sqlite_manager.delete({'Purchased': ['client_email', email]})

            keyboard = [[InlineKeyboardButton("برگشت ⤶", callback_data="my_service")]]

            text = f'*سرویس با موفقیت حذف شد و مبلغ {price:,} تومان به کیف پول شما برگشت ✅*'
            if not ret_conf['obj']['enable']:
                text = '*سرویس با موفقیت حذف شد ✅*'
            else:
                wallet_manage.add_to_wallet(chat_id, price)

                record_operation_in_file(chat_id=chat_id, price=price,
                                         name_of_operation=f'حذف سرویس و بازپرداخت به کیف پول {get_uuid[0][2]}', operation=1,
                                         status_of_pay=1, context=context)

        query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='markdown')

    except Exception as e:
        print(e)
        ready_report_problem_to_admin(context, 'REMOVE SERVICE',
                                      update.message.from_user['id'], e)
        query.answer('مشکلی وجود دارد!')


def remove_service(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id

    email = query.data.replace('remove_service_', '')
    email = email.replace('accept_rm_ser_', '')
    ret_conf = api_operation.get_client(email)

    try:
        upload_gb = int(ret_conf['obj']['up']) / (1024 ** 3)
        download_gb = int(ret_conf['obj']['down']) / (1024 ** 3)
        usage_traffic = round(upload_gb + download_gb, 2)
        total_traffic = int(ret_conf['obj']['total']) / (1024 ** 3)
        left_traffic = total_traffic - usage_traffic

        expiry_timestamp = ret_conf['obj']['expiryTime'] / 1000
        expiry_date = datetime.fromtimestamp(expiry_timestamp)
        days_lefts = (expiry_date - datetime.now()).days
        days_lefts = days_lefts if days_lefts >= 0 else 0

        price = int((left_traffic * private.PRICE_PER_GB) + (days_lefts * private.PRICE_PER_DAY))

        if 'remove_service_' in query.data:
            keyboard = [[InlineKeyboardButton("✓ بله مطمئنم", callback_data=f"accept_rm_ser_{email}")],
                        [InlineKeyboardButton("✗ منصرف شدم", callback_data="my_service")]]

            text = ('*لطفا اطلاعات زیر رو بررسی کنید:*'
                    f'\n\n• زمان باقی مانده سرویس: {days_lefts} روز'
                    f'\n• ترافیک باقی مانده سرویس: {left_traffic}GB'
                    f'\n• مبلغ قابل بازگشت به کیف پول:* {price:,} تومان*'
                    f'\n\n*آیا از حذف این سرویس مطمئن هستید؟*'
                    )

            if not ret_conf['obj']['enable']:

                text = ('*این سرویس تمام شده، اگر مایل به تمدید نیستید میتونید حذفش کنید:*'
                        f'\n\n*آیا از حذف این سرویس مطمئن هستید؟*'
                        )

        elif 'accept_rm_ser_' in query.data:

            get_uuid = sqlite_manager.select(column='client_id,inbound_id,name', table='Purchased', where=f'client_email = "{email}"')
            api_operation.del_client(get_uuid[0][1], get_uuid[0][0])

            sqlite_manager.delete({'Purchased': ['client_email', email]})

            keyboard = [[InlineKeyboardButton("برگشت ⤶", callback_data="main_menu")]]

            text = f'*سرویس با موفقیت حذف شد و مبلغ {price:,} تومان به کیف پول شما برگشت ✅*'
            if not ret_conf['obj']['enable']:
                text = '*سرویس با موفقیت حذف شد ✅*'
            else:
                wallet_manage.add_to_wallet(chat_id, price, query.from_user)

                record_operation_in_file(chat_id=chat_id, price=price,
                                         name_of_operation=f'حذف سرویس و بازپرداخت به کیف پول {get_uuid[0][2]}', operation=1,
                                         status_of_pay=1, context=context)

        query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='markdown')

    except Exception as e:
        print(e)
        ready_report_problem_to_admin(context, 'REMOVE SERVICE',
                                      update.message.from_user['id'], e)
        query.answer('مشکلی وجود دارد!')


def admin_reserve_service(update, context):
    # user_message = 'chat_id,product_id, message'

    user_message = update.message.text.replace('/admin_reserve_service ', '').split(',')
    try:
        user = sqlite_manager.select(column='name,user_name', table='User', where=f'chat_id = {user_message[0]}')

        ex = sqlite_manager.insert('Purchased', rows=[
            {'active': 0, 'status': 0, 'name': user[0][0], 'user_name': user[0][1],
             'chat_id': user_message[0], 'product_id': user_message[1], 'notif_day': 0, 'notif_gb': 0}])

        send_clean_for_customer(None, context, ex)

        if user_message[2]:
            message_to_user(update, context, user_message[2], user_message[0])
        update.message.reply_text('RESERVE SERVICE OK')
    except Exception as e:
        update.message.reply_text('something went wrong')
        ready_report_problem_to_admin(context, 'ADMIN RESERVE SERIVE', update.message.from_user['id'], e)


