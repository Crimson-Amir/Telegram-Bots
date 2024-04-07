from datetime import datetime, timedelta
from utilities import (ready_report_problem_to_admin)
import pytz
from admin_task import (api_operation, sqlite_manager)
# from private import *
from utilities import format_mb_traffic, make_day_name_farsi
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from plot import get_plot


STATISTICS_TIMER_HORSE = 3


def statistics_timer(context):
    get_all = api_operation.get_all_inbounds()

    date_now = datetime.now(pytz.timezone('Asia/Tehran'))
    date = datetime.strftime(date_now, '%Y-%m-%d %H:%M:%S')
    print(date)
    get_from_db = sqlite_manager.select(
        column='id,chat_id,client_email,status,date,notif_day,notif_gb,inbound_id,client_id,product_id',
        table='Purchased')

    get_last_traffic_uasge = sqlite_manager.select(
        column='last_usage,date',
        table='Last_usage',
        order_by='id DESC',
        limit=1
    )

    last_usage_dict, statistics_usage_traffic = {}, {}

    try:
        for server in get_all:
            for config in server['obj']:
                for client in config['clientStats']:
                    for purchased in get_from_db:
                        if purchased[2] == client['email'] and client['enable']:

                            last_traffic_usage = eval(get_last_traffic_uasge[0][0]).get(str(purchased[0]), None)

                            upload_mb = client['up'] / (1024 ** 2)
                            download_mb = client['down'] / (1024 ** 2)

                            usage_traffic = int((upload_mb + download_mb))
                            last_usage_dict[str(purchased[0])] = usage_traffic

                            if not last_traffic_usage: continue
                            traffic_use = int((usage_traffic - last_traffic_usage))
                            statistics_usage_traffic[str(purchased[0])] = traffic_use

        list_of_order = [f'INSERT INTO Last_usage (last_usage,date) VALUES ("{str(last_usage_dict)}", "{date}")',
                         f'INSERT INTO Statistics (traffic_usage,date) VALUES ("{str(statistics_usage_traffic)}", "{date}")']

        sqlite_manager.custom_multi(*list_of_order)



    except IndexError as e:
        ready_report_problem_to_admin(context, 'Statistics Timer IndexError!', '', e)
        if 'list index out of range' in str(e):
            sqlite_manager.insert(table='Last_usage', rows=[{'last_usage': "{}",
                                                             'date': date}])

    except Exception as e:
        ready_report_problem_to_admin(context, 'Statistics Timer IndexError!', '', e)


def datetime_range(start, end, delta):
    current = start
    while current <= end:
        yield current
        current += delta


