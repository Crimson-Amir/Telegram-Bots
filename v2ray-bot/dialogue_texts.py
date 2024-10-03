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
    'usd': {
        'en': 'USD',
        'fa': 'دلار'
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

    'upgrade_vpn_service': {
        'en': 'Upgrade VPN service number {0}',
        'fa': 'ارتقاء سرویس VPN شماره {0}'
    },
    'traffic': {
        'en': 'Traffic:',
        'fa': '• ترافیک (حجم):'
    },
    'period': {
        'en': 'Period:',
        'fa': '• دوره زمانی:'
    },
    'payment_getway_title': {
        'en': '• Redirect to payment page',
        'fa': '• هدایت به صفحه پرداخت'
    },
    'zarinpal_payment_getway_body': {
        'en': 'By clicking the button below, you will be transferred to the payment page. Please be patient until the end of the payment process and the server response and do not close the page.',
        'fa': 'با کلیک روی دکمه پایین به صفحه پرداخت منتقل میشوید. لطفاً تا پایان فرآیند پرداخت صبور باشید و از بستن صفحه خودداری کنید.'
    },
    'payment_getway_tail': {
        'en': '• After completing the payment, the operation will be done automatically.',
        'fa': '• پس از تکمیل پرداخت، عملیات به صورت اتوماتیک انجام خواهد شد.'
    },
    'cryptomus_payment_getway_body': {
        'en': 'By clicking the button below, you will be transferred to the payment page. Please be careful about currency and network.',
        'fa': 'با کلیک روی دکمه پایین به صفحه پرداخت منتقل میشوید. لطفا به ارز و شبکه پراخت دقت کنید.'
    },
    'amount_added_to_wallet_successfully': {
        'en': 'The amount of {0} IRT has been successfully added to your wallet✅',
        'fa': 'مبلغ {0} تومان به کیف پول شما اضافه شد✅'
    },
    'payment_getway_lable': {
        'en': 'Payment Getway:',
        'fa': 'درگاه پرداخت:'
    },
    'zarinpal_lable': {
        'en': 'ZarinPal',
        'fa': 'زرین پال'
    },
    'cryptomus_lable': {
        'en': 'Cryptomus',
        'fa': 'cryptomus'
    },
    'just_for_show': {
        'en': 'this button jusr showing info.',
        'fa': 'این دکمه جهت نمایش دادن اطلاعات است.'
    },
    'invoice_already_paid': {
        'en': 'This invoice already paid.',
        'fa': 'این فاکتور قبلا پرداخت شده است.'
    },
    'not_enogh_credit': {
        'en': 'you dont have enoght credit to pay this invoice!',
        'fa': 'اعتبار شما برای پرداخت این فاکتور کافی نمیباشد!'
    },
    'invoice_paid_by_wallet_message': {
        'en': 'invoice paid successfully✅',
        'fa': 'فاکتور با موفقیت پرداخت شد✅'
    },
    'upgrade_service_successfuly': {
        'en': '🟢 Your service named {0} has been upgraded successfully!'
              '\n• The specifications added to the service are as follows:'
              '\n• Traffic: {1} GB'
              '\n• Time period: {2} days',
        'fa': '🟢 سرویس شما با نام {0} با موفقیت ارتقا یافت!'
              '\n• مشخصات اضافه شده به سرویس به شرح زیر میباشد:'
              '\n• ترافیک: {1} گیگابایت'
              '\n• دوره زمانی: {2} روز'
    },
    'no_service_available': {
        'en': 'You font have service!',
        'fa': 'شما صاحب سرویس نیستید!'
    },
    'select_service_category': {
        'en': 'Select the category fot view info:',
        'fa': 'برای مشاهده جزئیات، دسته بندی مورد نظر را انتخاب کنید:'
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
    'my_services': {
        'en': 'My Services 🎛',
        'fa': '🎛 سرویس‌های ‌من'
    },
    'invite': {
        'en': 'invite',
        'fa': 'دعوت'
    },
    'back_button': {
        'en': 'Back ↰',
        'fa': 'برگشت ↰'
    },
    'bot_main_menu': {
        'en': 'Bot main menu ↵',
        'fa': 'صفحه اصلی ربات ↵'
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
    'buy_vpn_service_lable': {
        'en': 'Buy vpn service',
        'fa': 'خرید سرویس vpn'
    },
    'vpn_services_lable': {
        'en': 'VPN service',
        'fa': 'سرویس VPN'
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
    'login_to_payment_getway': {
        'en': 'Go to pay ↷',
        'fa': 'ورود به درگاه ↶'
    },
    'fail_to_create_payment_getway': {
        'en': 'Failed to create payment getway!',
        'fa': 'ساخت درگاه پرداخت موفقیت آمیز نبود!'
    },

}

text_transaction.update(vpn_service_dialogues.text_transaction)
keyboard_transaction.update(vpn_service_dialogues.keyboard_transaction)
