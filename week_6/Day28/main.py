import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

load_dotenv()

app = FastAPI()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# memory
memory = ConversationBufferMemory()

# conversation chain
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# request model
class ChatReq(BaseModel):
    message: str

@app.get("/")
def home():
    return {"message": "Memory chatbot running"}

@app.post("/chat")
def chat(request: ChatReq):
    response = conversation.predict(
        input = request.message
    )

    return {
        "user_message": request.message,
        "ai_response": response
    }