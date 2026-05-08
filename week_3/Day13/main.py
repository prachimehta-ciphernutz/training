from fastapi import FastAPI, Request
import time
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)

@app.middleware("http")
async def middleware(request:Request, call_next):
    start_time = time.perf_counter()

    logging.info(f"Request: {request.method} {request.url}")

    response = await call_next(request)

    process_time = time.perf_counter() - start_time

    logging.info(f"Response: {response.status_code} | Time: {process_time:.4f}s")

    response.headers["X-Process-Time"] = str(round(process_time, 4))

    return response

@app.get("/")
async def root():
    return {"msg": "hello"}