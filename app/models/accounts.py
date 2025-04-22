from sqlalchemy import Column, String, ForeignKey
from app.models.base_model import BaseModel


class Account(BaseModel):
    __tablename__ = 'accounts'

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=False)