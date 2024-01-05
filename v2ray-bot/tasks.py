from sqlite_manager import ManageDb

sqlite_manager = ManageDb('v2ray')


def not_ready_yet(update, context):
    query = update.callback_query
    query.answer(text="Not Ready Yet!", show_alert=False)


def buy_service(update, context):
    query = update.callback_query
    plans = sqlite_manager.select(table='Product', where='active = 1')
    print(plans)

