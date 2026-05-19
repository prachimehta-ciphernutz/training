from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey
)
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    relationship
)
from dotenv import load_dotenv
import os

# load env variables
load_dotenv()

# database url
DATABASE_URL = (
    f"postgresql://{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}/"
    f"{os.getenv('DB_NAME')}"
)

# database setup
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

app = FastAPI()

# database models

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)

    messages = relationship(
        "Message",
        back_populates="conversation"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String)
    content = Column(String)

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id")
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )


# create tables
Base.metadata.create_all(bind=engine)


# REQUEST MODEL

class ChatRequest(BaseModel):
    conversation_id: int
    role: str
    content: str


# CREATE CONVERSATION

@app.post("/conversation")
def create_conversation():

    db = SessionLocal()

    conversation = Conversation(
        title="New Chat"
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    db.close()

    return {
        "conversation_id": conversation.id
    }


# SAVE MESSAGE

@app.post("/chat")
def save_message(req: ChatRequest):

    db = SessionLocal()

    message = Message(
        role=req.role,
        content=req.content,
        conversation_id=req.conversation_id
    )

    db.add(message)
    db.commit()

    db.close()

    return {
        "message": "Chat saved successfully"
    }


# GET CHAT HISTORY

@app.get("/history/{conversation_id}")
def get_history(conversation_id: int):

    db = SessionLocal()

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).all()

    chat_history = []

    for message in messages:
        chat_history.append({
            "role": message.role,
            "content": message.content
        })

    db.close()

    return {
        "conversation_id": conversation_id,
        "messages": chat_history
    }