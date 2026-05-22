from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.logger import logger
import os

load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DTABASE_URL not found in .env")
    raise ValueError("DATABASE_URL is missing")

logger.info("Database URL loaded successfully")

engine = create_engine(DATABASE_URL)
logger.info("SQLAlchemy engine created")

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
logger.info("SessionLocal initialized")

Base = declarative_base()

logger.info("Base model initialized")