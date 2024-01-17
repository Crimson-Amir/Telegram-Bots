rank_access = {
    'ROOKIE': {'level': range(1, 3), 'access': ['BUY_CONFIG', 'CHECK_ANALYSE'], 'price': {'per_gb': 1_000, 'per_day': 1_000}},
    'BRONZE': {'level': range(3, 8), 'access': ['ROOKIE', 'CHANGE_SETTING'], 'price': {'per_gb': 1_000, 'per_day': 1_000}},
    'SILVER': {'level': range(8, 20), 'access': ['BRONZE', 'DELETE_CONFIG', 'USE_WALLET', 'RESET_FREE_EVERY_MONTH']},
    'GOLD': {'level': range(20, 40), 'access': ['SILVER', 'PAY_AFTER_USE', 'PAYMENT_GETWAY']},
    'DIAMOND': {'level': range(40, 100), 'access': ['GOLD', 'GET_CONFIG_WITHOUT_CONFIRM']},
    'ADMIN': {'level': 100, 'access': ['DIAMOND', 'ALL_ACCSESS']},
    'OWNER': {'level': 1000},
}

rank_emoji = {
    'ROOKIE': '🆕',
    'BRONZE': '🔸',
    'SILVER': '💠',
    'GOLD': '🌟',
    'DIAMOND': '💎',
    'ADMIN': '🪙',
    'OWNER': '👑',
}

rank_persian = {
    'ROOKIE': 'تازه وارد',
    'BRONZE': 'برنز',
    'SILVER': 'نقره',
    'GOLD': 'طلا',
    'DIAMOND': 'الماس',
    'ADMIN': 'ادمین',
    'OWNER': 'سازنده',
}

