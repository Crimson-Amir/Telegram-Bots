from database_sqlalchemy import SessionLocal
import models_sqlalchemy as model
from sqlalchemy import update, func, desc

def get_user(session, chat_id):
    return session.query(model.UserDetail).filter_by(chat_id=chat_id).first()


def get_financial_reports(session, chat_id, limit=5):
    return (session.query(model.FinancialReport).where(model.FinancialReport.active == True).
            filter_by(chat_id=chat_id).order_by(desc(model.FinancialReport.financial_id)).limit(limit).all())

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


def clear_wallet_notification(user_id: int):
    with SessionLocal() as session:
        with session.begin():
            stmt = (
                update(model.UserDetail)
                .where(model.UserDetail.chat_id == user_id)
                .values(notif_wallet=0, notif_low_wallet=0)
            )
            session.execute(stmt)

def add_financial_report(session, user_id: int, credit, operation, action, active, service_id=None):
    with session.begin():
        record = model.FinancialReport(operation=operation, value=credit, chat_id=user_id, action=action, service_id=service_id, active=active)
        session.add(record)
    return record

def add_credit_to_wallet(user_id: int, credit, operation, action, service_id=None):
    with SessionLocal() as session:
        with session.begin():
            stmt = (
                update(model.UserDetail)
                .where(model.UserDetail.chat_id == user_id)
                .values(
                    wallet=func.coalesce(model.UserDetail.wallet, 0) + credit,
                    notif_wallet=0,
                    notif_low_wallet=0
                )
            )
            record = model.FinancialReport(operation=operation, value=credit, chat_id=user_id, action=action, service_id=service_id, active=True)
            session.add(record)
            session.execute(stmt)

def less_from_wallet(user_id: int, credit, operation, action, service_id=None):
    with SessionLocal() as session:
        with session.begin():
            stmt = (
                update(model.UserDetail)
                .where(model.UserDetail.chat_id == user_id)
                .values(
                    wallet=func.coalesce(model.UserDetail.wallet, 0) - credit,
                    notif_wallet=0,
                    notif_low_wallet=0
                )
            )
            record = model.FinancialReport(operation=operation, value=credit, chat_id=user_id, action=action, service_id=service_id, active=True)
            session.add(record)
            session.execute(stmt)