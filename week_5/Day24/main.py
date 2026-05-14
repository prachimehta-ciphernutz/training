from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer

app = FastAPI()
model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="documents")

class TextData(BaseModel):
    id: str
    text: str

class QueryData(BaseModel):
    query: str

# store embeddings
@app.post("/store")
async def store_text(data: TextData):
    embedding = model.encode(data.text).tolist()
    collection.add(
        ids = [data.id],
        documents = [data.text],
        embeddings = [embedding]
    )
    return {"message": "Text stored successfully"}

# query nearest neighbors
@app.post("/search")
async def search_text(data: QueryData):
    query_embedding = model.encode(data.query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=2
    )
    return results