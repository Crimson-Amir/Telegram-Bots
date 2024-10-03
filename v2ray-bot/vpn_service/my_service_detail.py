from _datetime import datetime
import sys, os
import requests.exceptions
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utilities_reFactore import FindText, message_token, handle_error, human_readable
from vpn_service import vpn_crud
from database_sqlalchemy import SessionLocal
from vpn_service.panel_api import marzban_api

@handle_error.handle_functions_error
@message_token.check_token
async def my_services(update, context):
    query = update.callback_query
    ft_instance = FindText(update, context)
    user_detail = update.effective_chat

    with SessionLocal() as session:
        with session.begin():
            purchases = vpn_crud.get_purchase_by_chat_id(session, user_detail.id)

            if not purchases:
                return await query.answer(await ft_instance.find_text('no_service_available'), show_alert=True)

            service_status = {
                True: '✅',
                False: '🔴'
            }

            text = f"<b>{await ft_instance.find_text('vpn_selected_service_info')}</b>"
            keyboard = [[InlineKeyboardButton(f"{service.username} {service_status.get(service.active)}",
                                              callback_data=f'vpn_my_service_detail__{service.purchase_id}')]
                        for service in purchases]
            keyboard.append([InlineKeyboardButton(await ft_instance.find_keyboard('back_button'), callback_data='my_services_new')])

            if update.callback_query and update.callback_query.data != 'vpn_my_services_new':
                return await query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))
            return await context.bot.send_message(chat_id=user_detail.id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='html')


@handle_error.handle_functions_error
@message_token.check_token
async def service_info(update, context):
    query = update.callback_query
    ft_instance = FindText(update, context)
    purchase_id = query.data.replace('vpn_my_service_detail__', '')

    try:
        with SessionLocal() as session:
            with session.begin():
                purchase = vpn_crud.get_purchase(session, purchase_id)
                if not purchase:
                    return await query.answer(await ft_instance.find_text('no_service_available'), show_alert=True)

                main_server = purchase.product.main_server
                get_from_server = await marzban_api.get_user(main_server.server_ip, purchase.username)
                expire_date = human_readable(datetime.fromtimestamp(get_from_server.get('expire')), await ft_instance.find_user_language())
                used_traffic = round(get_from_server.get('used_traffic') / (1024 ** 3), 2)
                data_limit = int(get_from_server.get('data_limit') / (1024 ** 3))
                subscribe_link = f"{main_server.server_protocol}{main_server.server_ip}:{main_server.server_port}{get_from_server.get('subscription_url')}"

                service_status = {
                    'active': await ft_instance.find_text('vpn_service_active'),
                    'inactive': await ft_instance.find_text('vpn_service_inactive')
                }

                text = (
                    f"<b>{await ft_instance.find_text('vpn_selected_service_info')}</b>"
                    f"\n\n{await ft_instance.find_text('vpn_service_name')} {purchase.username}"
                    f"\n{await ft_instance.find_text('vpn_service_status')} {service_status.get(get_from_server.get('status'))}"
                    f"\n{await ft_instance.find_text('vpn_expire_date')} {expire_date}"
                    f"\n{await ft_instance.find_text('vpn_traffic_use')} {used_traffic}/{data_limit}GB"
                    f"\n\n{await ft_instance.find_text('vpn_subsrciption_address')}"
                    f"\n\n<code>{subscribe_link}</code>"
                )

                keyboard = [
                    [InlineKeyboardButton(await ft_instance.find_keyboard('vpn_upgrade_service'), callback_data=f'vpn_upgrade_service__30__40__{purchase_id}')],
                    [InlineKeyboardButton(await ft_instance.find_keyboard('refresh'), callback_data=f'vpn_my_service_detail__{purchase_id}'),
                     InlineKeyboardButton(await ft_instance.find_keyboard('vpn_remove_service'), callback_data=f'vpn_remove_service__{purchase_id}')],
                    [InlineKeyboardButton(await ft_instance.find_keyboard('back_button'), callback_data='vpn_my_services')]
                ]

                await query.edit_message_text(text=text, parse_mode='html', reply_markup=InlineKeyboardMarkup(keyboard))

    except requests.exceptions.HTTPError as e:
        if '404 Client Error' in str(e):
            return await query.answer(await ft_instance.find_text('vpn_service_not_exit_in_server'), show_alert=True)
        raise e

    except Exception as e:
        raise e

