from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os

app = FastAPI()

model = SentenceTransformer("all-MiniLM-L6-v2")
DATA_FILE = "stored_data.json"

class TextInput(BaseModel):
    text: str

@app.post("/store")
async def store_text(data: TextInput):
    embedding = model.encode(data.text).tolist()
    with open(DATA_FILE, "r") as file:
        stored_data = json.load(file)
    
    stored_data.append({
        "text": data.text,
        "embedding": embedding
    })

    with open(DATA_FILE, "w") as file:
        json.dump(stored_data, file, indent=4)

    return {"message": "Text stored successfully"}

# similarity search
@app.post("/search")
async def search_similarity(data: TextInput):
    query_embedding = model.encode(data.text)

    with open(DATA_FILE, "r") as file:
        stored_data = json.load(file)

    best_score = -1
    best_match = "" 

    for item in stored_data:
        stored_embeddings = [item["embedding"]]
        score = cosine_similarity(
            [query_embedding],
            stored_embeddings
        )[0][0]

        if score > best_score:
            best_score = score
            best_match = item["text"]

    return {
        "query": data.text,
        "most_similar_text": best_match,
        "similarity_score": float(best_score)
    }