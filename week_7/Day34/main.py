from fastapi import FastAPI
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv  
import os

load_dotenv()
app = FastAPI()
 
llm = ChatGoogleGenerativeAI(
    model = "gemini-3.1-flash-lite",
    google_api_key = os.getenv("GOOGLE_API_KEY")
)

# token price eg.
INPUT_COST_PER_1K = 0.00035
OUTPUT_COST_PER_1K = 0.00105

class ChatReq(BaseModel):
    question: str

@app.post("/chat")
def chat(req: ChatReq):
    
    input_tokens = len(req.question.split())

    response = llm.invoke(req.question)
    answer = str(response.content)

    output_tokens = len(answer.split())

    total_tokens = input_tokens + output_tokens

    # cost calculation
    input_cost = (input_tokens / 1000) * INPUT_COST_PER_1K
    output_cost = (output_tokens / 1000) * OUTPUT_COST_PER_1K

    total_cost = input_cost + output_cost

    return {
        "question": req.question,
        "answer": answer,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "total_cost": round(total_cost, 6)
    }