from datetime import datetime
from os import path

from sqlalchemy import Column, Date, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from const import DATABASE_URI

sqlite_db = 'sqlite:///' + path.join(DATABASE_URI)
engine = create_engine(sqlite_db, echo=True)
# connect_args = {'check_same_thread': False}
session = Session(bind=engine)
BaseModel = declarative_base()


class Stock(BaseModel):
    __tablename__ = 'stock'
    id = Column(Integer(), primary_key=True)
    company_name = Column(String(), nullable=False)
    end_date = Column(Date(), nullable=False)
    investment_id = Column(Integer(), nullable=False)
    issued_by = Column(String(), nullable=False)
    nep_end_date = Column(Date(), nullable=False)
    nep_start_date = Column(Date(), nullable=False)
    pdf = Column(String(), nullable=True)
    ratio = Column(String(), nullable=True)
    start_date = Column(Date(), nullable=False)
    stock_id = Column(Integer(), nullable=False)
    stock_symbol = Column(String(), nullable=False)
    stock_type = Column(String(), nullable=False)
    units = Column(String(), nullable=False)
    stock_added_at = Column(DateTime(), default=datetime.utcnow)


# To create database with given model if it doesn't exists
if not path.isfile(DATABASE_URI):
    BaseModel.metadata.create_all(engine)
