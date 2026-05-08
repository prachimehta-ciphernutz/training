from sqlalchemy import Column, Integer, String
from database import Base

# ORM Model
class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)

