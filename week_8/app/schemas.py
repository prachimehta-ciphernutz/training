from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class ConversationCreate(BaseModel):
    title: str

class ChatReq(BaseModel):
    question: str
    conversation_id: int