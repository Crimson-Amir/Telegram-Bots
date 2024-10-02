import sys, os, pytz
from datetime import datetime
from sqlalchemy import update
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import models_sqlalchemy as model

def get_purchase(session, purchase_id):
    return session.query(model.Purchase).filter_by(purchase_id=purchase_id).first()


def update_purchase(session, purchase_id:int, **kwargs):
    stmt = (
        update(model.Purchase)
        .where(model.Purchase.purchase_id == purchase_id)
        .values(
            register_date=datetime.now(pytz.timezone('Asia/Tehran')),
            day_notification_stats=False,
            traffic_notification_stats=False,
            active=True,
            **kwargs
        )
    )
    session.execute(stmt)


def get_all_main_servers(session):
    with session.begin():
        return session.query(model.MainServer).where(model.MainServer.active==True).all()
