from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
from jose import jwt
from datetime import datetime, timedelta
import os
import hashlib
from app.logger import logger 

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)
logger.info("Auth module loaded")

# convert long password into fixed hash
def safe_password(password: str):

    logger.info("Convertin password into SHA256 hash")
    return hashlib.sha256(
        password.encode()
    ).hexdigest()

def hash_password(password):

    logger.info("Hashing password")
    
    password = safe_password(password)
    hashed_password = pwd_context.hash(password)

    logger.info("Password hased successfully")

    return pwd_context.hash(password)

def verify_password(plain, hashed):

    logger.info("Verify password")

    plain = safe_password(plain)
    result = pwd_context.verify(plain, hashed)

    if result:
        logger.info("Password verification successful")
    else:
        logger.info("Password verification failed")

    return result 

def create_access_token(data: dict):

    logger.info("Creating access token")
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)

    to_encode.update({
        "exp": expire
    })

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    logger.info("Access token created successfully")
    return token