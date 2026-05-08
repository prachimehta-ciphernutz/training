from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os

app = FastAPI()

# Allowed file types
ALLOWED_EXTENSIONS = {".jpg", ".png", ".pdf"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    _, extension = os.path.splitext(file.filename)

    if extension.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, detail = "Invalid filetype"
        )
    
    filepath = f"uploads/{file.filename}"

    #save file locally
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "File upload successfully",
        "filename": file.filename
    }


