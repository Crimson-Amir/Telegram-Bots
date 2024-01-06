from sqlite_manager import ManageDb
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
import uuid
from private import ADMIN_CHAT_ID

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
        text = "<b>سرویس مناسب خودتون رو انتخاب کنید:\n\n✪ با انتخاب گزینه 'دلخواه' میتوانید یک سرویس شخصی سازی شده بسازید!</b>"
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
                f"\nحداکثر کاربر متصل: ∞"
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
        keyboard = [[InlineKeyboardButton("بیخیال", callback_data="cancel")]
            ,[InlineKeyboardButton("صفحه اصلی ⤶", callback_data="send_main_message")]]
        sqlite_manager.insert('Purchased',rows= [{'active': 0,'name': user["first_name"],'user_name': user["username"],
                                                  'chat_id': int(user["id"]),'factor_id': uuid_,'product_id': id_}])
        text = (f"شماره سفارش:"
                f"\n`{uuid_}`"
                f"\n\nمدت اعتبار فاکتور: 10 دقیقه"
                f"\nسرویس: {package[0][5]} روز - {package[0][6]} گیگابایت"
                f"\n*قیمت*: `{package[0][7]}`* تومان *"
                f"\n\n*• لطفا مبلغ دقیق را به شماره‌حساب زیر واریز کنید و اسکرین‌شات یا شماره‌پیگیری را بعد همین پیام ارسال کنید.*"
                f"\n\n`6219861938619417` - امیرحسین نجفی"
                f"\n\n*• بعد از تایید شدن پرداخت، سرویس برای شما ارسال میشه، زمان تقریبی 5 دقیقه الی 3 ساعت.*")
        query.edit_message_text(text=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return GET_EVIDENCE
    except Exception as e:
        print(e)
        something_went_wrong(update, context)


def send_evidence_to_admin(update, context):
    package = context.user_data['package']
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        caption = update.message.caption or ''
        caption += f"\n\n{'-'*50}\nFrom `{package[0][4]}` server, Inbound id: `{package[0][1]}`\n{package[0][5]} day - {package[0][6]}GB - {package[0][7]:,} T"
        context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=file_id, caption=caption, parse_mode='markdown')
        update.message.reply_text(f'*درخواست شما با موفقیت ثبت شد✅\nنتیجه از طریق همین ربات بهتون اعلام میشه*', parse_mode='markdown')
    elif update.message.text:
        text = update.message.text
        text += f"\n\n{'-'*50}\nFrom `{package[0][4]}` server, Inbound id: `{package[0][1]}`\n{package[0][5]} day - {package[0][6]}GB - {package[0][7]:,} T"
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, parse_mode='markdown')
        update.message.reply_text(f'*درخواست شما با موفقیت ثبت شد✅\nنتیجه از طریق همین ربات بهتون اعلام میشه*', parse_mode='markdown')
    else:
        update.message.reply_text('مشکلی وجود داره!')

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