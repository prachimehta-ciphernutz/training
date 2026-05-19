from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load 
load_dotenv()

# Configure API key
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Load model
model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")

app = FastAPI()

class TextInput(BaseModel):
    text: str


@app.post("/summarize")
async def summarize_text(data: TextInput):

    prompt = f"""
    Summarize this text in simple language:

    {data.text}
    """

    response = model.generate_content(prompt)

    return {
        "summary": response.text
    }