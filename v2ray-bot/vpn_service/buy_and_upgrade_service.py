import random
from _datetime import datetime, timedelta
import pytz, uuid, sys, os, logging, json, hashlib, qrcode
from io import BytesIO
from sqlalchemy import update as slalchemy_update
import models_sqlalchemy as model
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utilities_reFactore import FindText, message_token
from vpn_service import vpn_crud
import private

# api_operation = api_clean.XuiApiClean()

@message_token.check_token
async def buy_custom_service(update, context):
    query = update.callback_query
    ft_instance = FindText(update, context)
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


async def create_service_in_servers(session, purchase_id: int):
    get_purchase = vpn_crud.get_purchase(session, purchase_id)

    if not get_purchase:
        raise ValueError('Purchase is empty!')

    client_id = uuid.uuid4().hex
    inbound_id = random.choice(get_purchase.product.inbound_id)
    token = hashlib.sha256(f'{client_id}.{inbound_id}'.encode()).hexdigest()[:8]
    client_email = f"{get_purchase.purchase_id}_{token}"
    client_addresses = ''

    for server in get_purchase.product.server_associations:
        server_address = server.server.server_ip

        traffic_to_byte = int(get_purchase.traffic * (1024 ** 3))
        now = datetime.now(pytz.timezone('Asia/Tehran'))
        expiration_in_day = now + timedelta(days=get_purchase.period)
        time_to_ms = int(expiration_in_day.timestamp() * 1000)

        data = {
            "id": inbound_id,
            "settings": "{{\"clients\":[{{\"id\":\"{0}\",\"alterId\":0,\"start_after_first_use\":true,"
                        "\"email\":\"{1}\",\"limitIp\":0,\"totalGB\":{2},\"expiryTime\":{3},"
                        "\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}}]}}".format(client_id, client_email, traffic_to_byte, time_to_ms)
        }

        api_operation.add_client(data, server_address)
        check_servise_available = api_operation.get_client(client_email, domain=server_address)

        if not check_servise_available['obj']:
            raise ConnectionRefusedError('client was not create in server!')

        add_server_info = model.ClientServerAssociation(
            server_id=server.server_id,
            purchase_id=purchase_id,
            connected_iran_server_ips=server.server.connected_iran_server_ips
        )

        session.add(add_server_info)

        for iran_server in server.server.connected_iran_server_ips:

            get_config = api_operation.get_client_url(
                client_email, inbound_id,
                domain=iran_server,
                server_domain=server_address,
                host=get_purchase.product.inbound_host,
                header_type=get_purchase.product.inbound_header_type,
                remark=server.server.flag + ' ' + server.server.country_name_short
            )
            client_addresses += '\n' + get_config

    stmt = (
        slalchemy_update(model.Purchase)
        .where(model.Purchase.purchase_id == purchase_id)
        .values(
            inbound_id=inbound_id,
            client_email=client_email,
            client_id=client_id,
            register_date=datetime.now(pytz.timezone('Asia/Tehran')),
            token=token,
            active=True,
            client_addresses=client_addresses
        )
    )
    session.execute(stmt)
    session.refresh(get_purchase)
    return get_purchase


async def create_service_for_user(update, context, session, purchase_id: int):
        get_purchase = await create_service_in_servers(session, purchase_id)

        ft_instance = FindText(update, context)
        sub_link = get_purchase.product.sub_web_app_endpoint + get_purchase.token

        qr_code = qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=10,border=4)
        qr_code.add_data(sub_link)
        qr_code.make(fit=True)
        qr_image = qr_code.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        qr_image.save(buffer)
        binary_data = buffer.getvalue()

        keyboard = [[InlineKeyboardButton(await ft_instance.find_keyboard('vpn_my_service'), callback_data=f"vpn_my_service")],
                    [InlineKeyboardButton(await ft_instance.find_keyboard('bot_main_menu'), callback_data=f"vpn_main_menu")]]

        await context.bot.send_photo(photo=binary_data,
                                     caption=await ft_instance.find_text('vpn_service_activated') + f'\n\n{sub_link}',
                                     chat_id=get_purchase.chat_id, reply_markup=InlineKeyboardMarkup(keyboard),
                                     parse_mode='html')
        return get_purchase
