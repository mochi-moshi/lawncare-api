from sqlalchemy import Column, ForeignKey, Integer, Float, String
from sqlalchemy.sql.sqltypes import Date, TIMESTAMP, Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from .database import Base

class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, nullable=False)
    date_joined = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String(length=10), nullable=False)
    password = Column(String, nullable=False)
    address = Column(String, nullable=False)

class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True, nullable=False)
    date = Column(Date, nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=False)
    description = Column(String, server_default='', nullable=False)
    price = Column(Float, nullable=False)
    paid = Column(Boolean, server_default='f', nullable=False)

    client = relationship('Client')