from sqlalchemy import Column, Integer
from sqlalchemy.orm import DeclarativeBase


class BaseInit(DeclarativeBase):
    pass


class BaseModel:
    id = Column(Integer, primary_key=True, index=True)