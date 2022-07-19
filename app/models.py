from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from .database import Base

class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, nullable=False)
    date_joined = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone_number = Column(String(length=10), nullable=False)
    password = Column(String, nullable=False)
    address = Column(String, nullable=False)