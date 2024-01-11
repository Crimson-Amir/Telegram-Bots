import random
from datetime import datetime, timedelta
import telegram.error
import private
from sqlite_manager import ManageDb
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
import uuid
from private import ADMIN_CHAT_ID
from admin_task import add_client_bot, api_operation, add_service
import qrcode
from io import BytesIO
import pytz

sqlite_manager = ManageDb('v2ray')
GET_EVIDENCE = 0
GET_EVIDENCE_PER = 0

def not_ready_yet(update, context):
    query = update.callback_query
    query.answer(text="ببخشید، درحال توسعه است.", show_alert=False)


def something_went_wrong(update, context):
    query = update.callback_query
    query.answer(text="مشکلی وجود دارد!", show_alert=False)


def buy_service(update, context):
    try:
        query = update.callback_query
        plans = sqlite_manager.select(table='Product', where='active = 1')
        server_name_unic = {name[3]:name[4] for name in plans}
        keyboard = [[InlineKeyboardButton(ser, callback_data=cou)] for ser, cou in server_name_unic.items()]
        keyboard.append([InlineKeyboardButton("برگشت ↰", callback_data="main_menu")])
        query.edit_message_text(text="<b>سرور مورد نظر خودتون رو انتخاب کنید:</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
    except Exception as e:
        print(e)
        something_went_wrong(update, context)


def all_query_handler(update, context):
    try:
        text = "<b>سرویس مناسب خودتون رو انتخاب کنید:\n\n✪ با انتخاب گزینه 'دلخواه' میتونید یک سرویس شخصی سازی شده بسازید!</b>"
        query = update.callback_query
        plans = sqlite_manager.select(table='Product', where=f'active = 1 and country = "{query.data}"')
        country_unic = {name[4] for name in plans}
        for country in country_unic:
            if query.data == country:
                service_list = [service for service in plans if service[4] == country]
                keyboard = [[InlineKeyboardButton(f"سرویس {pattern[5]} روزه - {pattern[6]} گیگابایت - {pattern[7]:,} تومان",
                                                  callback_data=f"service_{pattern[0]}")] for pattern in service_list]

                keyboard.append([InlineKeyboardButton("سرویس دلخواه ४", callback_data=f"personalization_service_{plans[0][0]}")])
                keyboard.append([InlineKeyboardButton("برگشت ↰", callback_data="select_server")])
                query.edit_message_text(text= text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
    except Exception as e:
        print(e)
        something_went_wrong(update, context)


def payment_page(update, context):
    query = update.callback_query
    id_ = int(query.data.replace('service_', ''))
    try:
        package = sqlite_manager.select(table='Product', where=f'id = {id_}')
        if package[0][7]:
            keyboard = [
                [InlineKeyboardButton("کارت به کارت", callback_data=f'payment_by_card_{id_}')],
                [InlineKeyboardButton("پرداخت از طریق کیف پول", callback_data=f'payment_by_wallet_{id_}')],
                [InlineKeyboardButton("پرداخت از طریق کریپتو", callback_data=f'payment_by_crypto_{id_}')],
                [InlineKeyboardButton("برگشت ↰", callback_data="select_server")]
            ]
        else:
            free = sqlite_manager.select(column='free_service', table='User', where=f'chat_id = {query.message.chat_id}')
            if free[0][0]:
                query.answer('ببخشید، شما یک بار این بسته را دریافت کردید!')
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
        print(e)
        something_went_wrong(update, context)


def pay_page_get_evidence(update, context):
    query = update.callback_query
    user = query.from_user
    uuid_ = str(uuid.uuid4())[:-7]
    id_ = int(query.data.replace('payment_by_card_', ''))
    try:
        package = sqlite_manager.select(table='Product', where=f'id = {id_}')
        context.user_data['package'] = package
        keyboard = [[InlineKeyboardButton("صفحه اصلی ⤶", callback_data="send_main_message")]]
        ex = sqlite_manager.insert('Purchased',rows= [{'active': 0,'status': 0, 'name': user["first_name"],'user_name': user["username"],
                                                       'chat_id': int(user["id"]),'factor_id': uuid_,'product_id': id_}])
        context.user_data['purchased_id'] = ex
        text = (f"شماره سفارش:"
                f"\n`{uuid_}`"
                f"\n\nمدت اعتبار فاکتور: 10 دقیقه"
                f"\nسرویس: {package[0][5]} روز - {package[0][6]} گیگابایت"
                f"\n*قیمت*: `{package[0][7]:,}`* تومان *"
                f"\n\n*• لطفا مبلغ رو به شماره‌حساب زیر واریز کنید و اسکرین‌شات یا شماره‌پیگیری رو بعد از همین پیام ارسال کنید.*"
                f"\n\n`6219861938619417` - امیرحسین نجفی"
                f"\n\n*• بعد از تایید شدن پرداخت، سرویس برای شما ارسال میشه، زمان تقریبی 5 دقیقه الی 3 ساعت.*")
        query.edit_message_text(text=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return GET_EVIDENCE
    except Exception as e:
        print(e)
        something_went_wrong(update, context)


def send_evidence_to_admin(update, context):
    package = context.user_data['package']
    purchased_id = context.user_data['purchased_id']
    text = "- Check the new payment to the card:\n\n"
    keyboard = [[InlineKeyboardButton("Accept ✅", callback_data=f"accept_card_pay_{purchased_id}")]
        , [InlineKeyboardButton("Refuse ❌", callback_data=f"refuse_card_pay_{purchased_id}")]]
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        text += f"caption: {update.message.caption}" or 'Witout caption!'
        text += f"\n\nServer: `{package[0][4]}`\nInbound id: `{package[0][1]}`\nPeriod: {package[0][5]} Day\n Traffic: {package[0][6]}GB\nPrice: {package[0][7]:,} T"
        context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=file_id, caption=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        update.message.reply_text(f'*سفارش شما با موفقیت ثبت شد✅\nنتیجه از طریق همین ربات بهتون اعلام میشه*', parse_mode='markdown')
    elif update.message.text:
        text += f"Text: {update.message.text}"
        text += f"\n\nServer: `{package[0][4]}`\nInbound id: `{package[0][1]}`\nPeriod: {package[0][5]} Day\n Traffic: {package[0][6]}GB\nPrice: {package[0][7]:,} T"
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        update.message.reply_text(f'*درخواست شما با موفقیت ثبت شد✅\nنتیجه از طریق همین ربات بهتون اعلام میشه*', parse_mode='markdown')
    else:
        update.message.reply_text('مشکلی وجود داره!')

    context.user_data.clear()
    return ConversationHandler.END


def cancel(update, context):
    query = update.callback_query
    query.answer(text="با موفقیت کنسل شد!", show_alert=False)
    return ConversationHandler.END


get_service_con = ConversationHandler(
    entry_points=[CallbackQueryHandler(pay_page_get_evidence, pattern=r'payment_by_card_\d+')],
    states={
        GET_EVIDENCE: [MessageHandler(Filters.all, send_evidence_to_admin)]
    },
    fallbacks=[CallbackQueryHandler(cancel, pattern='cancel')],
    conversation_timeout=600,
    per_chat=True,
    allow_reentry=True
)


def send_clean_for_customer(query, context, id_):
    create = add_client_bot(id_)
    if create:
        try:
            get_client = sqlite_manager.select(table='Purchased', where=f'id = {id_}')
            returned = api_operation.get_client_url(client_email=get_client[0][9], inbound_id=get_client[0][7])
            if returned:
                returned_copy = f'`{returned}`'
                qr_code = qrcode.make(returned)
                qr_image = qr_code.get_image()
                buffer = BytesIO()
                qr_image.save(buffer, format='PNG')
                binary_data = buffer.getvalue()
                keyboard = [[InlineKeyboardButton("🎛 سرویس های من", callback_data=f"my_service")],
                            [InlineKeyboardButton("دریافت به صورت فایل", callback_data=f"create_txt_file")]]
                context.user_data['v2ray_client'] = returned
                context.bot.send_photo(photo=binary_data,
                                       caption=f' سرویس شما با موفقیت فعال شد✅\n\n*• میتونید جزئیات سرویس رو از بخش "سرویس های من" مشاهده کنید.\n\n✪ لطفا سرویس رو به صورت مستقیم از طریق پیام رسان های ایرانی یا پیامک ارسال نکنید، با کلیک روی گزینه "دانلود به صورت فایل" سرویس رو به صورت فایل ارسال کنید.* \n\n\nلینک:\n{returned_copy}',
                                       chat_id=get_client[0][4], reply_markup=InlineKeyboardMarkup(keyboard),
                                       parse_mode='markdown')
                query.answer('Done ✅')
                query.delete_message()
            else:
                print('wrong: ', returned)
                query.answer('Wrong')
        except Exception as e:
            print(e)
            query.answer(f'Failed ❌ | {e}')
            query.delete_message()
    else:
        query.answer('Failed ❌')


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

        elif 'cancel_pay' in query.data:
            query.answer('Done ✅')
            query.delete_message()
    except Exception as e:
        print('errot:', e)


def my_service(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    get_purchased = sqlite_manager.select(table='Purchased', where=f'chat_id = {chat_id} and active = 1')
    if get_purchased:
        keyboard = [[InlineKeyboardButton(f"{'✅' if ser[11] == 1 else '❌'} {ser[9]}", callback_data=f"view_service_{ser[9]}")] for ser in get_purchased]
        keyboard.append([InlineKeyboardButton("برگشت ↰", callback_data="main_menu")])
        try:
            query.edit_message_text('*برای مشاهده جزئیات، سرویس مورد نظر خودتان را انتخاب کنید:*', reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='markdown')
        except telegram.error.BadRequest:
            query.answer('در یک پیام جدید فرستادم!')
            context.bot.send_message(chat_id=chat_id, text='*برای مشاهده جزئیات، سرویس مورد نظر خودتان را انتخاب کنید:*', reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='markdown')
    else:
        query.answer('سرویسی برای شما یافت نشد!')


def server_detail_customer(update, context):
    query = update.callback_query
    email = update.callback_query.data.replace('view_service_', '')
    try:
        get_data = sqlite_manager.select(table='Purchased', where=f'client_email = "{email}"')
        ret_conf = api_operation.get_client(email)
        keyboard = [[InlineKeyboardButton("تمدید و ارتقا ↟", callback_data=f"personalization_service_lu_{get_data[0][0]}")],
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
        days_lefts = (expiry_date - datetime.now()).days

        change_active = '✅' if ret_conf['obj']['enable'] else '❌'
        purchase_date = datetime.strptime(get_data[0][12], "%Y-%m-%d %H:%M:%S.%f%z").replace(tzinfo=None)
        days_left_2 = abs(days_lefts)
        exist_day = f"({days_left_2} روز {'مانده' if days_lefts >= 0 else 'گذشته'})"

        context.user_data['period_for_upgrade'] = (expiry_date - purchase_date).days
        context.user_data['traffic_for_upgrade'] = total_traffic

        text_ = (
            f"<b>اطلاعات سرویس انتخاب شده:</b>"
            f"\n\n🔷 نام سرویس: {email}"
            f"\n💡 فعال: {change_active}"
            f"\n📅 تاریخ انقضا: {expiry_month} {exist_day}"
            f"\n🔼 آپلود↑: {upload_gb}"
            f"\n🔽 دانلود↓: {download_gb}"
            f"\n📊 مصرف کل: {usage_traffic}/{total_traffic}GB"
            f"\n\n⏰ تاریخ خرید: {purchase_date.strftime('%H:%M:%S | %Y/%m/%d')}"
            f"\n\n🌐 آدرس سرویس:\n <code>{get_data[0][8]}</code>"
        )
        query.edit_message_text(text=text_, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
        sqlite_manager.update({'Purchased': {'status': 1 if ret_conf['obj']['enable'] else 0}}, where=f'where client_email = "{email}"')
    except Exception as e:
        query.answer('مشکلی وجود دارد!')
        print(e)


def create_file_and_return(update, context):
    query = update.callback_query
    try:
        config_ = context.user_data['v2ray_client']
        random_number = random.randint(0, 5)
        with open(f'text_file/create_v2ray_file_with_id_{random_number}.txt', 'w') as f:
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

    traffic = get_data_from_db[0][5]
    period = get_data_from_db[0][6]
    price = (traffic * private.PRICE_PER_GB) + (period * private.PRICE_PER_DAY)

    if 'traffic_low_10' in query.data or 'traffic_low_1' in query.data:
        traffic_t = int(query.data.replace('traffic_low_', ''))
        traffic = traffic - traffic_t
        traffic = traffic if traffic >= 0 else 0
    elif 'traffic_high_1' in query.data or 'traffic_high_10' in query.data:
        traffic_t = int(query.data.replace('traffic_high_', ''))
        traffic = traffic + traffic_t
        traffic = traffic if traffic <= 500 else 500
    elif 'period_low_10' in query.data or 'period_low_1' in query.data:
        period_t = int(query.data.replace('period_low_', ''))
        period = period - period_t
        period = period if period >= 1 else 1
    elif 'period_high_1' in query.data or 'period_high_10' in query.data:
        period_t = int(query.data.replace('period_high_', ''))
        period = period + period_t
        period = period if period <= 500 else 500

    elif 'accept_personalization' in query.data:
        id_ =  context.user_data['personalization_service_id']
        check_available = sqlite_manager.select(table='Product', where=f'is_personalization = {query.message.chat_id}')
        inbound_id = sqlite_manager.select(column='inbound_id,name,country', table='Product', where=f'id = {id_}')

        get_data = {'inbound_id': inbound_id[0][0], 'active': 0,
                    'name': inbound_id[0][1], 'country': inbound_id[0][2],
                    'period': period, 'traffic': traffic,
                    'price': price, 'date': datetime.now(pytz.timezone('Asia/Tehran')),
                    'is_personalization': query.message.chat_id}

        if check_available:
            sqlite_manager.update({'Product': get_data}, where=f'where id = {check_available[0][0]}')
            new_id = check_available[0][0]
        else:
            new_id = sqlite_manager.insert('Product', [get_data])
        texted = ('*• شخصی سازی را تایید میکنید؟:*'
                  f'\n\nحجم سرویس: {traffic}GB'
                  f'\nدوره زمانی: {period} روز'
                  f'\n*قیمت: {price:,}*')
        keyboard = [[InlineKeyboardButton("خیر❌", callback_data=f"personalization_service_{id_}"),
                     InlineKeyboardButton("بله✅", callback_data=f"service_{new_id}"),]]

        query.edit_message_text(text=texted, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data.clear()
        return


    sqlite_manager.update({'User': {'traffic':traffic, 'period': period}},where=f'where chat_id = {query.message.chat_id}')
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


# ----------------------------------------------------------------------------------------------------------


def personalization_service_lu(update, context):
    query = update.callback_query
    if 'personalization_service_lu_' in query.data:
        period_for_upgrade = context.user_data['period_for_upgrade']
        traffic_for_upgrade = context.user_data['traffic_for_upgrade']
        sqlite_manager.update({'User': {'period': int(period_for_upgrade), 'traffic': int(traffic_for_upgrade)}},
                              where=f'where chat_id = {query.message.chat_id}')
        context.user_data['personalization_client_lu_id'] = int(query.data.replace('personalization_service_lu_', ''))

    id_ = context.user_data['personalization_client_lu_id']
    get_data_from_db = sqlite_manager.select(table='User', where=f'chat_id = {query.message.chat_id}')

    traffic = get_data_from_db[0][5]
    period = get_data_from_db[0][6]

    if 'traffic_low_10' in query.data or 'traffic_low_1' in query.data:
        traffic_t = int(query.data.replace('traffic_low_', ''))
        traffic = traffic - traffic_t
        traffic = traffic if traffic >= 0 else 0
    elif 'traffic_high_1' in query.data or 'traffic_high_10' in query.data:
        traffic_t = int(query.data.replace('traffic_high_', ''))
        traffic = traffic + traffic_t
        traffic = traffic if traffic <= 500 else 500
    elif 'period_low_10' in query.data or 'period_low_1' in query.data:
        period_t = int(query.data.replace('period_low_', ''))
        period = period - period_t
        period = period if period >= 1 else 1
    elif 'period_high_1' in query.data or 'period_high_10' in query.data:
        period_t = int(query.data.replace('period_high_', ''))
        period = period + period_t
        period = period if period <= 500 else 500


    sqlite_manager.update({'User': {'traffic':traffic, 'period': period}},where=f'where chat_id = {query.message.chat_id}')
    price = (traffic * private.PRICE_PER_GB) + (period * private.PRICE_PER_DAY)

    text = ('*• تو این بخش میتونید سرویس مورد نظر خودتون رو تمدید کنید و یا ارتقا دهید:*'
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
        [InlineKeyboardButton("✓ تایید", callback_data=f"payment_by_card_lu_{id_}")],
        [InlineKeyboardButton("برگشت ↰", callback_data="my_service")]
    ]
    query.edit_message_text(text=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))


def pay_page_get_evidence_per(update, context):
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
        something_went_wrong(update, context)


def send_evidence_to_admin_per(update, context):
    package = context.user_data['package']
    purchased_id = context.user_data['purchased_id']
    text = "- Check the new payment to the card:\n-FOR UPDATE SERVICE\n\n"
    price = (package[0][5] * private.PRICE_PER_GB) + (package[0][6] * private.PRICE_PER_DAY)
    keyboard = [[InlineKeyboardButton("Accept ✅", callback_data=f"accept_card_pay_lu_{purchased_id}")]
        , [InlineKeyboardButton("Refuse ❌", callback_data=f"refuse_card_pay_lu_{purchased_id}")]]
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        text += f"caption: {update.message.caption}" or 'Witout caption!'
        text += f"\n\nPeriod: {package[0][6]} Day\n Traffic: {package[0][5]}GB\nPrice: {price:,} T"
        context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=file_id, caption=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        update.message.reply_text(f'*سفارش شما با موفقیت ثبت شد✅\nنتیجه از طریق همین ربات بهتون اعلام میشه*', parse_mode='markdown')
    elif update.message.text:
        text += f"Text: {update.message.text}"
        text += f"\n\nPeriod: {package[0][6]} Day\n Traffic: {package[0][5]}GB\nPrice: {price:,} T"
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        update.message.reply_text(f'*درخواست شما با موفقیت ثبت شد✅\nنتیجه از طریق همین ربات بهتون اعلام میشه*', parse_mode='markdown')
    else:
        update.message.reply_text('مشکلی وجود داره!')

    context.user_data.clear()
    return ConversationHandler.END


get_service_con_per = ConversationHandler(
    entry_points=[CallbackQueryHandler(pay_page_get_evidence_per, pattern=r'payment_by_card_lu_\d+')],
    states={
        GET_EVIDENCE_PER: [MessageHandler(Filters.all, send_evidence_to_admin_per)]
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
            data = {
                "id": int(get_client[0][7]),
                "settings": "{{\"clients\":[{{\"id\":\"{0}\",\"alterId\":0,"
                            "\"email\":\"{1}\",\"limitIp\":0,\"totalGB\":{2},\"expiryTime\":{3},"
                            "\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}}]}}".format(get_client[0][10], get_client[0][9],
                                                                                       traffic, my_data)}
            # breakpoint()
            print(api_operation.update_client(get_client[0][10], data))
            sqlite_manager.update({'Purchased': {'date': datetime.now(pytz.timezone('Asia/Tehran'))}}
                                  ,where=f'where client_email = "{get_client[0][9]}"')
            context.bot.send_message(text='سفارش شما برای تمدید و یا ارتقا با موفقیت تایید شد ✅', chat_id=get_client[0][4])
            query.answer('Done ✅')
            query.delete_message()
        elif 'ok_card_pay_lu_refuse_' in query.data:
            id_ = int(query.data.replace('ok_card_pay_lu_refuse_', ''))
            get_client = sqlite_manager.select(table='Purchased', where=f'id = {id_}')
            context.bot.send_message(text=f'متاسفانه درخواست شما برای تمدید یا ارتقا سرویس پذیرفته نشد❌\n ارتباط با پشتیبانی: \n @Fupport ', chat_id=get_client[0][4])
            query.answer('Done ✅')
            query.delete_message()

        elif 'cancel_pay' in query.data:
            query.answer('Done ✅')
            query.delete_message()
    except Exception as e:
        print('errot:', e)


def get_free_service(update, context):
    user = update.callback_query.from_user
    uuid_ = random.randint(1, 100000)
    sqlite_manager.update({'User': {'free_service': 1}}, where=f"where chat_id = {user['id']}")
    ex = sqlite_manager.insert('Purchased', rows=[
        {'active': 1, 'status': 1, 'name': user["first_name"], 'user_name': user["username"],
         'chat_id': int(user["id"]), 'factor_id': uuid_, 'product_id': 1, 'inbound_id': 1,
         'client_email': f'Test Service | FreeByte | {uuid_}', 'client_id':uuid_, 'date': datetime.now()}])
    send_clean_for_customer(update.callback_query, context, ex)


def help_sec(update, context):
    query = update.callback_query
    text = "*برای کدوم دیوایس یا سیستم عامل راهنمایی لازم دارید؟*"
    keyboard = [
        [InlineKeyboardButton("اندروید", callback_data=f"android_help"),
         InlineKeyboardButton("ویندوز", callback_data=f"windows_help")],
        [InlineKeyboardButton("آیفون و مک‌", callback_data=f"mac_help"),
         InlineKeyboardButton("لینوکس", callback_data=f"linux_help")],
        [InlineKeyboardButton("در مورد v2ray بیشتر بدانید", callback_data=f"v2ray_help")],
        [InlineKeyboardButton("صفحه اصلی ⤶", callback_data="main_menu")]
    ]
    query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='markdown')


def show_help(update, context):
    query = update.callback_query
    help_what = query.data.replace('_help', '')
    if help_what == 'android':
        text = ("*برای اندروید میتونید از نرم‌افزار v2rayNG استفاده کنید.*"
                "\n\nراهنما اتصال:"
                "\n• بعد از دانلود و نصب وارد برنامه بشید و روی گزینه + کلیک کنید"
                "\n• از لیست تاشو انتخاب کنید چطور کانفیگ رو وارد میکنید"
                "\n• اگر لینک کانفیگ رو کپی کردید، با انتخاب گزینه from clipboard "
                "کانفیگ رو وارد برنامه کنید و با دکمه پایین، اتصال رو برقرار کنید")
        keyboard = [
            [InlineKeyboardButton("دانلود از پلی استور", url="https://play.google.com/store/apps/details?id=com.v2ray.ang&pcampaignid=web_share")],
            [InlineKeyboardButton("دانلود از صفحه رسمی", url="https://github.com/2dust/v2rayNG/releases/")],
            [InlineKeyboardButton("برگشت ⤶", callback_data="guidance")]
        ]
    elif help_what == 'mac':
        text = "*برای آیفون و مک میتونید از نرم‌افزار V2Box استفاده کنید.*"
        keyboard = [
            [InlineKeyboardButton("دانلود از apple.com", url="https://apps.apple.com/us/app/v2box-v2ray-client/id6446814690?platform=mac")],
            [InlineKeyboardButton("برگشت ⤶", callback_data="guidance")]
        ]
    elif help_what == 'windows':
        text = ("*برای ویندوز میتونید از نرم‌افزار v2rayN یا nekoray استفاده کنید.*"
                "\n\n• برای اتصال کافیه نرم افزار رو باز کنید و کانفیگ کپی شده رو paste کنید."
                "\n\n*حتما نسخه core نرم افزار 2rayN رو دانلود کنید.*")
        keyboard = [
            [InlineKeyboardButton("دانلود v2rayN", url="https://github.com/2dust/v2rayN/releases")],
            [InlineKeyboardButton("دانلود nekoray", url="https://github.com/Matsuridayo/nekoray/releases")],
            [InlineKeyboardButton("برگشت ⤶", callback_data="guidance")]
        ]
    elif help_what == 'linux':
        text = "*برای اتصال و پروکسی کردن سیستم لینوکس، میتونید آموزش لینک شده رو بخونید*"
        keyboard = [
            [InlineKeyboardButton("نحوه پروکسی کردن اوبونتو، سایت linuxbabe", url="https://www.linuxbabe.com/ubuntu/set-up-v2ray-proxy-server")],
            [InlineKeyboardButton("برگشت ⤶", callback_data="guidance")]
        ]

    elif help_what == 'v2ray':
        text = 'چیزی اضافه نشده'
        keyboard = [[InlineKeyboardButton("برگشت ⤶", callback_data="guidance")]]

    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='markdown')

def support(update, context):
    query = update.callback_query
    keyboard = [[InlineKeyboardButton("پرایوت", url="https://t.me/fupport")],
                [InlineKeyboardButton("برگشت ⤶", callback_data="main_menu")]]
    query.edit_message_text('از طریق روش های زیر میتوانید با پشتیبان صحبت کنید', reply_markup=InlineKeyboardMarkup(keyboard))