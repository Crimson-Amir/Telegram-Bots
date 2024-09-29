import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database_sqlalchemy import SessionLocal
import private
from dialogue_texts import text_transaction, keyboard_transaction
from private import default_language, telegram_bot_url, ADMIN_CHAT_IDs
import crud, functools, requests
from telegram.ext import ConversationHandler

class UserNotFound(Exception):
    def __init__(self): super().__init__("user was't register in bot!")


class FindText:
    def __init__(self, update, context, user_id=None, notify_user=True):
        self._update = update
        self._context = context
        self._notify_user = notify_user
        self._user_id = user_id

    @staticmethod
    async def handle_error_message(update, context, message_text=None):
        user_id = update.effective_chat.id
        if update.callback_query:
            await update.callback_query.answer(message_text)
            return
        await context.bot.send_message(text=message_text, chat_id=user_id)

    @staticmethod
    async def language_transaction(text_key, language_code=default_language, section="text") -> str:
        transaction = text_transaction
        if section == "keyboard": transaction = keyboard_transaction
        return transaction.get(text_key, transaction.get('error_message')).get(language_code, 'language not found!')

    @staticmethod
    async def get_language_from_database(user_id):
        with SessionLocal() as session:
            language = crud.get_user(session, user_id)
        if language:
            return language.language

    async def find_user_language(self):
        user_id = self._update.effective_chat.id
        user_language = self._context.user_data.get('user_language')
        if not user_language:
            get_user_language_from_db = await self.get_language_from_database(user_id)
            if not get_user_language_from_db:
                if self._notify_user:
                    await self.handle_error_message(self._update, self._context, message_text="Your info was't found, please register with /start command!")
                raise UserNotFound()
            user_language = get_user_language_from_db
            self._context.user_data['user_language'] = user_language
        return user_language

    async def find_text(self, text_key):
        return await self.language_transaction(text_key, await self.find_user_language())

    async def find_keyboard(self, text_key):
        return await self.language_transaction(text_key, await self.find_user_language(), section='keyboard')

    async def find_from_database(self, user_id, text_key, section='text'):
        user_language = await self.get_language_from_database(user_id)
        return await self.language_transaction(text_key, user_language, section=section)

class HandleErrors:
    err_msg = "🔴 An error occurred in {}:\n{}\nerror type: {}\nuser chat id: {}"
    def handle_functions_error(self, func):
        @functools.wraps(func)
        async def wrapper(update, context, **kwargs):
            user_detail = update.effective_chat
            try:
                return await func(update, context, **kwargs)
            except Exception as e:
                if 'Message is not modified' in str(e): return await update.callback_query.answer()
                err = self.err_msg.format(func.__name__, str(e), type(e), user_detail.id)
                await self.report_to_admin(err)
                await self.handle_error_message(update, context)
        return wrapper

    @staticmethod
    async def report_to_admin(msg, message_thread_id=private.error_thread_id):
        requests.post(url=telegram_bot_url, json={'chat_id': ADMIN_CHAT_IDs[0], 'text': msg, 'message_thread_id': message_thread_id})

    @staticmethod
    async def handle_error_message(update, context, message_text=None):
        user_id = update.effective_chat.id
        ft_instance = FindText(update, context)
        message_text = message_text if message_text else await ft_instance.find_text('error_message')
        if update.callback_query:
            return await update.callback_query.answer(message_text)
        await context.bot.send_message(text=message_text, chat_id=user_id)

