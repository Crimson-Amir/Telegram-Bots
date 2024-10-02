from _datetime import datetime, timedelta
import pytz, uuid, sys, os, logging, hashlib, qrcode
from io import BytesIO
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utilities_reFactore import FindText, message_token
from vpn_service import vpn_crud, panel_api
import setting

marzban_api = panel_api.MarzbanAPI()

@message_token.check_token
async def buy_custom_service(update, context):
    query = update.callback_query
    ft_instance = FindText(update, context)
    try:
        period_callback, traffic_callback = query.data.replace('vpn_set_period_traffic__', '').split('_')

        traffic = max(min(int(traffic_callback), 150), 5) or 40
        period = max(min(int(period_callback), 60), 5) or 30

        price = (traffic * setting.PRICE_PER_GB) + (period * setting.PRICE_PER_DAY)
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


async def create_json_config(username, expiration_in_day, traffic_in_byte):
    return {
        "username": username,
        "proxies": {
            "vless": {}
        },
        "inbounds": {
            "vless": [
                "VLESS TCP REALITY"
            ]
        },
        "expire": expiration_in_day,
        "data_limit": traffic_in_byte,
        "data_limit_reset_strategy": "no_reset",
        "status": "active",
        "note": "",
        "on_hold_timeout": "2023-11-03T20:30:00",
        "on_hold_expire_duration": 0
    }


async def create_service_in_servers(session, purchase_id: int):
    get_purchase = vpn_crud.get_purchase(session, purchase_id)

    if not get_purchase:
        raise ValueError('Purchase is empty!')

    username = (
        f"{get_purchase.purchase_id}_"
        f"{hashlib.sha256(f'{get_purchase.chat_id}.{uuid.uuid4().hex}'.encode()).hexdigest()[:5]}"
    )

    traffic_to_byte = int(get_purchase.traffic * (1024 ** 3))
    now = datetime.now(pytz.timezone('Asia/Tehran'))
    date_in_timestamp = (now + timedelta(days=get_purchase.period)).timestamp()


    json_config = await create_json_config(username, date_in_timestamp, traffic_to_byte)
    create_user = await marzban_api.add_user(get_purchase.product.main_server.server_ip, json_config)

    vpn_crud.update_purchase(session, purchase_id, username=username, subscription_url=create_user['subscription_url'])
    session.refresh(get_purchase)
    return get_purchase

async def create_service_for_user(update, context, session, purchase_id: int):
    get_purchase = await create_service_in_servers(session, purchase_id)

    ft_instance = FindText(update, context)
    main_server = get_purchase.product.main_server
    sub_link = f"{main_server.server_protocol}{main_server.server_ip}:{main_server.server_port}{get_purchase.subscription_url}"

    qr_code = qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=10,border=4)
    qr_code.add_data(sub_link)
    qr_code.make(fit=True)
    qr_image = qr_code.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    qr_image.save(buffer)
    binary_data = buffer.getvalue()

    keyboard = [[InlineKeyboardButton(await ft_instance.find_keyboard('vpn_my_service'), callback_data=f"vpn_my_service")],
                [InlineKeyboardButton(await ft_instance.find_keyboard('bot_main_menu'), callback_data=f"vpn_main_menu_new")]]

    await context.bot.send_photo(photo=binary_data,
                                 caption=await ft_instance.find_text('vpn_service_activated') + f'\n\n{sub_link}',
                                 chat_id=get_purchase.chat_id, reply_markup=InlineKeyboardMarkup(keyboard),
                                 parse_mode='html')
    return get_purchase


async def upgrade_service_for_user(update, context, session, purchase_id: int):
    purchase = await create_service_in_servers(session, purchase_id)
    ft_instance = FindText(update, context)
    traffic_to_byte = int(purchase.upgrade_traffic * (1024 ** 3))
    now = datetime.now(pytz.timezone('Asia/Tehran'))
    date_in_timestamp = (now + timedelta(days=purchase.upgrade_period)).timestamp()

    main_server_ip = purchase.product.main_server.server_ip
    json_config = await create_json_config(purchase.username, date_in_timestamp, traffic_to_byte)

    await marzban_api.modify_user(main_server_ip, purchase.username, json_config)
    vpn_crud.update_purchase(session, purchase_id, traffic=purchase.upgrade_traffic, period=purchase.upgrade_period)
    session.refresh(purchase)

    text = f"{await ft_instance.find_keyboard('upgrade_service_successfuly')}"
    text = text.format(purchase.username, purchase.upgrade_traffic, purchase.upgrade_period)

    await context.bot.send_message(text=text, chat_id=purchase.chat_id)
    return purchase
