import random
import uuid
from datetime import datetime, timedelta
import telegram.error
import private
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters

import ranking
import utilities
from admin_task import add_client_bot, api_operation, second_to_ms, message_to_user, wallet_manage, sqlite_manager
import qrcode
from io import BytesIO
import pytz

# dont delete that:
import os

from utilities import (human_readable,something_went_wrong,
                       ready_report_problem_to_admin,format_traffic,record_operation_in_file,
                       send_service_to_customer_report)
import re
from private import ADMIN_CHAT_ID

GET_EVIDENCE = 0
GET_EVIDENCE_PER = 0
GET_EVIDENCE_CREDIT = 0
GET_TICKET = 0


PAY_PER_USE_INBOUND_ID = 4
PAY_PER_USE_DOMAIN = 'human.ggkala.shop'
LOW_WALLET_CREDIT = 1_000

def buy_service(update, context):
    query = update.callback_query
    try:
        sqlite_manager.delete({'Purchased': ['active', 0]})
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
        plans = sqlite_manager.select(table='Product', where=f'active = 1 and country = "{query.data}"')
        country_flag = plans[0][3][:2]
        text = f"<b>• {country_flag} سرویس مناسب خودتون رو انتخاب کنید:\n\n• با انتخاب گزینه دلخواه میتونید یک سرویس شخصی سازی شده بسازید.</b>"
        text += "\n\n<b>• سرویس ساعتی به شما اجازه میده به اندازه مصرف در هر ساعت پرداخت کنید.</b>"
        country_unic = {name[4] for name in plans}
        for country in country_unic:
            if query.data == country:
                service_list = [service for service in plans if service[4] == country]
                keyboard = [[InlineKeyboardButton(f"سرویس {pattern[5]} روزه - {pattern[6]} گیگابایت - {pattern[7]:,} تومان",
                                                  callback_data=f"service_{pattern[0]}")] for pattern in service_list]

                keyboard.append([InlineKeyboardButton("✪ سرویس دلخواه", callback_data=f"personalization_service_{plans[0][0]}"),
                                 InlineKeyboardButton("✪ سرویس ساعتی", callback_data=f"pay_per_use_{plans[0][0]}")])
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
                    [InlineKeyboardButton("برگشت ↰", callback_data="main_menu")]
                ]

        text = (f"<b>❋ بسته انتخابی شامل مشخصات زیر میباشد:</b>\n"
                f"\nسرور: {package[0][3]}"
                f"\nدوره زمانی: {package[0][5]} روز"
                f"\nترافیک (حجم): {package[0][6]} گیگابایت"
                f"\nحداکثر کاربر مجاز: ♾️"
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
                "گزارش به ادمین ها ارسال شد، نتیجه بهتون اعلام میشه")
        keyboard = [[InlineKeyboardButton("برگشت ↰", callback_data="main_menu")]]
        update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END


def cancel(update, context):
    query = update.callback_query
    query.answer(text="با موفقیت کنسل شد!", show_alert=False)
    query.delete_message()
    return ConversationHandler.END


