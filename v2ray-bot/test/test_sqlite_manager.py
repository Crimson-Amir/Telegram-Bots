# import unittest
# from sqlite_manager import ManageDb
#
# sqlite_manager = ManageDb()
#
# class SqliteManagerTest(unittest.TestCase):
#     pass
import random
import uuid
from datetime import datetime, timedelta
import telegram.error

import private
from utilities import (human_readable, something_went_wrong,
                       ready_report_problem_to_admin, format_traffic, record_operation_in_file,
                       send_service_to_customer_report, report_status_to_admin, find_next_rank,
                       change_service_server, get_rank_and_emoji, report_problem_by_user_utilitis, report_problem,
                       format_mb_traffic)
import admin_task
from private import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
import ranking
import utilities
from admin_task import (add_client_bot, api_operation, second_to_ms, message_to_user, wallet_manage, sqlite_manager,
                        ranking_manage)
import qrcode
from io import BytesIO
import pytz
import re
import functools
from sqlite_manager import ManageDb
import json


ret_conf = api_operation.get_inbound(2, 'finland.ggkala.shop')
client_list = json.loads(ret_conf['obj']['settings'])['clients']
print(client_list)