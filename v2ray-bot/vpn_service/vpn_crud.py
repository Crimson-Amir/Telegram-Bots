import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import models_sqlalchemy as model

def get_purchased(session, purchased_id):
    return session.query(model.Purchased).filter_by(purchased_id=purchased_id).first()