from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__="users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)

class Conversation(Base):
    __tablename__="conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)

    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__="messages"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String)
    content = Column(String)

    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    
    total_cost = Column(Float)

    conversation_id = Column(
        Integer, ForeignKey("conversations.id")
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )
