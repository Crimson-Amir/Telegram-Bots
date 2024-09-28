from database_sqlalchemy import Base
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime, BigInteger, ARRAY, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

class UserDetail(Base):
    __tablename__ = 'UserDetail'

    user_id = Column(Integer, primary_key=True)
    user_level = Column(Integer, default=1)
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
    services = relationship("Purchased", back_populates="owner")


class FinancialReport(Base):
    __tablename__ = 'FinancialReport'

    financial_id = Column(Integer, primary_key=True)
    active = Column(Boolean, default=False)
    operation = Column(String, default='spend')
    value = Column(Integer)
    action = Column(String)
    service_id = Column(Integer)
    register_date = Column(DateTime, default=datetime.now())

    chat_id = Column(BigInteger, ForeignKey('UserDetail.chat_id'))
    owner = relationship("UserDetail", back_populates="financial_reports")


class Server(Base):
    __tablename__ = 'Server'
    server_id = Column(Integer, primary_key=True)
    active = Column(Boolean)

    server_ip = Column(String)
    # server_protocol = Column(String)
    server_port = Column(Integer)
    server_user_name = Column(String)
    server_password = Column(String)

    country = Column(String)
    flag = Column(String)
    connected_iran_server_ips = Column(ARRAY(String))

    product_associations = relationship("ServerProductAssociations", back_populates="server", cascade="all, delete-orphan")

class ServerProductAssociations(Base):
    __tablename__ = 'ServerProductAssociations'
    server_id = Column(Integer, ForeignKey('Server.server_id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('Product.product_id', ondelete='CASCADE'), primary_key=True)

    product = relationship("Product", back_populates="server_associations")
    server = relationship("Server", back_populates="product_associations")

class Product(Base):
    __tablename__ = 'Product'

    product_id = Column(Integer, primary_key=True)
    inbound_id = Column(ARRAY(Integer))
    active = Column(Boolean)
    product_name = Column(String)

    vpn_server = Column(JSON) # {1.1.1.1: [human.ggkala.shop, service.freebyte.click], 2.2.2.2: [human.ggkala.shop, service.freebyte.click], 2.2.3.2: [human.ggkala.shop, service.freebyte.click]}
    sub_web_app_endpoint = Column(String)

    inbound_host = Column(String)
    inbound_header_type = Column(String)

    register_date = Column(DateTime, default=datetime.now())
    purchaseds = relationship("Purchased", back_populates="product")

    server_associations = relationship("ServerProductAssociations", back_populates="product", cascade="all, delete-orphan")


class Purchased(Base):
    __tablename__ = 'Purchased'

    purchased_id = Column(Integer, primary_key=True)
    active = Column(Boolean)

    inbound_id = Column(Integer)

    client_email = Column(String)
    client_id = Column(String)
    traffic = Column(Integer)
    period = Column(Integer)

    notif_day = Column(Boolean, default=False)
    notif_gb = Column(Boolean, default=False)
    auto_renewal = Column(Boolean, default=False)

    token = Column(String)
    vpn_server = Column(ARRAY(String))
    client_addresses = Column(String)

    product_id = Column(Integer, ForeignKey('Product.product_id'))
    product = relationship("Product", back_populates="purchaseds")

    chat_id = Column(BigInteger, ForeignKey('UserDetail.chat_id'))
    owner = relationship("UserDetail", back_populates="services")

    register_date = Column(DateTime, default=datetime.now())
