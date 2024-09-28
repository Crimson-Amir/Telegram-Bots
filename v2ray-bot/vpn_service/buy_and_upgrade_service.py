import uuid
from _datetime import datetime, timedelta
import pytz
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utilities_reFactore import FindText, message_token, handle_error
from database_sqlalchemy import SessionLocal
from vpn_service import vpn_crud
import private, crud, logging

@message_token.check_token
async def buy_custom_service(update, context):
    query = update.callback_query
    ft_instance = FindText(update, context, notify_user=False)
    try:
        period_callback, traffic_callback = query.data.replace('vpn_set_period_traffic__', '').split('_')

        traffic = max(min(int(traffic_callback), 150), 5) or 40
        period = max(min(int(period_callback), 60), 5) or 30

        price = (traffic * private.PRICE_PER_GB) + (period * private.PRICE_PER_DAY)
        text = '\n' + await ft_instance.find_text('buy_service_title') + "\n\n" + await ft_instance.find_text('price') + f' {price:,} ' + await ft_instance.find_text('irt')

        keyboard = [
            [InlineKeyboardButton(await ft_instance.find_keyboard('vpn_traffic_lable'), callback_data="just_for_show")],
            [InlineKeyboardButton("➖", callback_data=f"vpn_set_period_traffic__{period}_{traffic - 5}"),
             InlineKeyboardButton(f"{traffic} {await ft_instance.find_keyboard('gb_lable')}", callback_data="just_for_show"),
             InlineKeyboardButton("➕", callback_data=f"vpn_set_period_traffic__{period}_{traffic + 10}")],
            [InlineKeyboardButton(await ft_instance.find_keyboard('period_traffic_lable'), callback_data="just_for_show")],
            [InlineKeyboardButton("➖", callback_data=f"vpn_set_period_traffic__{period - 5}_{traffic}"),
             InlineKeyboardButton(f"{period} {await ft_instance.find_keyboard('day_lable')}", callback_data="just_for_show"),
             InlineKeyboardButton("➕", callback_data=f"vpn_set_period_traffic__{period + 10}_{traffic}")],
            [InlineKeyboardButton(await ft_instance.find_keyboard('back_button'), callback_data='vpn_main_menu'),
             InlineKeyboardButton(await ft_instance.find_keyboard('confirm'), callback_data=f"create_invoice__buy_vpn_service__{period}__{traffic}")]
        ]

        await query.edit_message_text(text=text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    except Exception as e:
        if "specified new message content and reply markup are exactly the same" in str(e):
            return await query.answer()
        logging.error(f'error in wallet page: {e}')
        return await query.answer(await ft_instance.find_text('error_message'))


async def create_service_in_servers(purchased_id):

    try:
        with SessionLocal() as session:
            get_purchased = vpn_crud.get_purchased(session, purchased_id)
            client_id = uuid.uuid4().hex
            client_email = None

            traffic_to_byte = int(get_purchased.traffic * (1024 ** 3))

            now = datetime.now(pytz.timezone('Asia/Tehran'))
            expiration_in_day = now + timedelta(days=get_purchased.period)
            time_to_ms = int(expiration_in_day.timestamp() * 1000)

            data = {
                "id": get_purchased.inbound_id,
                "settings": "{{\"clients\":[{{\"id\":\"{0}\",\"alterId\":0,\"start_after_first_use\":true,"
                            "\"email\":\"{1}\",\"limitIp\":0,\"totalGB\":{2},\"expiryTime\":{3},"
                            "\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}}]}}".format(client_id, client_email, traffic_to_byte, time_to_ms)
            }

            create = api_operation.add_client(data, get_service_db[0][5])

            check_servise_available = api_operation.get_client(email_, domain=get_service_db[0][5])
            if not check_servise_available['obj']: return False, create, 'service do not create'

            get_cong = api_operation.get_client_url(email_, int(get_service_db[0][0]),
                                                    domain=get_service_db[0][4], server_domain=get_service_db[0][5],
                                                    host=inbound_host, header_type=inbound_header_type)

            sqlite_manager.update({'Purchased': {'inbound_id': int(get_service_db[0][0]),'client_email': email_,
                                                 'client_id': id_, 'date': datetime.now(pytz.timezone('Asia/Tehran')),
                                                 'details': get_cong, 'active': 1, 'status': 1}}, where=f'id = {purchased_id}')

            if create['success']:
                return True, create, 'service create success'
            else:
                return False, create, 'create service is failed'

        except Exception as e:
            utilities.report_problem_to_admin_witout_context('ADD CLIENT BOT [ADMIN TASK]', chat_id=None, error=e)
            return False, None, f'Error: {e}'


def create_service_for_user(query, context, id_, max_retries=2):
    create = add_client_bot(id_)
    if create[0]:
        get_client = sqlite_manager.select(table='Purchased', where=f'id = {id_}')
        try:
            get_product = sqlite_manager.select(column='price,domain,server_domain,inbound_host,inbound_header_type', table='Product', where=f'id = {get_client[0][6]}')
            get_user_detail = sqlite_manager.select(column='invited_by', table='User', where=f'chat_id={get_client[0][4]}')

            get_domain = get_product[0][1]
            get_server_domain = get_product[0][2]
            inbound_host = get_product[0][3]
            inbound_header_type = get_product[0][4]

            returned = api_operation.get_client_url(client_email=get_client[0][9], inbound_id=get_client[0][7],
                                                    domain=get_domain, server_domain=get_server_domain, host=inbound_host,
                                                    header_type=inbound_header_type)
            if returned:
                returned_copy = f'`{returned}`'
                qr_code = qrcode.make(returned)
                qr_image = qr_code.get_image()
                buffer = BytesIO()
                qr_image.save(buffer, format='PNG')
                binary_data = buffer.getvalue()
                keyboard = [[InlineKeyboardButton("دریافت فایل سرویس", callback_data=f"create_txt_file_{id_}"),
                             InlineKeyboardButton("🎛 سرویس های من", callback_data=f"my_service")],
                            [InlineKeyboardButton("صفحه اصلی ربات ↵", callback_data=f"main_menu_in_new_message")]]
                context.user_data['v2ray_client'] = returned

                context.bot.send_photo(photo=binary_data,
                                       caption=f' سرویس شما با موفقیت فعال شد✅\n\n*• میتونید جزئیات سرویس رو از بخش "سرویس های من" مشاهده کنید.\n\n✪ لطفا سرویس رو به صورت مستقیم از طریق پیام رسان های ایرانی یا پیامک ارسال نکنید، با کلیک روی گزینه "دریافت فایل" سرویس را به صورت فایل یا کیوآرکد ارسال کنید.* \n\n\nلینک:\n{returned_copy}',
                                       chat_id=get_client[0][4], reply_markup=InlineKeyboardMarkup(keyboard),
                                       parse_mode='markdown')

                price = ranking_manage.discount_calculation(direct_price=get_product[0][0], user_id=get_client[0][4])

                record_operation_in_file(chat_id=get_client[0][4], price=price,
                                         name_of_operation=f'خرید سرویس {get_client[0][9]}', operation=0,
                                         status_of_pay=1, context=context)

                send_service_to_customer_report(context, status=1, chat_id=get_client[0][4],
                                                service_name=get_client[0][9])

                invite_chat_id = get_user_detail[0][0]
                subcategory_auto(context, invite_chat_id, price)

                return {'success': True, 'msg': 'config created successfull', 'purchased_id': id_}
            else:
                send_service_to_customer_report(context, status=0, chat_id=get_client[0][4],
                                                service_name=get_client[0][9],
                                                more_detail=create)
                return {'success': False, 'msg': returned}

        except Exception as e:
            send_service_to_customer_report(context, status=0, chat_id=get_client[0][4], service_name=get_client[0][9],
                                            more_detail='ERROR IN SEND CLEAN FOR CUSTOMER', error=e)
            return {'success': False, 'msg': str(e)}

    elif not create[0] and create[2] == 'service do not create':
        send_service_to_customer_report(context, status=0, chat_id=None, service_name=None,
                                        more_detail=f'SERVICE DONT CREATED SUCCESSFULL AND TRY ONE MORE TIME (SEND CLEAN FOR CUSTOMER)\n{create}')
        if max_retries > 0:
            return send_clean_for_customer(query, context, id_, max_retries - 1)
        else:
            return {'success': False, 'msg': 'Maximum retries exceeded'}

    else:
        send_service_to_customer_report(context, status=0, chat_id=None, service_name=None,
                                        more_detail=f'EEROR IN ADD CLIENT (SEND CLEAN FOR CUSTOMER)\n{create}')
        return Exception(f'Error: {create}')