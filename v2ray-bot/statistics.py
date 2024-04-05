from datetime import datetime, timedelta
from utilities import (ready_report_problem_to_admin)
import pytz
from admin_task import (api_operation, sqlite_manager)
from private import *
from utilities import format_mb_traffic, make_day_name_farsi


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

        sqlite_manager.custom(f'INSERT INTO Last_usage (last_usage,date) VALUES ("{str(last_usage_dict)}", "{date}")')

        sqlite_manager.custom(f'INSERT INTO Statistics (traffic_usage,date) VALUES ("{str(statistics_usage_traffic)}", "{date}")')



    except IndexError as e:
        ready_report_problem_to_admin(context, 'Statistics Timer IndexError!', '', e)
        sqlite_manager.insert(table='Last_usage', rows=[{'last_usage': "{}",
                                                         'date': date}])

    except Exception as e:
        ready_report_problem_to_admin(context, 'Statistics Timer IndexError!', '', e)


def datetime_range(start, end, delta):
    current = start
    while current <= end:
        yield current
        current += delta


def reports_section(update, context):
    # query = update.callback_query
    # data = query.data.split('_')
    # chat_id = query.message.chat_id
    data = [0, 'monthly', 'all']
    chat_id = 81532053

    date_now = datetime.now(pytz.timezone('Asia/Tehran'))

    purchased = data[2]
    period = data[1]

    if purchased == 'all':
        get_all_purchased_from_db = sqlite_manager.select(column='id', table='Purchased', where=f'chat_id = {chat_id}')
        purchased = [str(id_[0]) for id_ in get_all_purchased_from_db]

    period_mapping = {
        'daily': (1, 'روزانه'),
        'weekly': (7, 'هفتگی'),
        'monthly': (30, 'ماهانه'),
        'yearly': (365, 'سالانه')
    }

    period_info = period_mapping.get(period, (365, 'سالانه'))
    delta_days, period_text = period_info
    date = date_now - timedelta(days=delta_days)

    get_db = sqlite_manager.select(table='Statistics', where=f'date > "{date}"')
    user_usage_dict = {}

    for get_date in get_db:
        get_user_usage = [{user_purchased[0]: user_purchased[1]} for user_purchased in eval(get_date[1]).items() if user_purchased[0] in purchased]
        user_usage_dict[get_date[2]] = get_user_usage

    usage_text = ''

    if period == 'daily':
        for _ in user_usage_dict.items():
            time = datetime.strptime(_[0], '%Y-%m-%d %H:%M:%S')
            first_time = time - timedelta(hours=STATISTICS_TIMER_HORSE)
            usage_detail, all_usage_traffic = [], 0

            for usage in _[1]:
                usage_name = next(iter(usage.keys()))
                usage_traffic = next(iter(usage.values()))

                usage_detail.append(f'\n- سرویس شماره {usage_name}: {format_mb_traffic(usage_traffic)}' if usage_traffic else '')
                all_usage_traffic += usage_traffic

            usage_text += f'\n\n• از ساعت {first_time.strftime("%H:%M")} تا {time.strftime("%H:%M")} = {format_mb_traffic(all_usage_traffic)}'
            usage_text += ''.join(usage_detail[:4])

    elif period == 'weekly':
        for our_date in datetime_range(date, date_now, timedelta(days=1)):
            date_ = our_date.strftime('%Y-%m-%d')
            get_usage = {}
            get_traff = 0
            for _ in user_usage_dict.items():
                time = datetime.strptime(_[0], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                if time == date_:
                    for usage in _[1]:
                        usage_name = next(iter(usage.keys()))
                        usage_traffic = next(iter(usage.values()))
                        get_traff += usage_traffic
                        get_usage[usage_name] = get_usage.get(usage_name, 0) + usage_traffic

            usage_detail = [f'\n- سرویس شماره {get_name} = {format_mb_traffic(get_traffic)}' for get_name, get_traffic in get_usage.items() if get_traffic]

            usage_text += f'\n\n• در {make_day_name_farsi(our_date.strftime('%A'))} {date_} = {format_mb_traffic(get_traff)}'
            usage_text += ''.join(usage_detail[:5])

    elif period == 'monthly':
        for our_date in datetime_range(date, date_now, timedelta(days=7)):
            date_ = our_date.strftime('%Y-%m')
            get_usage = {}
            get_traff = 0
            for _ in user_usage_dict.items():
                time = datetime.strptime(_[0], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m')
                if time == date_:
                    for usage in _[1]:
                        usage_name = next(iter(usage.keys()))
                        usage_traffic = next(iter(usage.values()))
                        get_traff += usage_traffic
                        get_usage[usage_name] = get_usage.get(usage_name, 0) + usage_traffic

            usage_detail = [f'\n- سرویس شماره {get_name} = {format_mb_traffic(get_traffic)}' for get_name, get_traffic
                            in get_usage.items() if get_traffic]

            usage_text += f'\n\n• در {make_day_name_farsi(our_date.strftime('%A'))} {date_} = {format_mb_traffic(get_traff)}'
            usage_text += ''.join(usage_detail[:5])

    elif period == 'yearly':
        for our_date in datetime_range(date, date_now, timedelta(days=30)):
            date_ = our_date.strftime('%Y-%m')
            get_usage = {}
            get_traff = 0
            for _ in user_usage_dict.items():
                time = datetime.strptime(_[0], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m')
                if time == date_:
                    for usage in _[1]:
                        usage_name = next(iter(usage.keys()))
                        usage_traffic = next(iter(usage.values()))
                        get_traff += usage_traffic
                        get_usage[usage_name] = get_usage.get(usage_name, 0) + usage_traffic

            usage_detail = [f'\n- سرویس شماره {get_name} = {format_mb_traffic(get_traffic)}' for get_name, get_traffic
                            in get_usage.items() if get_traffic]

            usage_text += f'\n\n• در {make_day_name_farsi(our_date.strftime('%A'))} {our_date} = {format_mb_traffic(get_traff)}'
            usage_text += ''.join(usage_detail[:5])


    print(usage_text)



reports_section('all', 'monthly')
# statistics_timer(1)