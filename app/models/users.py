from sqlalchemy import Column, String

from app.models.base_model import BaseModel, BaseInit


class User(BaseModel, BaseInit):
    __tablename__ = 'users'

    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)