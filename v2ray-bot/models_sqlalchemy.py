from database_sqlalchemy import Base
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime

class UserDetail(Base):
    __tablename__ = 'UserDetail'

    user_id = Column(Integer, primary_key=True)
    status = Column(String, default="active")
    email = Column(String, unique=True, default=None)
    phone_number = Column(BigInteger, unique=True, default=None)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String, unique=True)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    language = Column(String, default='fa')
    traffic = Column(Integer, default=1)
    period = Column(Integer, default=1)
    free_service = Column(Boolean, default=False)
    notification_gb = Column(Integer, default=85)
    notification_day = Column(Integer, default=3)
    wallet = Column(Integer, default=0)
    notification_wallet = Column(Integer, default=5000)
    notif_wallet = Column(Integer, default=0)
    notif_low_wallet = Column(Integer, default=0)
    invited_by = Column(Integer, nullable=True, default=None)
    register_date = Column(DateTime, default=datetime.now())

    financial_reports = relationship("FinancialReport", back_populates="owner")


class FinancialReport(Base):
    __tablename__ = 'FinancialReport'

    financial_id = Column(Integer, primary_key=True)
    operation = Column(String, default='spend')
    value = Column(Integer)
    detail = Column(String)
    register_date = Column(DateTime, default=datetime.now())

    chat_id = Column(BigInteger, ForeignKey('UserDetail.chat_id'))
    owner = relationship("UserDetail", back_populates="financial_reports")

