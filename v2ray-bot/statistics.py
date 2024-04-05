from datetime import datetime, timedelta
from utilities import (ready_report_problem_to_admin)
import pytz
from admin_task import (api_operation, sqlite_manager)
from private import *


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


def reports_section(purchased, period, chat_id):
    date_now = datetime.now(pytz.timezone('Asia/Tehran'))
    get_all_purchased = purchased

    if purchased == 'all':
        get_all_purchased_from_db = sqlite_manager.select(column='id', table='Purchased', where=f'chat_id = {chat_id}')
        get_all_purchased = [str(id_[0]) for id_ in get_all_purchased_from_db]


    if period == 'daily':
        date = date_now.strftime('%Y-%m-%d')
    elif period == 'weekly':
        date = date_now - timedelta(days=7)
    elif period == 'monthly':
        date = date_now - timedelta(days=30)
    else:
        date = date_now - timedelta(days=365)

    get_db = sqlite_manager.select(table='Statistics', where=f'date > "{date}"')
    user_usage_dict = {}

    for get_date in get_db:
        get_user_usage = [{user_purchased[0]: user_purchased[1]} for user_purchased in eval(get_date[1]).items() if user_purchased[0] in get_all_purchased]
        user_usage_dict[get_date[2]] = get_user_usage

    return user_usage_dict


reports_section('all', 'monthly', 101854406)