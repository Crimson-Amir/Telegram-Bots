from sqlite_manager import ManageDb

class WalletManage(ManageDb):
    def __init__(self, wallet_table, wallet_column, db_name, user_id_identifier):
        super().__init__(db_name)
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
        return get_credit

    @try_except
    def get_all_wallet(self):
        get_credit = self.select(column=self.WALLET_COLUMN, table=self.WALLET_TABALE)
        return get_credit

    @try_except
    def add_to_wallet(self, user_id, credit):
        credit = self.get_wallet_credit(user_id)[0][0] + credit
        get_credit = self.update(table={self.WALLET_TABALE: {self.WALLET_COLUMN: credit}},
                                 where=f'{self.USER_ID} = {user_id}')
        return get_credit

    @try_except
    def less_from_wallet(self, user_id, credit):
        credit = self.get_wallet_credit(user_id)[0][0] - credit
        get_credit = self.update(table={self.WALLET_TABALE: {self.WALLET_COLUMN: credit}},
                                 where=f'{self.USER_ID} = {user_id}')
        return get_credit

    @try_except
    def set_credit(self, user_id, credit):
        get_credit = self.update(table={self.WALLET_TABALE: {self.WALLET_COLUMN: credit}},
                                 where=f'{self.USER_ID} = {user_id}')
        return get_credit

# a = WalletManage('User', 'wallet', 'v2ray', 'chat_id')
# print(a.less_from_wallet(6450325872, 1))
# print(a.get_all_wallet())