get_service_con = ConversationHandler(
    entry_points=[CallbackQueryHandler(get_card_pay_evidence, pattern=r'payment_by_card_\d+')],
    states={
        GET_EVIDENCE: [MessageHandler(Filters.all, send_evidence_to_admin)]
    },
    fallbacks=[CallbackQueryHandler(cancel, pattern='cancel')],
    conversation_timeout=800,
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
            query.delete_message()

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
        get_server_country = sqlite_manager.select(column='name,server_domain', table='Product', where=f'id = {get_data[0][6]}')
        get_server_domain = get_server_country[0][1]
        get_server_country = get_server_country[0][0].replace('سرور ','').replace('pay_per_use_', '')

        ret_conf = api_operation.get_client(email, get_server_domain)

        upload_gb = round(int(ret_conf['obj']['up']) / (1024 ** 3), 2)
        download_gb = round(int(ret_conf['obj']['down']) / (1024 ** 3), 2)
        usage_traffic = round(upload_gb + download_gb, 2)

        change_active = 'فعال ✅' if ret_conf['obj']['enable'] else 'غیرفعال ❌'
        purchase_date = datetime.strptime(get_data[0][12], "%Y-%m-%d %H:%M:%S.%f%z").replace(tzinfo=None)


        if int(ret_conf['obj']['total']) != 0 and int(ret_conf['obj']['expiryTime']) != 0:
            total_traffic = int(round(ret_conf['obj']['total'] / (1024 ** 3), 2))

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
            keyboard = [[InlineKeyboardButton("تمدید و ارتقا ↟", callback_data=f"personalization_service_lu_{get_data[0][0]}")]]

        else:
            total_traffic = '♾️'
            expiry_month = '♾️'
            exist_day = '(بدون محدودیت زمانی)'
            service_activate_status = 'غیرفعال سازی ⤈' if ret_conf['obj']['enable'] else 'فعال سازی ↟'
            keyboard = [[InlineKeyboardButton(service_activate_status, callback_data=f"change_infiniti_service_status_{get_data[0][0]}_{ret_conf['obj']['enable']}")]]

        keyboard.append([InlineKeyboardButton("حذف سرویس ⇣", callback_data=f"remove_service_{email}"),
                      InlineKeyboardButton("تازه سازی ↻", callback_data=f"view_service_{email}")])

        keyboard.append([InlineKeyboardButton("گزینه های پیشرفته ⥣", callback_data=f"not_ready_yet")])  # advanced_option_{email}
        keyboard.append([InlineKeyboardButton("برگشت ↰", callback_data="my_service")])

        text_ = (
            f"<b>اطلاعات سرویس انتخاب شده:</b>"
            f"\n\n🔷 نام سرویس: {email}"
            f"\n💡 وضعیت: {change_active}"
            f"\n🗺 موقعیت سرور: {get_server_country}"
            f"\n📅 تاریخ انقضا: {expiry_month} {exist_day}"
            f"\n🔼 آپلود↑: {format_traffic(upload_gb)}"
            f"\n🔽 دانلود↓: {format_traffic(download_gb)}"
            f"\n📊 مصرف کل: {usage_traffic}/{total_traffic}{'GB' if isinstance(total_traffic, int) else ''}"
            f"\n\n⏰ تاریخ خرید/تمدید: {purchase_date.strftime('%H:%M:%S | %Y/%m/%d')}"
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
        utilities.report_status_to_admin(context, text=f'Service With Email {get_data[0][9]} Has Be Changed Activity By User To {status}', chat_id=get_data[0][4])

        query.answer(f'سرویس با موفقیت {status} شد')
        keyboard = [
            [InlineKeyboardButton("برگشت ↰", callback_data=f"view_service_{get_data[0][9]}")]]

        query.edit_message_text(f'سرویس با موفقیت {status} شد✅', reply_markup=keyboard)

    else:
        get_credit = sqlite_manager.select(column='wallet', table='User', where=f'chat_id = {get_data[0][4]}')[0][0]

        if get_credit >= private.PRICE_PER_DAY:
            text = f'آیا از {status} کردن این سرویس مطمئن هستید؟'
            keyboard = [
                [InlineKeyboardButton(f"بله، {status} کن", callback_data=f"{query.data}_accept")],
                [InlineKeyboardButton("برگشت ↰", callback_data=f"view_service_{get_data[0][9]}")]]
        else:
            text = (f'برای فعال کردن این سرویس، کیف پول خودتون رو شارژ کنید.'
                    f'\n\nاعتبار شما: {get_credit:,}'
                    f'\nحداقل اعتبار برای فعال کردن سرویس: {private.PRICE_PER_DAY:,}')
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

    if 'personalization_service_' in query.data:
        context.user_data['personalization_service_id'] = int(query.data.replace('personalization_service_', ''))

    get_data_from_db = sqlite_manager.select(table='User', where=f'chat_id = {query.message.chat_id}')

    try:
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

            inbound_id = sqlite_manager.select(column='inbound_id,name,country,server_domain,domain,country', table='Product', where=f'id = {id_}')

            check_available = sqlite_manager.select(table='Product', where=f'is_personalization = {query.message.chat_id} and country = "{inbound_id[0][5]}"')

            get_data = {'inbound_id': inbound_id[0][0], 'active': 0,
                        'name': inbound_id[0][1], 'country': inbound_id[0][2],
                        'period': period, 'traffic': traffic,
                        'price': price, 'date': datetime.now(pytz.timezone('Asia/Tehran')),
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
    except Exception as e:
        utilities.ready_report_problem_to_admin(context, text='personalization_service', chat_id=query.message.chat_id, error=e)
        query.answer('مشکلی وجود دارد')


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
             InlineKeyboardButton("کارت به کارت", callback_data=f'payment_by_card_lu_{id_}')],
            [InlineKeyboardButton("برگشت ↰", callback_data="select_server")]
        ]
        price = (package[0][5] * private.PRICE_PER_GB) + (package[0][6] * private.PRICE_PER_DAY)
        text = (f"<b>❋ بسته انتخابی شامل مشخصات زیر میباشد:</b>\n"
                f"\nدوره زمانی: {package[0][6]} روز"
                f"\nترافیک (حجم): {package[0][5]} گیگابایت"
                f"\nحداکثر کاربر مجاز: ♾️"
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
    conversation_timeout=800,
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

            get_server_domain = sqlite_manager.select(column='server_domain', table='Product',
                                                      where=f'id = {get_client[0][6]}')

            user_db = sqlite_manager.select(table='User', where=f'chat_id = {get_client[0][4]}')

            price = (user_db[0][5] * private.PRICE_PER_GB) + (user_db[0][6] * private.PRICE_PER_DAY)

            ret_conf = api_operation.get_client(get_client[0][9], get_server_domain[0][0])
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
                print(api_operation.reset_client_traffic(get_client[0][7], get_client[0][9], get_server_domain[0][0]))
            data = {
                "id": int(get_client[0][7]),
                "settings": "{{\"clients\":[{{\"id\":\"{0}\",\"alterId\":0,"
                            "\"email\":\"{1}\",\"limitIp\":0,\"totalGB\":{2},\"expiryTime\":{3},"
                            "\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}}]}}".format(get_client[0][10], get_client[0][9],
                                                                                       traffic, my_data)}
            # breakpoint()
            print(api_operation.update_client(get_client[0][10], data, get_server_domain[0][0]))
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

            keyboard = [[InlineKeyboardButton("پشتیبانی", url="@Fupport")]]

            context.bot.send_message(text='درخواست شما برای سفارش یا ارتقا سرویس تایید نشد!\nاگر فکر میکنید خطایی رخ داده با پشتیبانی در ارتباط باشید:', chat_id=get_client[0][4], reply_markup=InlineKeyboardMarkup(keyboard))
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


def guidance(update, context):
    query = update.callback_query
    text = "<b>📚 به بخش راهنمای ربات خوش آمدید!</b>"
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

    elif help_what == 'people_ask':
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

    for server in get_all:
        for config in server['obj']:
            for client in config['clientStats']:
                #  check ExpiryTime
                for user in get_from_db:
                    if user[2] == client['email']:
                        list_of_notification = [notif for notif in get_users_notif if notif[0] == user[1]]
                        if not client['enable'] and user[3] and client['total']:
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
        [InlineKeyboardButton("نوتیفیکیشن سرویس", callback_data="service_notification"),
         InlineKeyboardButton("نوتیفیکیشن کیف‌پول", callback_data="wallet_notification")],
        [InlineKeyboardButton("• تراکنش های مالی", callback_data="financial_transactions")],
        [InlineKeyboardButton("برگشت ↰", callback_data="main_menu")]
    ]
    query.edit_message_text(text='*در این قسمت میتونید تنظیمات ربات رو مشاهده و یا شخصی سازی کنید:*', parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))


