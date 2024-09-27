import crud, arrow, logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from database_sqlalchemy import SessionLocal
from utilities_reFactore import FindText

def human_readable(date, user_language):
    get_date = arrow.get(date)
    if user_language == 'en':
        return get_date.humanize()

    try:
        return get_date.humanize(locale="fa-ir")
    except ValueError as e:
        if 'week' in str(e):
            return str(get_date.humanize()).replace('weeks ago', 'هفته پیش').replace('a week ago', 'هفته پیش')
        else:
            return get_date.humanize()

    except Exception as e:
        logging.error(f'an error in humanize data: {e}')
        return f'Error In Parse Data'


class WalletManage:
    def __init__(self, wallet_table, wallet_column, db_name, user_id_identifier):
        super().__init__(db_name)
        self.database_name = db_name
        self.WALLET_TABALE = wallet_table
        self.WALLET_COLUMN = wallet_column
        self.USER_ID = user_id_identifier

    @staticmethod
    def add_financial_report(user_id, credit, operation, detail):
        crud.add_financial_report(user_id, credit, operation, detail)

    @staticmethod
    def add_to_wallet(user_id, credit, detail):
        crud.add_credit_to_wallet(user_id, credit, 'spend', detail)

    @staticmethod
    def less_from_wallet(user_id, credit, detail):
        crud.less_from_wallet(user_id, credit, 'recive', detail)

async def wallet_page(update, context):
    query = update.callback_query
    chat_id = update.effective_chat.id
    ft_instance = FindText(update, context)

    try:
        with SessionLocal() as session:
            get_user = crud.get_user(session, chat_id)

            if get_user.financial_reports:
                last_transaction = human_readable(f'{get_user.financial_reports[0].register_date}', await ft_instance.find_user_language())
                lasts_report = await ft_instance.find_text('recent_transactions')
                for count, report in enumerate(get_user.financial_reports):
                    lasts_report += f"\n{await ft_instance.find_text('recive_money') if report.operation == 'recive' else
                    await ft_instance.find_text('spend_money')} {report.value:,} {await ft_instance.find_text('irt')} - {human_readable(report.register_date, await ft_instance.find_user_language())}"
                    if count == 5: break
            else:
                last_transaction = await ft_instance.find_text('no_transaction_yet')
                lasts_report = ''

            keyboard = [
                [InlineKeyboardButton(await ft_instance.find_keyboard('refresh'), callback_data='wallet_page'),
                 InlineKeyboardButton(await ft_instance.find_keyboard('increase_balance'), callback_data='buy_credit_volume')],
                [InlineKeyboardButton(await ft_instance.find_keyboard('financial_transactions'), callback_data='financial_transactions_wallet')],
                [InlineKeyboardButton(await ft_instance.find_keyboard('back_button'), callback_data='start')]]

            text = (
                f"<b>{await ft_instance.find_text('wallet_page_title')}</b>"
                f"\n\n{await ft_instance.find_text('wallet_balance_key')} {get_user.wallet:,} {await ft_instance.find_text('irt')}"
                f"\n{await ft_instance.find_text('last_transaction')} {last_transaction}"
                f"\n\n{lasts_report}"
            )

            await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')

    except Exception as e:
        logging.error(f'error in wallet page: {e}')
        if "specified new message content and reply markup are exactly the same" in str(e):
            return await query.answer()
        return await query.answer(await ft_instance.find_text('error_message'))


async def financial_transactions_wallet(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    ft_instance = FindText(update, context)

    try:
        with SessionLocal() as session:
            get_user = crud.get_user(session, chat_id)

            if get_user.financial_reports:
                lasts_report = await ft_instance.find_text('recent_transactions') + '\n'
                for report in get_user.financial_reports:
                    lasts_report += f"\n\n{await ft_instance.find_text('recive_money') if report.operation == 'recive' else
                    await ft_instance.find_text('spend_money')} {report.value:,} {await ft_instance.find_text('irt')} - {human_readable(report.register_date, await ft_instance.find_user_language())}\n• {report.detail}"
            else:
                lasts_report = await ft_instance.find_text('no_transaction_yet')

            keyboard = [
                [InlineKeyboardButton(await ft_instance.find_keyboard('refresh'), callback_data='financial_transactions_wallet')],
                [InlineKeyboardButton(await ft_instance.find_keyboard('back_button'), callback_data='wallet_page')]]

            text_ = f"\n\n{lasts_report}"
            await query.edit_message_text(text=text_, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')

    except Exception as e:
        logging.error(f'error in wallet page: {e}')
        if "specified new message content and reply markup are exactly the same" in str(e):
            return await query.answer()
        return await query.answer(await ft_instance.find_text('error_message'))


async def buy_credit_volume(update, context):
    query = update.callback_query
    ft_instance = FindText(update, context)

    try:
        text = '• مشخص کنید چه مقدار اعتبار به کیف پولتون اضافه بشه:'

        keyboard = [
            [InlineKeyboardButton("250,000 تومن", callback_data="set_credit_250000"),
             InlineKeyboardButton("100,000 تومن", callback_data="set_credit_100000")],
            [InlineKeyboardButton("1,000,000 تومن", callback_data="set_credit_1000000"),
             InlineKeyboardButton("500,000 تومن", callback_data="set_credit_500000")],
            [InlineKeyboardButton("برگشت ↰", callback_data="wallet_page")]
        ]

        query.edit_message_text(text=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    except Exception as e:
        logging.error(f'error in buy credit volume: {e}')
        return await query.answer(await ft_instance.find_text('error_message'))


def pay_way_for_credit(update, context):
    query = update.callback_query
    id_ = int(query.data.replace('pay_way_for_credit_', ''))
    package = sqlite_manager.select(column='value', table='Credit_History', where=f'id = {id_}')

    keyboard = [
        [InlineKeyboardButton("درگاه پرداخت بانکی", callback_data=f"zarinpall_page_wallet_{id_}")],
        [InlineKeyboardButton("پرداخت با کریپتو", callback_data=f"cryptomus_page_wallet_{id_}")],
        [InlineKeyboardButton("برگشت ↰", callback_data="buy_credit_volume")],

    ]

    text = (f"<b>❋ مبلغ انتخاب شده رو برای اضافه کردن به کیف پول تایید میکنید؟:</b>\n"
            f"\n<b>مبلغ: {package[0][0]:,} تومان</b>"
            f"\n\n<b>⤶ برای پرداخت میتونید یکی از روش های زیر رو استفاده کنید:</b>")
    query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))
