from sqlite_manager import ManageDb
from private import PRICE_PER_DAY, PRICE_PER_GB


rank_access = {
    'ROOKIE': {'level': range(1, 10), 'access': ['BUY_SERVICE', 'CHECK_ANALYSE', 'CHANGE_SETTINGS', 'USE_WALLET']},
    'BRONZE': {'level': range(10, 200), 'access': ['ROOKIE']},
    'SILVER': {'level': range(200, 500), 'access': ['BRONZE', '5off']},
    'GOLD': {'level': range(500, 1_000), 'access': ['SILVER', '9off']},
    'DIAMOND': {'level': range(1_000, 5_000), 'access': ['GOLD', 'GET_SERVICE_WITHOUT_CONFIRM', '15off']},
    'SUPER_USER': {'level': range(5_000, 20_000), 'access': ['DIAMOND', '20off']},
    'ADMIN': {'level': range(20_000, 100_000), 'access': ['SUPER_USER', 'BOT_MANAGER']},
    'OWNER': {'level': range(100_000, 1_000_000), 'access': ['ALL']},
}

pay_after_use_per_rank = {
    'SILVER': 1,
    'GOLD': 5,
    'DIAMOND': 10,
    'SUPER_USER': 20,
}

off_per_rank = {
    'ROOKIE': 0,
    'BRONZE': 2,
    'SILVER': 6,
    'GOLD': 7,
    'DIAMOND': 9,
    'SUPER_USER': 20,
}

rank_emojis = {
    'ROOKIE': '🌱',
    'BRONZE': '🥉',
    'SILVER': '🥈',
    'GOLD': '🌟',
    'DIAMOND': '💎',
    'SUPER_USER': '🚀',
    'ADMIN': '👑',
    'OWNER': '🌐',
}


rank_access_fa = {
    'ROOKIE': ['None', 'خرید سرویس', 'بررسی آمار سرویس', 'تغییر تنظیمات ربات', 'استفاده از کیف پول'],
    'BRONZE': ['ROOKIE'],
    'SILVER': ['BRONZE'],
    'GOLD': ['SILVER'],
    'DIAMOND': ['GOLD', 'دریافت سرویس بدون بررسی ادمین'],
    'SUPER_USER': ['DIAMOND'],
    'ADMIN': ['SUPER_USER', 'مدیریت ربات'],
}

rank_title_fa = {
    'ROOKIE': 'تازه وارد',
    'BRONZE': 'برنز',
    'SILVER': 'نقره',
    'GOLD': 'طلا',
    'DIAMOND': 'الماس',
    'ADMIN': 'ادمین',
    'SUPER_USER': 'کاربر ویژه',
    'OWNER': 'سازنده',
}


class RankManage(ManageDb):
    def __init__(self, rank_table, level_column, rank_column, db_name, user_id_identifier):
        super().__init__(db_name)
        self.database_name = db_name
        self.RANK_TABALE = rank_table
        self.LEVEL_COLUMN = level_column
        self.RANK_COLUMN = rank_column
        self.identifier = user_id_identifier

        get_partner_chat_id = self.select(column='chat_id', table='Partner')
        self.list_of_partner = [partner[0] for partner in get_partner_chat_id]

    @staticmethod
    def get_rank_name_by_level(level):
        return [rank_key for rank_key, value in rank_access.items() if level in value['level']][0]

    @staticmethod
    def get_range_of_level_by_rank(rank_name):
        return [value['level'] for rank_key, value in rank_access.items() if rank_name == rank_key][0]

    @staticmethod
    def get_all_access(rank):
        all_access = []
        for key, value in rank_access.items():
            all_access += value['access'][1:]
            if key == rank:
                break
        return all_access

    @staticmethod
    def get_all_access_fa(rank):
        all_access = []
        for key, value in rank_access_fa.items():
            all_access += value[1:]
            if key == rank:
                break
        return all_access

    def get_partner(self):
        get_partner_chat_id = self.select(column='chat_id', table='Partner')
        self.list_of_partner = [partner[0] for partner in get_partner_chat_id]

    def get_user_rank_and_level(self, user_id):
        try:
            return self.select(column=f'{self.RANK_COLUMN}, {self.LEVEL_COLUMN}', table=self.RANK_TABALE, where=f'{self.identifier} = {user_id}')[0]
        except Exception as e:
            print(f'* Error In get_user_rank_and_level: {e}')

    def update_rank_with_level(self, level, user_id):
        rank_name = self.get_rank_name_by_level(level)
        self.update({self.RANK_TABALE: {self.RANK_COLUMN: rank_name, self.LEVEL_COLUMN: level}}, where=f'{self.identifier} = {user_id}')


    def set_rank_to(self, rank, user_id):
        if isinstance(rank, str):
            rank = self.get_range_of_level_by_rank(rank)[0]

        self.update_rank_with_level(rank, user_id)

    def rank_up(self, rank, user_id):
        if isinstance(rank, str):
            rank = self.get_range_of_level_by_rank(rank)[0]

        user_rank = self.get_user_rank_and_level(user_id)
        rank += user_rank[1]

        self.update_rank_with_level(rank, user_id)

    def rank_down(self, rank, user_id):
        if isinstance(rank, str):
            rank = self.get_range_of_level_by_rank(rank)[0]

        user_rank = self.get_user_rank_and_level(user_id)
        rank = user_rank[1] - rank

        self.update_rank_with_level(rank, user_id)

    def discount_calculation(self, user_id, traffic=None, period=None, direct_price=None, without_off=False, more_detail=False):
        price_per_gb, price_per_day = PRICE_PER_GB, PRICE_PER_DAY

        if user_id in self.list_of_partner:
            get_detail_of_partner = self.select('traffic_price,period_price', 'Partner', where=f'chat_id = {user_id}')
            price_per_gb = get_detail_of_partner[0][0]
            price_per_day = get_detail_of_partner[0][1]

        user_rank = self.select(table='Rank', where=f'chat_id = {user_id}')
        price = direct_price if direct_price is not None else (traffic * price_per_gb) + (period * price_per_day)

        if without_off: return price
        if not user_rank:
            detail = (price, 0, price) if more_detail else price
            return detail

        off = (price * off_per_rank[user_rank[0][5]] / 100)
        final_price = round((price - off), -2)
        detail = (int(final_price), off_per_rank[user_rank[0][5]], price) if more_detail else int(final_price)
        return detail


    def enough_rank(self, task, user_id):
        user_rank = self.select(table='Rank', where=f'chat_id = {user_id}')
        if not user_rank: return False
        all_access = self.get_all_access(user_rank[0][5])
        # user_rank_detail =  [value for rank_key, value in rank_access.items() if user_rank[0][5] == rank_key and task in value['access']]
        return True if task in all_access else False

# a = RankManage('Rank', 'level', 'rank_name',db_name='v2ray', user_id_identifier='chat_id')
# print(a.enough_rank('GET_SERVICE_WITHOUT_CONFIRM', 6450325872))