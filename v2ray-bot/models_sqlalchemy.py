from database_sqlalchemy import Base
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime, BigInteger, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime

class UserDetail(Base):
    __tablename__ = 'UserDetail'

    user_id = Column(Integer, primary_key=True)
    user_level = Column(Integer, default=1)
    status = Column(String, default="active")

    email = Column(String, unique=True, default=None)
    phone_number = Column(String, unique=True, default=None)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String, unique=True)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    language = Column(String, default='fa')
    free_service = Column(Boolean, default=False)
    wallet = Column(Integer, default=0)
    invited_by = Column(BigInteger, ForeignKey('UserDetail.chat_id'))
    register_date = Column(DateTime, default=datetime.now())

    financial_reports = relationship("FinancialReport", back_populates="owner")
    services = relationship("Purchase", back_populates="owner")


class FinancialReport(Base):
    __tablename__ = 'FinancialReport'

    financial_id = Column(Integer, primary_key=True)
    operation = Column(String, default='spend')

    amount = Column(Integer, nullable=False)
    action = Column(String, nullable=False)
    id_holder = Column(Integer)

    payment_getway = Column(String)
    authority = Column(String)
    currency = Column(String)
    url_callback = Column(String)
    additional_data = Column(String)
    payment_status = Column(String)

    register_date = Column(DateTime, default=datetime.now())

    chat_id = Column(BigInteger, ForeignKey('UserDetail.chat_id'))
    owner = relationship("UserDetail", back_populates="financial_reports")


class MainServer(Base):
    __tablename__ = 'MainServer'
    server_id = Column(Integer, primary_key=True)
    active = Column(Boolean)
    server_ip = Column(String)
    server_protocol = Column(String)
    server_port = Column(Integer)
    server_username = Column(String)
    server_password = Column(String)
    products = relationship("Product", back_populates="main_server")

class Product(Base):
    __tablename__ = 'Product'

    product_id = Column(Integer, primary_key=True)
    active = Column(Boolean)
    product_name = Column(String)
    register_date = Column(DateTime, default=datetime.now())
    purchase = relationship("Purchase", back_populates="product")

    main_server_id = Column(Integer, ForeignKey('MainServer.server_id'))
    main_server = relationship("MainServer", back_populates="products")


class Purchase(Base):
    __tablename__ = 'Purchase'

    purchase_id = Column(Integer, primary_key=True)
    username = Column(String)
    active = Column(Boolean)
    traffic = Column(Integer)
    period = Column(Integer)
    day_notification_stats = Column(Boolean, default=False)
    traffic_notification_stats = Column(Boolean, default=False)
    subscription_url = Column(String)

    upgrade_traffic = Column(Integer, default=1)
    upgrade_period = Column(Integer, default=1)

    product_id = Column(Integer, ForeignKey('Product.product_id'))
    product = relationship("Product", back_populates="purchase")
    chat_id = Column(BigInteger, ForeignKey('UserDetail.chat_id'))
    owner = relationship("UserDetail", back_populates="services")

    register_date = Column(DateTime, default=datetime.now())


class Statistics(Base):
    __tablename__ = 'Statistics'

    statistics_id = Column(Integer, primary_key=True)
    traffic_usage = Column(String)
    data = Column(String)

    register_date = Column(DateTime, default=datetime.now())

class LastUsage(Base):
    __tablename__ = 'Last_usage'

    last_usage_id = Column(Integer, primary_key=True)
    last_usage = Column(String)
    data = Column(String)

    register_date = Column(DateTime, default=datetime.now())
