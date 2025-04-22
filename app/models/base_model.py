from sqlalchemy import Column, Integer


class BaseModel:
    id = Column(Integer, primary_key=True, index=True)