async def report_to_admin(level, fun_name, msg, user_table=None):
    report_level = {
        'purchase': {'thread_id': private.purchased_thread_id, 'emoji': '🟢'},
        'info': {'thread_id': private.info_thread_id, 'emoji': '🔵'},
        'warning': {'thread_id': private.info_thread_id, 'emoji': '🟡'},
        'error': {'thread_id': private.error_thread_id, 'emoji': '🔴'},
        'emergecy_error': {'thread_id': private.error_thread_id, 'emoji': '🔴🔴'},
    }
    emoji = report_level.get(level, {}).get('emoji', '🔵')
    thread_id = report_level.get(level, {}).get('thread_id', private.info_thread_id)
    message = f"{emoji} Report {level.replace('_', ' ')} {fun_name}\n\n{msg}"

    if user_table:
        message += (
            "\n\n👤 User Info:"
            f"\nUser name: {user_table.first_name} {user_table.last_name}"
            f"\nUser ID: {user_table.chat_id}"
            f"\nUsername: @{user_table.username}"
        )

    await HandleErrors.report_to_admin(message, thread_id)


async def report_to_user(level, user_id, msg):
    report_level = {
        'success': '🟢',
        'info': '🔵',
        'warning': '🟡',
        'error': '🔴',
    }
    emoji = report_level.get(level, '🔵')
    message = emoji + msg

    requests.post(url=telegram_bot_url, json={'chat_id': user_id, 'text': message})


class MessageToken:
    message_timer = {}

    @classmethod
    def set_message_time(cls, message_id):
        cls.message_timer[message_id] = datetime.datetime.now()

    @classmethod
    def message_expierd(cls, message_id):
        if (cls.message_timer[message_id] + datetime.timedelta(hours=1)) < datetime.datetime.now():
            return True
        return False

    @classmethod
    def check_token(cls, func):
        @functools.wraps(func)
        async def wrapper(update, context, **kwargs):

            if update.message:
                message_id = update.message.message_id
            elif update.callback_query and update.callback_query.message:
                message_id = update.callback_query.message.message_id
            else:
                return await func(update, context, **kwargs)

            query = update.callback_query
            timer_exist_in_message_timer = cls.message_timer.get(message_id)

            if timer_exist_in_message_timer:
                if cls.message_expierd(message_id):
                    ft_instance = FindText(update, context, notify_user=False)
                    text = await ft_instance.find_text('start_menu')
                    main_keyboard = [
                        [InlineKeyboardButton(await ft_instance.find_keyboard('menu_services'), callback_data='menu_services')],
                        [InlineKeyboardButton(await ft_instance.find_keyboard('wallet'), callback_data='wallet_page'),
                         InlineKeyboardButton(await ft_instance.find_keyboard('ranking'), callback_data='ranking')],
                        [InlineKeyboardButton(await ft_instance.find_keyboard('setting'), callback_data='setting'),
                         InlineKeyboardButton(await ft_instance.find_keyboard('invite'), callback_data='invite')],
                        [InlineKeyboardButton(await ft_instance.find_keyboard('help_button'), callback_data='help_button')],
                    ]
                    new_message = await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=InlineKeyboardMarkup(main_keyboard), parse_mode='html')
                    await query.answer(await ft_instance.find_keyboard('message_expierd_send_new_message'))

                    del cls.message_timer[message_id]
                    cls.set_message_time(new_message.message_id)
                else:
                    cls.set_message_time(message_id)
                    return await func(update, context, **kwargs)
            else:
                cls.set_message_time(message_id)
                return await func(update, context, **kwargs)

        return wrapper

class FakeContext:
    user_data = {}

    class bot:
        @staticmethod
        async def send_message(chat_id, text):
            url = f"https://api.telegram.org/bot{private.telegram_bot_token}/sendMessage"
            json_data = {'chat_id': chat_id, 'text': text}
            requests.post(url=url, json=json_data)
        @staticmethod
        async def send_photo(chat_id, text, caption, reply_markup, parse_mode):
            url = f"https://api.telegram.org/bot{private.telegram_bot_token}/SendPhoto"
            json_data = {'chat_id': chat_id, 'text': text, 'caption': caption, 'reply_markup':reply_markup, 'parse_mode': parse_mode}
            requests.post(url=url, json=json_data)

handle_error = HandleErrors()
message_token = MessageToken()