from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import os

load_dotenv()
app = FastAPI()

# gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

class ChatReq(BaseModel):
    question: str

# streaming Generator
def generate_res(question):
    res = llm.stream(question)

    for chunk in res:
        if chunk.content:
            yield str(chunk.content)

# streaming endpoint
@app.post("/chat")
def chat(req:ChatReq):
    return StreamingResponse(
        generate_res(req.question),
        media_type="text/plain"
    )