def change_notif(update, context):
    query = update.callback_query
    get_data_from_db = sqlite_manager.select(table='User', where=f'chat_id = {query.message.chat_id}')

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
    conversation_timeout=800,
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

                get_server_domain = sqlite_manager.select(column='server_domain', table='Product',
                                                          where=f'id = {get_client[0][6]}')

                user_db = sqlite_manager.select(table='User', where=f'chat_id = {get_client[0][4]}')

                price = (user_db[0][5] * private.PRICE_PER_GB) + (user_db[0][6] * private.PRICE_PER_DAY)

                ret_conf = api_operation.get_client(get_client[0][9], get_server_domain[0][0])
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
                    print(api_operation.reset_client_traffic(get_client[0][7], get_client[0][9], get_server_domain[0][0]))
                data = {
                    "id": int(get_client[0][7]),
                    "settings": "{{\"clients\":[{{\"id\":\"{0}\",\"alterId\":0,"
                                "\"email\":\"{1}\",\"limitIp\":0,\"totalGB\":{2},\"expiryTime\":{3},"
                                "\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}}]}}".format(get_client[0][10], get_client[0][9],
                                                                                           traffic, my_data)}
                # breakpoint()
                print(api_operation.update_client(get_client[0][10], data, get_server_domain[0][0]))

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
                        if get_wallet[0][0] >= package[0][7] else [InlineKeyboardButton("افزایش موجودی ↟", callback_data=f"buy_credit_volume")],
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
        query.answer('شکلی وجود داشت، گزارش به ادمین ها ارسال شد.')
        ready_report_problem_to_admin(context, 'PAY FROM WAWLLET', query.from_user['id'], e)
        something_went_wrong(update, context)