def reports_func(data):

    chat_id = data[0]
    date_now = datetime.now(pytz.timezone('Asia/Tehran'))
    get_purchased = [str(data[2])]
    purchased = get_purchased
    period = data[1]

    if purchased[0] == 'all':
        get_all_purchased_from_db = sqlite_manager.select(column='id', table='Purchased', where=f'chat_id = {chat_id}')
        purchased = [str(id_[0]) for id_ in get_all_purchased_from_db]

    period_mapping = {
        'day': (1, 'روز'),
        'week': (7, 'هفته'),
        'month': (30, 'ماه'),
        'year': (365, 'سال')
    }

    delta_days, period_text = period_mapping.get(period, (365, 'سالانه'))
    date = date_now - timedelta(days=delta_days)

    get_db = sqlite_manager.select(table='Statistics', where=f'date > "{date}"')
    user_usage_dict = {}

    for get_date in get_db:
        get_user_usage = [{user_purchased[0]: user_purchased[1]} for user_purchased in eval(get_date[1]).items() if user_purchased[0] in purchased]
        user_usage_dict[get_date[2]] = get_user_usage

    detail_text, final_dict, final_traffic, avreage_traffic, index = '', {}, 0, 0, 1

    if period == 'day':
        for index, (timestamp, usage_list) in enumerate(user_usage_dict.items()):
            time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            first_time = time - timedelta(hours=STATISTICS_TIMER_HORSE)
            usage_detail, get_traffic = [], 0

            for usage in usage_list:
                usage_name = next(iter(usage.keys()))
                usage_traffic = next(iter(usage.values()))

                usage_detail.append(
                    f'\n- سرویس شماره {usage_name} = {format_mb_traffic(usage_traffic)}' if usage_traffic else '')
                get_traffic += usage_traffic

            detail_text += f'\n\n• از ساعت {first_time.strftime("%H:%M")} تا {time.strftime("%H:%M")} = {format_mb_traffic(get_traffic)}'
            detail_text += ''.join(usage_detail[:5]) if get_purchased[0] == 'all' else ''

            final_traffic += get_traffic
            final_dict[f'{first_time.strftime("%H")} to {time.strftime("%H")}'] = get_traffic

        avreage_traffic = (final_traffic / 3) / index

    elif period == 'week':
        for index, our_date in enumerate(datetime_range(date, date_now, timedelta(days=1))):
            date_ = our_date.strftime('%Y-%m-%d')
            get_usage, get_traff = {}, 0
            for _ in user_usage_dict.items():
                time = datetime.strptime(_[0], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                if time == date_:
                    for usage in _[1]:
                        usage_name, usage_traffic = next(iter(usage.items()))
                        get_traff += usage_traffic
                        get_usage[usage_name] = get_usage.get(usage_name, 0) + usage_traffic

            usage_detail = [f'\n- سرویس شماره {get_name} = {format_mb_traffic(get_traffic)}' for get_name, get_traffic in get_usage.items() if get_traffic]
            detail_text += f"\n\n• در {make_day_name_farsi(our_date.strftime('%A'))} {date_} = {format_mb_traffic(get_traff)}"
            detail_text += ''.join(usage_detail[:5]) if get_purchased[0] == 'all' else ''

            final_traffic += get_traff
            final_dict[f"{our_date.strftime('%A')}"] = get_traff

        avreage_traffic = final_traffic / index


    period_info = {
        'month': {'timedelta': timedelta(days=7), 'date_format': '%Y-%m'},
        'year': {'timedelta': timedelta(days=30), 'date_format': '%Y-%m'}
    }

    for period_key, period_value in period_info.items():
        if period == period_key:
            for our_date in datetime_range(date, date_now, period_value['timedelta']):
                date_ = our_date.strftime(period_value['date_format'])
                get_usage, get_traff = {}, 0
                for _ in user_usage_dict.items():
                    time = datetime.strptime(_[0], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m')
                    if time == date_:
                        for usage in _[1]:
                            usage_name, usage_traffic = next(iter(usage.items()))
                            get_traff += usage_traffic
                            get_usage[usage_name] = get_usage.get(usage_name, 0) + usage_traffic

                usage_detail = [f'\n- سرویس شماره {get_name} = {format_mb_traffic(get_traffic)}' for get_name, get_traffic
                                in get_usage.items() if get_traffic]

                detail_text += f'\n\n• در {our_date.strftime("%Y-%m-%d")} = {format_mb_traffic(get_traff)}'
                detail_text += ''.join(usage_detail[:5]) if get_purchased[0] == 'all' else ''

                final_traffic += get_traff
                final_dict[f"{our_date.strftime('%Y-%m')}"] = get_traff

            avreage_traffic = final_traffic / index
            break

    return detail_text, final_dict, final_traffic, avreage_traffic


def report_section(update, context):
    query = update.callback_query
    data_org = query.data.split('_')  # statistics_day_all_hide
    chat_id = query.message.chat_id
    data = [chat_id, data_org[1], data_org[2]]
    get_data = reports_func(data)

    if sum(get_data[1].values()) == 0:
        keyboard = [[InlineKeyboardButton("برگشت ↰", callback_data='main_menu')]]
        query.edit_message_text('<b>مصرفی برای شما ثبت نشده است.</b>', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    mapping = {
        'day': (None, 'روز', f'statistics_week_{data[2]}_{data_org[3]}', 'ساعت'),
        'week': (f'statistics_day_{data[2]}_{data_org[3]}', 'هفته', f'statistics_month_{data[2]}_{data_org[3]}', 'روز'),
        'month': (f'statistics_week_{data[2]}_{data_org[3]}', 'ماه', f'statistics_year_{data[2]}_{data_org[3]}', 'هفته'),
        'year': (f'statistics_month_{data[2]}_{data_org[3]}', 'سال', None, 'ماه'),
    }

    back_button, button_name, next_button, constituent_name = (
        mapping.get(data[1], (f'statistics_day_{data[2]}', 'هفته', f'statistics_month_{data[2]}', 'روز')))

    detail_emoji, detail_callback, detail_text = '➕', 'open', ''

    if data_org[3] == 'open':
        detail_emoji, detail_callback = '➖', 'hide'
        detail_text = get_data[0]

    arrows = []
    if back_button: arrows.append(InlineKeyboardButton("⇤", callback_data=back_button))
    arrows.append(InlineKeyboardButton(f"{button_name}", callback_data='just_for_show'))
    if next_button: arrows.append(InlineKeyboardButton("⇥", callback_data=next_button))

    keyboard = [
        arrows,
        [InlineKeyboardButton(f"{detail_emoji} جزئیات گزارش", callback_data=f'statistics_{data[1]}_{data[2]}_{detail_callback}')],
        [InlineKeyboardButton(f"مشاهده گزارش سرویس ها", callback_data=f'service_statistics_all')],
        [InlineKeyboardButton("برگشت ↰", callback_data='menu_delete_main_message')]
    ]

    get_plot_image = get_plot(get_data[1], data[1])

    text = (f'<b>گزارش مصرف {button_name}:</b>'
            f'\n\n<b>• مصرف کل {button_name}: {format_mb_traffic(get_data[2])}</b>'
            f'\n<b>• میانگین مصرف در {constituent_name}: {format_mb_traffic(get_data[3])}</b>')
    text += f'\n{detail_text}'

    if query.message.photo:
        media_photo = InputMediaPhoto(media=get_plot_image, caption=text, parse_mode='html')
        context.bot.edit_message_media(media=media_photo, chat_id=chat_id, message_id=query.message.message_id)
        context.bot.edit_message_caption(caption=text, parse_mode='html', chat_id=chat_id,
                                         message_id=query.message.message_id,
                                         reply_markup=InlineKeyboardMarkup(keyboard))

    else:
        query.delete_message()
        context.bot.send_photo(photo=get_plot_image, chat_id=chat_id, caption=text,
                               reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')


# reports_func('all')
# statistics_timer(1)