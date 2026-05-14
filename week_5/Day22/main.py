from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import json
import os

app = FastAPI()

# load embedding model
model = SentenceTransformer("all-MiniLM-L6-V2")

# req body
class TextInput(BaseModel):
    text: str

@app.post("/generate-embedding")
async def generate(data: TextInput):
    embedding = model.encode(data.text)
    embedding_list = embedding.tolist()

    record = {
        "text": data.text,
        "embedding": embedding_list
    }

    filename = "embeddings.json"

    if os.path.exists(filename):
        with open(filename, "r") as file:
            existing_data = json.load(file)
    else:
        existing_data = []

    existing_data.append(record)

    with open (filename, "w") as file:
        json.dump(existing_data, file, indent=4)

    return {
        "message": "Embeddin generated and stored successfully",
        "embedding_dim": len(embedding_list)
    }