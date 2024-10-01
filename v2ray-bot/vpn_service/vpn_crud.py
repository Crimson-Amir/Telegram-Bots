import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import models_sqlalchemy as model
from database_sqlalchemy import SessionLocal

def get_purchase(session, purchase_id):
    return session.query(model.Purchase).filter_by(purchase_id=purchase_id).first()


def get_all_main_servers():
    with SessionLocal() as session:
        with session.begin():
            return session.query(model.MainServer).where(model.MainServer.active==True).all()
