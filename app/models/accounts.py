from sqlalchemy import Column, String, Float, ForeignKey
from app.models.base_model import BaseModel, BaseInit


class AccountModel(BaseInit):
    __tablename__ = 'accounts'

    account_id = Column(String, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=False)
    risk = Column(Float, nullable=False, default=0.0)