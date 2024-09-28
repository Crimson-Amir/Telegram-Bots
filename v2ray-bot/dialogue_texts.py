import vpn_service.dialogue_texts as vpn_service_dialogues


text_transaction = {
    'error_message': {
        'en': 'sorry, somthing went wrong!',
        'fa': 'ببخشید، مشکلی وجود داشت!'
    },
    'start_menu': {
        'en': 'Hi, welcome to DataGuardian Bot.',
        'fa': 'درود، به ربات فری بایت خوش آمدید!'
    },
    'select_section': {
        'en': 'Select the section you want to continue:',
        'fa': 'برای ادامه بخش مورد نظر خودتان را انتخاب کنید:'
    },
    'operation_successfull': {
        'en': 'The operation successful✅',
        'fa': 'عملیات با موفقیت انجام شد✅'
    },
    'operation_failed': {
        'en': 'The operation failed❌',
        'fa': 'عملیات شسکت خورد❌'
    },
    'message_expierd_send_new_message': {
        'en': 'The message has expired! The new menu has been sent to you.',
        'fa': 'پیام منقضی شده است! منو جدید برای شما ارسال شد'
    },
    'recent_transactions': {
        'en': '• Recent transactions:',
        'fa': '• تراکنش های اخیر:'
    },
    'recive_money': {
        'en': '💰 Recive',
        'fa': '💰 دریافت'
    },
    'spend_money': {
        'en': '💸 Spend',
        'fa': '💸 برداشت'
    },
    'irt': {
        'en': 'IRT',
        'fa': 'تومان'
    },
    'no_transaction_yet': {
        'en': 'you have no transactions yet!',
        'fa': 'شما تا به حال تراکنشی نداشتید!'
    },
    'wallet_page_title': {
        'en': 'Your wallet view:',
        'fa': 'اطلاعات کیف پول شما:'
    },
    'wallet_balance_key': {
        'en': '• Balance:',
        'fa': '• موجودی حساب:'
    },
    'last_transaction': {
        'en': '• Last transaction:',
        'fa': '• آخرین تراکنش:'
    },
    'add_crredit_to_wallet_title': {
        'en': '• Charge your wallet with one of this options:',
        'fa': '• مشخص کنید چه مقدار اعتبار به کیف پولتون اضافه بشه:'
    },
    'invoice_title': {
        'en': '• Check the information below and if approved, finalize the payment:',
        'fa': '• اطلاعات زیر را بررسی کنید و درصورت تایید، پرداخت را نهایی کنید:'
    },
    'price': {
        'en': 'Price:',
        'fa': 'مبلغ:'
    },
    'payment_option_title': {
        'en': '⤷ You can choose one of this methods for payment:',
        'fa': '⤶ برای پرداخت میتوانید یکی از روش های زیر را انتخاب کنید:'
    },
    'invoice_extra_data': {
        'en': '• Invoice information:',
        'fa': '• اطلاعات فاکتور:'
    },
    'charge_wallet': {
        'en': 'Charge wallet balance',
        'fa': 'افزایش اعتبار کیف پول'
    },
    'buy_vpn_service': {
        'en': 'Buy VPN service',
        'fa': 'خرید سرویس VPN'
    },
    'traffic': {
        'en': 'Traffic:',
        'fa': '• ترافیک (حجم):'
    },
    'period': {
        'en': 'Period:',
        'fa': '• دوره زمانی:'
    },


}

keyboard_transaction = {
    'error_message': {
        'en': 'sorry, somthing went wrong!',
        'fa': 'ببخشید، مشکلی وجود داشت!'
    },
    'menu_services': {
        'en': 'services 🎛️',
        'fa': 'خدمات 🎛️'
    },
    'wallet': {
        'en': 'wallet 👝',
        'fa': 'کیف پول 👝'
    },
    'ranking': {
        'en': 'ranking 👥️',
        'fa': 'رتبه بندی 👥️'
    },
    'setting': {
        'en': 'Setting ⚙️',
        'fa': 'تنظیمات ⚙️'
    },
    'invite': {
        'en': 'invite',
        'fa': 'دعوت'
    },
    'back_button': {
        'en': 'Back ↰',
        'fa': 'برگشت ↰'
    },
    'confirm': {
        'en': 'Confirm ✓',
        'fa': '✓ تایید'
    },
    'help_button': {
        'en': 'Help and support 📚',
        'fa': 'راهنما و پشتیبانی 📚'
    },
    'cancel_button': {
        'en': 'Cancel ✘',
        'fa': 'انصراف ✘'
    },
    'financial_transactions': {
        'en': '• Financial transactions',
        'fa': '• تراکنش های مالی'
    },
    'increase_balance': {
        'en': 'Increase balance ↟',
        'fa': 'افزایش موجودی ↟'
    },
    'refresh': {
        'en': 'refresh ⟳',
        'fa': 'تازه سازی ⟳'
    },
    'buy_vpn_service': {
        'en': 'Buy vpn service',
        'fa': 'خرید سرویس vpn'
    },
    'iran_payment_getway': {
        'en': 'Iran Payment Getway',
        'fa': 'درگاه پرداخت بانکی'
    },
    'cryptomus_payment_getway': {
        'en': 'Pay whth Crypto',
        'fa': 'پرداخت با کریپتو'
    },
    'pay_with_wallet_balance': {
        'en': 'Pay whth Wallet',
        'fa': 'پرداخت با کیف پول'
    },
    'not_enogh_rank': {
        'en': 'Not enoght rank to view this!',
        'fa': 'رتبه شما برای دیدن این قسمت کافی نیست!'
    },
}

text_transaction.update(vpn_service_dialogues.text_transaction)
keyboard_transaction.update(vpn_service_dialogues.keyboard_transaction)
