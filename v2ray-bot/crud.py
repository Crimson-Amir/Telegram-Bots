import logging

from database_sqlalchemy import SessionLocal
import models_sqlalchemy as model
from sqlalchemy import update, func, desc

def get_user(session, chat_id):
    return session.query(model.UserDetail).filter_by(chat_id=chat_id).first()

def get_financial_report_by_id(session, financial_id):
    return session.query(model.FinancialReport).where(model.FinancialReport.financial_id == financial_id).first()

def get_financial_report_by_authority(session, authority):
    return session.query(model.FinancialReport).where(model.FinancialReport.authority == authority).first()

def get_financial_reports(session, chat_id, limit=5, only_paid_financial=False):
    financial_reports = session.query(model.FinancialReport)
    if only_paid_financial:
        financial_reports = financial_reports.where(model.FinancialReport.payment_status == 'paid')
    financial_reports = financial_reports.filter_by(chat_id=chat_id).order_by(desc(model.FinancialReport.financial_id)).limit(limit).all()
    return financial_reports

def create_user(user_detail, inviter_user_id, selected_language):
    with SessionLocal() as session:
        with session.begin():
            user = model.UserDetail(
                first_name=user_detail.first_name,
                last_name=user_detail.last_name,
                username=user_detail.username,
                chat_id=user_detail.id,
                invited_by=inviter_user_id,
                language=selected_language
            )
            session.add(user)


def add_credit_to_wallet(session, financial_db, payment_status='paid'):
    user_id: int = financial_db.owner.chat_id

    stmt = (
        update(model.UserDetail)
        .where(model.UserDetail.chat_id == user_id)
        .values(
            wallet=func.coalesce(model.UserDetail.wallet, 0) + financial_db.amount
        )
    )
    session.execute(stmt)

    try:
        financial_id: int = financial_db.financial_id
        stmt_2 = (
            update(model.FinancialReport)
            .where(model.FinancialReport.financial_id == financial_id)
            .values(
                payment_status=payment_status
            )
        )
        session.execute(stmt_2)
    except Exception as e:
        logging.error(f'error in update financial_report in refund section! {e}')


def less_from_wallet(user_id: int, credit, operation, action, service_id=None):
    with SessionLocal() as session:
        with session.begin():
            stmt = (
                update(model.UserDetail)
                .where(model.UserDetail.chat_id == user_id)
                .values(
                    wallet=func.coalesce(model.UserDetail.wallet, 0) - credit
                )
            )
            record = model.FinancialReport(operation=operation, value=credit, chat_id=user_id, action=action, service_id=service_id)
            session.add(record)
            session.execute(stmt)


def update_financial_report(session, financial_id: int, payment_getway, authority, currency, url_callback, additional_data=None):
    stmt = (
        update(model.FinancialReport)
        .where(model.FinancialReport.financial_id == financial_id)
        .values(
            payment_getway=payment_getway,
            authority=authority,
            currency=currency,
            url_callback=url_callback,
            additional_data=additional_data
        )
    )

    session.execute(stmt)


def update_financial_report_status(session, financial_id: int, new_status):
    stmt = (
        update(model.FinancialReport)
        .where(model.FinancialReport.financial_id == financial_id)
        .values(
            payment_status = new_status
        )
    )

    session.execute(stmt)


def creatcreate_purchase(session, product_id, chat_id, traffic, period):
    purchase = model.Purchase(
        active=False,
        product_id=product_id,
        chat_id=chat_id,
        traffic=int(traffic),
        period=int(period)
    )
    session.add(purchase)
    session.flush()
    return purchase


def create_financial_report(session, operation, chat_id, amount, action, service_id, payment_status):
    financial = model.FinancialReport(
        operation=operation,
        amount=amount,
        chat_id=chat_id,
        action=action,
        id_holder=service_id,
        payment_status=payment_status
    )

    session.add(financial)
    session.flush()
    return financial
