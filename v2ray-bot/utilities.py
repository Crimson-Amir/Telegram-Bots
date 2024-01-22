import arrow
from private import ADMIN_CHAT_ID


def human_readable(number):
    return arrow.get(number).humanize(locale="fa-ir")

def not_ready_yet(update, context):
    query = update.callback_query
    query.answer(text="ببخشید، درحال توسعه است.", show_alert=False)


def something_went_wrong(update, context):
    query = update.callback_query
    query.answer(text="مشکلی وجود دارد!", show_alert=False)


def just_for_show(update, context):
    query = update.callback_query
    query.answer(text="این دکمه برای نمایش دادن اطلاعات است!", show_alert=False)


def report_problem_to_admin(context, text):
    text = ("🔴 Report Problem in Bot\n\n"
            f"{text}")
    context.bot.send_message(ADMIN_CHAT_ID, text, parse_mode='html')


def ready_report_problem_to_admin(context, text, chat_id, error):
    text = ("🔴 Report Problem in Bot\n\n"
            f"Something Went Wrong In <b>{text}</b> Section."
            f"\nUser ID: {chat_id}"
            f"\nError Type: {type(error).__name__}"
            f"\nError Reason:\n{error}")
    context.bot.send_message(ADMIN_CHAT_ID, text, parse_mode='html')
    print(f'* REPORT TO ADMIN SUCCESS: ERR: {error}')


def format_traffic(traffic, without_text=None):
    if int(traffic) < 1:
        megabytes = traffic * 1024
        if without_text:
            return int(megabytes)
        return f"{int(megabytes)} مگابایت"
    else:
        return f"{traffic} گیگابایت"