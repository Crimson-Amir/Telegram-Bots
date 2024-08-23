from sqlite_manager import ManageDb
from datetime import datetime
import pytz, requests
from private import telegram_bot_token, ADMIN_CHAT_ID

def report_problem_to_admin_witout_context(text, chat_id, error, detail=None):
    text = ("🔴 Report Problem in Bot\n\n"
            f"Something Went Wrong In {text} Section."
            f"\nUser ID: {chat_id}"
            f"\nError Type: {type(error).__name__}"
            f"\nError Reason:\n{error}")
    text += f"\nDetail:\n {detail}" if detail else ''
    telegram_bot_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    requests.post(telegram_bot_url, data={'chat_id': ADMIN_CHAT_ID, 'text': text})
    print(f'* REPORT TO ADMIN SUCCESS: ERR: {error}')

class WalletManage(ManageDb):
    def __init__(self, wallet_table, wallet_column, db_name, user_id_identifier):
        super().__init__(db_name)
        self.database_name = db_name
        self.WALLET_TABALE = wallet_table
        self.WALLET_COLUMN = wallet_column
        self.USER_ID = user_id_identifier

    @staticmethod
    def try_except(method):
        def warpper(*args, **kwargs):
            try:
                return method(*args, **kwargs)
            except Exception as e:
                print(e)
                return e
        return warpper


    @try_except
    def get_wallet_credit(self, user_id):
        get_credit = self.select(column=self.WALLET_COLUMN, table=self.WALLET_TABALE,
                                 where=f'{self.USER_ID} = {user_id}')
        return int(get_credit[0][0])

    @try_except
    def get_all_wallet(self):
        get_credit = self.select(column=self.WALLET_COLUMN, table=self.WALLET_TABALE)
        return get_credit


    def clear_wallet_notif(self, chat_id):
        self.update({'User': {'notif_wallet': 0,'notif_low_wallet': 0}}, where=f'chat_id = {chat_id}')


    @try_except
    def add_to_wallet(self, user_id, credit, user_detail):
        try:
            credit_all = int(self.get_wallet_credit(user_id) + credit)
            get_credit = self.update(table={self.WALLET_TABALE: {self.WALLET_COLUMN: credit_all}},
                                     where=f'{self.USER_ID} = {user_id}')

            self.clear_wallet_notif(user_id)
            self.insert(table='Credit_History',
                        rows={'active': 1, 'chat_id': user_id, 'value': credit,
                              'name': user_detail['name'], 'user_name': user_detail['username'],
                              'operation': 1, 'date': datetime.now(pytz.timezone('Asia/Tehran'))})

            return get_credit
        except Exception as e:
            report_problem_to_admin_witout_context(chat_id=user_id, text='ADD TO WALLET [wallet script]', error=e)
            raise e

    def add_to_wallet_without_history(self, user_id, credit):
        try:
            credit = int(self.get_wallet_credit(user_id) + credit)
            get_credit = self.update(table={self.WALLET_TABALE: {self.WALLET_COLUMN: credit}},
                                     where=f'{self.USER_ID} = {user_id}')

            self.clear_wallet_notif(user_id)

            return get_credit
        except Exception as e:
            report_problem_to_admin_witout_context(chat_id=user_id, text='ADD TO WALLET WITHOUT HISTORY [wallet script]', error=e)
            return False

    @try_except
    def less_from_wallet(self, user_id, credit, user_detail):
        try:
            credit_all = int(self.get_wallet_credit(user_id) - credit)
            get_credit = self.update(table={self.WALLET_TABALE: {self.WALLET_COLUMN: credit_all}},
                                     where=f'{self.USER_ID} = {user_id}')

            self.insert(table='Credit_History',
                        rows={'active': 1, 'chat_id': user_id, 'value': credit,
                              'name': user_detail['name'], 'user_name': user_detail['username'],
                              'operation': 0, 'date': datetime.now(pytz.timezone('Asia/Tehran'))})

            return get_credit
        except Exception as e:
            report_problem_to_admin_witout_context(chat_id=user_id, text='LESS FROM WALLET [wallet script]', error=e)
            return False

    @try_except
    def less_from_wallet_with_condition_to_make_history(self, user_id, credit, user_detail, con):
        try:
            credit_all = int(self.get_wallet_credit(user_id) - credit)
            get_credit = self.update(table={self.WALLET_TABALE: {self.WALLET_COLUMN: credit_all}},
                                     where=f'{self.USER_ID} = {user_id}')

            if credit > con:
                self.insert(table='Credit_History',
                            rows={'active': 1, 'chat_id': user_id, 'value': credit,
                                  'name': user_detail['name'], 'user_name': user_detail['username'],
                                  'operation': 0, 'date': datetime.now(pytz.timezone('Asia/Tehran'))})

            return get_credit
        except Exception as e:
            report_problem_to_admin_witout_context(chat_id=user_id, text='LESS FROM WALLET [wallet script]', error=e)
            return False


    @try_except
    def set_credit(self, user_id, credit):
        get_credit = self.update(table={self.WALLET_TABALE: {self.WALLET_COLUMN: credit}},
                                 where=f'{self.USER_ID} = {user_id}')
        return get_credit

# a = WalletManage('User', 'wallet', 'v2ray', 'chat_id')
# print(a.less_from_wallet(6450325872, 1))
# print(a.get_all_wallet())