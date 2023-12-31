import random

import telegram.error

from sqlite_manager import ManageDb
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
import uuid
from private import ADMIN_CHAT_ID
from admin_task import add_client_bot, api_operation
import qrcode
from io import BytesIO


sqlite_manager = ManageDb('v2ray')
GET_EVIDENCE = 0


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
        server_name_unic = {name[3] for name in plans}
        country_unic = {name[4] for name in plans}
        keyboard = [[InlineKeyboardButton(ser, callback_data=cont)] for ser, cont in zip(list(server_name_unic), list(country_unic))]
        keyboard.append([InlineKeyboardButton("برگشت ↰", callback_data="main_menu")])
        query.edit_message_text(text="<b>سرور مورد نظر خودتون رو انتخاب کنید:</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')
    except Exception as e:
        print(e)
        something_went_wrong(update, context)


def all_query_handler(update, context):
    try:
        text = "<b>سرویس مناسب خودتون رو انتخاب کنید:\n\n✪ با انتخاب گزینه 'دلخواه' میتونید یک سرویس شخصی سازی شده بسازید!</b>"
        query = update.callback_query
        plans = sqlite_manager.select(table='Product', where='active = 1')
        country_unic = {name[4] for name in plans}
        for country in country_unic:
            if query.data == country:
                service_list = [service for service in plans if service[4] == country]
                keyboard = [[InlineKeyboardButton(f"سرویس {pattern[5]} روزه - {pattern[6]} گیگابایت - {pattern[7]:,} تومان",
                                                  callback_data=f"service_{pattern[0]}")] for pattern in service_list]

                keyboard.append([InlineKeyboardButton("سرویس دلخواه ४", callback_data="personalization_service")])
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
        keyboard = [
            [InlineKeyboardButton("کارت به کارت", callback_data=f'payment_by_card_{id_}')],
            [InlineKeyboardButton("پرداخت از طریق کیف پول", callback_data=f'payment_by_wallet_{id_}')],
            [InlineKeyboardButton("پرداخت از طریق کریپتو", callback_data=f'payment_by_crypto_{id_}')],
            [InlineKeyboardButton("برگشت ↰", callback_data="select_server")]
        ]
        text = (f"<b>❋ بسته انتخابی شامل مشخصات زیر میباشد:</b>\n"
                f"\nسرور: {package[0][3]}"
                f"\nدوره زمانی: {package[0][5]} روز"
                f"\nترافیک (حجم): {package[0][6]} گیگابایت"
                f"\nحداکثر کاربر مجاز: ∞"
                f"\n<b>قیمت: {package[0][7]:,} تومان</b>"
                f"\n\n• دوره زمانی سرویس بعد از اولین اتصال شروع میشود."
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
                f"\n*قیمت*: `{package[0][7]}`* تومان *"
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
    purchased_id = context.user_data['purchased_id'][1]
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
    email = int(update.callback_query.data.replace('view_service_', ''))
    api_operation.get_client(email)



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
