from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
import logging
from tenacity import retry, stop_after_attempt, wait_fixed
from langchain_google_genai import ChatGoogleGenerativeAI

from app.rag import (
    process_pdf,
    get_similar_chunks
)
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer
from app.schemas import UserCreate, UserLogin, ChatReq, ConversationCreate
from app.auth import hash_password, verify_password, create_access_token
from app.database import engine, SessionLocal, Base
from app.models import User, Conversation, Message
from app.logger import logger
import shutil
import os
from app.redis_cache import set_cache, get_cache

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request 
from fastapi.responses import JSONResponse

load_dotenv()
Base.metadata.create_all(bind=engine)
app = FastAPI()

limiter = Limiter(
    key_func=get_remote_address
)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
logger.info("Rate limiter initialized")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
logger.info("Upload directory ready")

# gemini model
primary_llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

fallback_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
logger.info("LLM model initialized")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2)
)

def call_primary_llm(prompt):
    logger.info("Calling primary Gemini model")
    return primary_llm.stream(prompt)

#global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):

    logger.error(
        f"Unhandled exception: {str(exc)}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "message":
            "Internal Server Error"
        }
    )

#rate limit exception
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(
    request: Request,
    exc: RateLimitExceeded
):
    logger.warning("Rate limit exceeded")
    return JSONResponse(
        status_code=429,
        content={
            "message": "Too many requests. Try again later."
        }
    )

# request model

@app.get("/")
def home():
    logger.info("Home endpoint called")
    return {"message": "API running"}

@app.post("/register")
@limiter.limit("3/minute")
def register(request: Request, user: UserCreate):
    logger.info(f"Register request: {user.username}")
    db: Session = SessionLocal()
    
    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user:
        logger.warning("User already exists")
        raise HTTPException(
            status_code=400,
            detail="user already exists"
        )
    new_user = User(
        username=user.username,
        password = hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    logger.info(f"User registered: {user.username}")
    return {"message": "User registered successfully"}

@app.post("/login")
@limiter.limit("5/minute")
def login(request: Request, user: UserLogin):
    logger.info(f"Login request: {user.username}")

    db: Session = SessionLocal()
    db_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if not db_user:
        logger.warning("Invalid username")

        raise HTTPException(
            status_code=400,
            detail="Invalid username"
        )
    
    if not verify_password(
        user.password,
        db_user.password
    ):
        logger.warning("Invalid password")
        raise HTTPException(
            status_code=400, detail="Invalid password"
        )
    token = create_access_token(
        {"sub": db_user.username}
    )
    logger.info(f"Login successful: {user.username}")
    return {
        "access_token": token
    }

@app.post("/upload")
@limiter.limit("2/minute")
def upload_file(request: Request, file: UploadFile = File(...)):
    logger.info(f"Upload request: {file.filename}")
    
    try:
        file_path = f"{UPLOAD_DIR}/{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info("PDF saved successfully")
        process_pdf(file_path)

        logger.info("PDF processed successfully")

        return {"message": "PDF uploaded successfully"}

    except Exception as e:
        logger.error(
            f"PDF upload failed: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail=str(e)
        )

def generate_answer(question, context):
    logger.info("Generating streamed answer")

    prompt = f"""
    Answer the question based on the context.

    Context:
    {context}

    Question:
    {question}
    """

    stream = primary_llm.stream(prompt)

    full_response = ""

    for chunk in stream:

        # extract only text
        text = ""

        if hasattr(chunk, "content"):
            text = chunk.content

        elif isinstance(chunk, dict):
            text = chunk.get("text", "")

        # if content is list
        if isinstance(text, list):
            text = "".join(
                item.get("text", "")
                for item in text
                if isinstance(item, dict)
            )

        full_response += text

        yield text
    
    logger.info("Streaming completed")

    return full_response

@app.post("/conversation")
def create_conversation(request: Request, req: ConversationCreate):
    logger.info(f"Creting conversation: {req.title}")

    db = SessionLocal()
    new_conversation = Conversation(
        title = req.title
    )
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    logger.info(f"Conversation created ID: {new_conversation.id}")

    return {
        "conversation_id": new_conversation.id,
        "title": new_conversation.title
    }

@app.post("/chat")
@limiter.limit("5/minute")
def chat(request: Request, req: ChatReq):
    logger.info(f"Chat request: {req.question}")

    db: Session = SessionLocal()

    # normalize question
    normalized_question = req.question.strip().lower()

    cache_key = f"chat:{normalized_question}"

    # check cache first
    cached_response = get_cache(cache_key)

    if cached_response:
        logger.info("CACHE HIT")

        def cached_generator():
            yield cached_response

        return StreamingResponse(
            cached_generator(),
            media_type="text/plain"
        )

    logger.info("CACHE MISS")

    context = get_similar_chunks(
        req.question
    )

    logger.info("Retrieved similar chunks")

    input_tokens = len(
        req.question.split()
    )

    conversation = db.query(
        Conversation
    ).filter(
        Conversation.id == req.conversation_id
    ).first()

    if not conversation:
        logger.warning("Conversation not found")
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )
    logger.info("Conversation verified")

    user_message = Message(
        role="user",
        content=req.question,
        input_tokens=input_tokens,
        output_tokens=0,
        total_cost=0,
        conversation_id=req.conversation_id
    )

    db.add(user_message)
    db.commit()
    logger.info("User message stored")

    def response_generator():

        assistant_response = ""

        try:
            logger.info("Using primary model")

            response = call_primary_llm(
                f"""
                Context: {context}
                Question: {req.question}
                """
            )
        except Exception as e:
            logger.warning(
                f"Primary model failed: {str(e)}"
            )
            logger.info("Using fallback model")

            response = fallback_llm.stream(
                f"""
                Context: {context}
                Question: {req.question}
                """
            )

        for chunk in response:

            chunk_text = ""

            if isinstance(chunk.content, list):

                for item in chunk.content:

                    if isinstance(item, dict):
                        chunk_text += item.get(
                            "text", ""
                        )

                    elif hasattr(item, "text"):
                        chunk_text += item.text

                    else:
                        chunk_text += str(item)

            else:
                chunk_text = str(
                    chunk.content
                )

            assistant_response += chunk_text

            yield chunk_text

        logger.info("Streaming response completed")
        # save in redis cache
        set_cache(
            cache_key,
            assistant_response
        )

        logger.info("Response stored in Redis")

        output_tokens = len(
            assistant_response.split()
        )

        total_cost = (
            (input_tokens * 0.000001)
            +
            (output_tokens * 0.000002)
        )

        assistant_message = Message(
            role="assistant",
            content=assistant_response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_cost=total_cost,
            conversation_id=req.conversation_id
        )

        db.add(assistant_message)
        db.commit()

        logger.info(
            "Assistant message stored"
        )
        logger.info(
            f"Total Cost: {total_cost}"
        )

    return StreamingResponse(
        response_generator(),
        media_type="text/plain"
    )