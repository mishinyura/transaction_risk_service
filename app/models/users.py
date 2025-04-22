from sqlalchemy import Column, String, SecretStr

from app.models.base_model import BaseModel


class User(BaseModel):
    __tableName__ = 'users'

    username = Column(String, nullable=False, unique=True)
    password = Column(SecretStr, nullable=False)