def remove_service(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id

    email = query.data.replace('remove_service_', '')
    email = email.replace('accept_rm_ser_', '')

    print(email)

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
            price = int((left_traffic * private.PRICE_PER_GB) + (days_lefts * private.PRICE_PER_DAY))

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


def pay_per_use(update, context):
    query = update.callback_query

    try:
        if 'pay_per_use_' in query.data:

            sqlite_manager.delete({'Product': ['status', 0]})

            get_product_id = int(query.data.replace('pay_per_use_', ''))
            product_db  = sqlite_manager.select(table='Product', where=f'id = {get_product_id}')
            country = product_db[0][4]
            server_domain = product_db[0][11]

            user_credit = wallet_manage.get_wallet_credit(query.message.chat_id)

            chrge_for_next_24_hours = private.PRICE_PER_DAY

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
                    f"\n\nهزینه روزانه سرویس: {private.PRICE_PER_DAY:,} تومان"
                    f"\nهزینه هر گیگابایت: {private.PRICE_PER_GB:,} تومان"
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

    get_from_db = sqlite_manager.select(column='id,chat_id,client_email,status,date,notif_day,notif_gb,inbound_id,client_id',
                                        table='Purchased', where=f"inbound_id = {PAY_PER_USE_INBOUND_ID}")

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

                            if client['enable']:

                                upload_gb = client['up'] / (1024 ** 3)
                                download_gb = client['down'] / (1024 ** 3)
                                usage_traffic = upload_gb + download_gb

                                time_price = private.PRICE_PER_DAY / 24
                                traffic_use =  (usage_traffic - last_traffic_usage[0][2]) * private.PRICE_PER_GB
                                cost = int(time_price + traffic_use)

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

        utilities.report_problem_by_user(context, problem.replace('_', ' '), query.from_user)

    query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


def say_to_user_send_ticket(update, context):
    query = update.callback_query
    query.answer('پیام خودتون رو بفرستید')
    problem = query.data.replace('ticket_send_', '')
    try:
        context.user_data['problem'] = problem
        text = 'پیام خودتو رو بفرستید:\nهمچنین میتونید عکس مورد نظر خودتون رو با توضیحات در کپشن بفرستید:'
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
    conversation_timeout=800,
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

        next_rank = utilities.find_next_rank(rank[0][5], rank[0][4])

        text = (f"<b>• با افزایش رتبه، به ویژگی های بیشتری از ربات و همچنین تخفیف بالاتری دسترسی پیدا میکنید!</b>"
                f"\n\n<b>❋ رتبه شما: {utilities.get_rank_and_emoji(rank[0][5])}</b>"
                f"\n❋ امتیاز: {rank[0][4]:,}"
                f"<b>\n\n• دسترسی های رتبه شما:</b>\n\n"
                f"- {'\n- '.join(utilities.get_access_fa(rank[0][5]))}"
                f"\n\n• <b>رتبه بعدی: {next_rank[0]}</b>"
                f"\n<b>• امتیاز مورد نیاز: {next_rank[1]:,}</b>"
                )
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
        get_data = sqlite_manager.select(table='Purchased', where=f'client_email = "{email}"')
        get_server_country = sqlite_manager.select(column='name,server_domain', table='Product',
                                                   where=f'id = {get_data[0][6]}')

        get_server_domain = get_server_country[0][1]
        get_server_country = get_server_country[0][0].replace('سرور ', '').replace('pay_per_use_', '')
        get_country_flag = get_server_country[:2]
        auto_renewal, auto_renewal_button, chenge_to = ('فعال ✓', 'غیرفعال کردن تمدید خودکار', False) if get_data[0][15] \
            else ('غیرفعال ✗', 'فعال کردن تمدید خودکار', True)

        text_ = (
            f"<b>اطلاعات سرویس انتخاب شده:</b>"
            f"\n\n🔷 نام سرویس: {email}"
            f"\n🗺 موقعیت سرور: {get_server_country}"
            f"\n🔁 تمدید خودکار: {auto_renewal}"
            f"\n\n🌐 آدرس سرویس:\n <code>{get_data[0][8]}</code>"
        )

        keyboard = [[InlineKeyboardButton(f"{auto_renewal_button}", callback_data=f"change_auto_renewal_status_{email}_{chenge_to}")],
                    [InlineKeyboardButton(f"تغییر کشور ({get_country_flag})", callback_data=f"change_country_server_{email}")],
                    [InlineKeyboardButton("برگشت ↰", callback_data="my_service")]]

        query.edit_message_text(text_, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')

    except Exception as e:
        print(e)

def change_server(update, context):
    pass