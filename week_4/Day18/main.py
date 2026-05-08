from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta

app = FastAPI()

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_user = {
    "username": "prachi",
    "password": "1234"
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# create jwt token

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(
        to_encode, SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt

# login endpoint
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if (form_data.username != fake_user["username"] or form_data.password != fake_user["password"]):
        raise HTTPException(
            status_code=401, detail="Invalid username or password"
        )
    access_token = create_access_token(data={"sub":form_data.username})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
    
# protected route
@app.get("/protected")
async def protected_route(
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        username = payload.get("sub")
        return {
            "message": f"Welcome {username}"
        }
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Invalid or expired token"
        )