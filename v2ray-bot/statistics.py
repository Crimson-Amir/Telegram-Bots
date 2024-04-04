import datetime
from utilities import (ready_report_problem_to_admin)
import pytz
from admin_task import (api_operation, sqlite_manager)
from private import *


def pay_per_use_calculator(context):
    get_all = api_operation.get_all_inbounds()

    get_from_db = sqlite_manager.select(
        column='id,chat_id,client_email,status,date,notif_day,notif_gb,inbound_id,client_id,product_id',
        table='Purchased')

    get_last_traffic_uasge = sqlite_manager.select(
        column='last_usage,date',
        table='Last_usage',
        order_by='id DESC',
        limit=1
    )

    last_usage_dict = statistics_usage_traffic = {}

    try:
        for server in get_all:
            for config in server['obj']:
                for client in config['clientStats']:
                    for purchased in get_from_db:
                        if purchased[2] == client['email'] and client['enable']:

                            last_traffic_usage = eval(get_last_traffic_uasge[0][0]).get(str(purchased[0]), 0)

                            upload_mb = client['up'] / (1024 ** 2)
                            download_mb = client['down'] / (1024 ** 2)

                            usage_traffic = int((upload_mb + download_mb))
                            traffic_use = int((usage_traffic - last_traffic_usage))

                            last_usage_dict[str(purchased[0])] = usage_traffic
                            statistics_usage_traffic[str(purchased[0])] = traffic_use

        sqlite_manager.custom(f'INSERT INTO Last_usage (last_usage,date) VALUES ("{str(last_usage_dict)}", "{datetime.datetime.now(pytz.timezone('Asia/Tehran'))}")')

        sqlite_manager.custom(f'INSERT INTO Statistics (traffic_usage,date) VALUES ("{str(statistics_usage_traffic)}", "{datetime.datetime.now(pytz.timezone('Asia/Tehran'))}")')



    except IndexError as e:
        # ready_report_problem_to_admin(context, 'Statistics Timer IndexError!', '', e)
        sqlite_manager.insert(table='Last_usage', rows=[{'last_usage': "{}",
                                                         'date': datetime.datetime.now(pytz.timezone('Asia/Tehran'))}])

    except Exception as e:
        ready_report_problem_to_admin(context, 'Statistics Timer IndexError!', '', e)


pay_per_use_calculator(1)