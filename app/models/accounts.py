from sqlalchemy import Column, String, ForeignKey
from app.models.base_model import BaseModel, BaseInit


class Account(BaseModel, BaseInit):
    __tablename__ = 'accounts'
    account_id = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=False)