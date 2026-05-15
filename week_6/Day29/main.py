import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.tools import Tool

load_dotenv()

app = FastAPI()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# calculator tool
def calculator(expression: str):
    try:
        result = eval(expression)
        return str(result)
    except Exception:
        return "Invalid mathematical expression"

# tool object
calculator_tool = Tool( 
    name = "Calculator",
    func = calculator,
    description="""
Useful for solving mathematical calculations.
Example:
45 * 20
100 / 5
12 + 78 
"""
)

# agent
agent = initialize_agent(
    tools=[calculator_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

class QueReq(BaseModel):
    question: str

@app.get("/")
def home():
    return {"message": "tool calling agent running"}

@app.post("/ask")
def ask_agent(request: QueReq):
    response = agent.run(request.question)
    return {
        "question": request.question,
        "response": response
    }