import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import models_sqlalchemy as model

def get_purchase(session, purchase_id):
    return session.query(model.Purchase).filter_by(purchase_id=purchase_id).first()