from utilities import (ready_report_problem_to_admin)
from private import *
from admin_task import (api_operation, sqlite_manager)


def pay_per_use_calculator(context):
    get_all = api_operation.get_all_inbounds()

    get_from_db = sqlite_manager.select(
        column='id,chat_id,client_email,status,date,notif_day,notif_gb,inbound_id,client_id,product_id',
        table='Purchased')

    get_last_traffic_uasge = sqlite_manager.select(
        column='last_usage,date',
        table='Last_usage',
        order_by='id DECS',
        limit=1
    )

    last_usage_dict = {}

    try:
        for server in get_all:
            for config in server['obj']:
                for client in config['clientStats']:
                    for purchased in get_from_db:
                        if purchased[2] == client['email']:
                            purchased_wallet = []
                            last_traffic_usage = [last_traffic_use for last_traffic_use in get_last_traffic_uasge[0][0] if
                                                  last_traffic_use == purchased[0]]
                            print(last_traffic_usage)
                            # if client['enable']:
                            #
                            #     upload_mb = client['up'] / (1024 ** 4)
                            #     download_mb = client['down'] / (1024 ** 4)
                            #     usage_traffic = upload_mb + download_mb
                            #
                            #     traffic_use = (usage_traffic - last_traffic_usage[0][2]) * PRICE_PER_GB

                                # last_usage_dict[]



                            # else:
                            #     credit_now = purchased_wallet[0][1]


    except Exception as e:
        ready_report_problem_to_admin(context, 'PAY PER USE CALCULATOR', '', e)