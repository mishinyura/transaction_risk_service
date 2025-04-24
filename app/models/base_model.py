from sqlalchemy import Column, Integer
from sqlalchemy.orm import DeclarativeBase, declarative_base


# class BaseInit(DeclarativeBase):
#     pass


BaseInit = declarative_base()


class BaseModel:
    id = Column(Integer, primary_key=True, index=True)