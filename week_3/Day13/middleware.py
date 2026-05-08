from fastapi import FastAPI, Request
import time
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)

@app.middleware("http")
async def middleware(request:Request, call_next):
    start_time = time.time()
    logging.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    process_time = time.time() - start_time
    logging.info(f"Response: {response.status_code} | Time: {process_time: .4f}s")
    return response