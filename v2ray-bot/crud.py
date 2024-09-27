from database_sqlalchemy import SessionLocal
import models_sqlalchemy as model
import logging

def get_user_language(user_id):
    session = SessionLocal()
    try:
        return session.query(model.UserDetail).where(model.UserDetail.chat_id == user_id).first()
    finally:
        session.close()


def create_user(user_detail, inviter_user_id, selected_language):
    session = SessionLocal()
    try:
        user = model.UserDetail(
            first_name=user_detail.first_name,
            last_name=user_detail.last_name,
            username=user_detail.username,
            chat_id=user_detail.id,
            invited_by=inviter_user_id,
            language = selected_language
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    finally:
        session.close()
