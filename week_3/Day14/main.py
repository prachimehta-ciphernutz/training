from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

# global exception handler

@app.exception_handler(Exception)
async def global_exc_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "type": "InternalServerError",
                "message": str(exc)
            }
        }
    )


@app.exception_handler(HTTPException)
async def http_exc_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "type": "HTTPException",
                "message": exc.detail
            }
        }
    )

# test route

@app.get("/")
async def home():
    return {"success": True, "message": "API is working"}

# route with error

@app.get("/error")
async def error_route():
    raise HTTPException(status_code=404, details="Item not found")

@app.get("/crash")
async def crash():
    x = 1 / 0
    return x