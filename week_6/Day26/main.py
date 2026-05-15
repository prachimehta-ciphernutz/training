import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

app = FastAPI()

# gemini model object
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

class TopicReq(BaseModel):
    topic: str

class QueReq(BaseModel):
    question: str

# simple llm chain
simple_prompt = PromptTemplate(
    input_variables=["topic"],
    template="""
Explain {topic} in simple words.
"""
)
simple_chain = (
    simple_prompt
    | llm
    | StrOutputParser()
)

#multi step reasoning chain
# step - 1 -> analyze question

analysis_prompt = PromptTemplate(
    input_variables=["question"],
    template="""
Analyze the following question carefully.

Question:
{question}

Break it into smaller reasoning steps.
"""
)

analysis_chain = (
    analysis_prompt 
    | llm 
    | StrOutputParser()
)

# step - 2 -> generate final answer
answer_prompt = PromptTemplate(
    input_variables=["question", "analysis"],
    template="""
You are an intelligent AI assistant.

Question:
{question}

Reasoning steps:
{analysis}

Generate a detailed final answer.
"""
)

answer_chain = (
    answer_prompt
    | llm
    | StrOutputParser()
)

# routes

@app.get("/")
def home():
    return {
        "message": "LangChain chains running"
    }

# simple chain api

@app.post("/simple-chain")
def simple_chain_api(request: TopicReq):
    response = simple_chain.invoke({
        "topic": request.topic
    })

    return {
        "topic": request.topic,
        "response": response
    }

# multi step chain api

@app.post("/reasoning-chain")
def reasoning_chain_api(request: QueReq):

    # Step 1
    analysis = analysis_chain.invoke({
        "question": request.question
    })

    # Step 2
    final_answer = answer_chain.invoke({
        "question": request.question,
        "analysis": analysis
    })

    return {
        "question": request.question,
        "reasoning_steps": analysis,
        "final_answer": final_answer
    }