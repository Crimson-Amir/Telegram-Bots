def not_ready_yet(update, context):
    query = update.callback_query
    query.answer(text="Not Ready Yet!", show_alert=False)
