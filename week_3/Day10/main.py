from fastapi  import FastAPI
from services.message_service import get_message

app = FastAPI()

@app.get("/")
async def root():
    return {"message": get_message()}