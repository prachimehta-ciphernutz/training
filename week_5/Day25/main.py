import os
import chromadb
import google.generativeai as genai
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI()
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name = "manual_rag"
)

class QueryReq(BaseModel):
    question: str

# chunking
def chunk_text(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks

# embedding generation
def generate_embedding(text):
    response = genai.embed_content(
        model="models/gemini-embedding-2-preview",
        content=text
    )
    return response["embedding"]

# document ingestion
def ingest_document():
    with open("documents.txt", "r", encoding="utf-8") as file:
        text = file.read()
    existing_data = collection.get()

    if existing_data["ids"]:
        collection.delete(ids=existing_data["ids"])

    chunks = chunk_text(text)

    for index, chunk in enumerate(chunks):
        embedding = generate_embedding(chunk)

        collection.add(
            ids=[f"chunk_{index}"],
            documents=[chunk],
            embeddings=[embedding]
        )
    return len(chunks)

# retrieval
def retrieve_context(query, top_k=3):
    query_embedding = generate_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results["documents"][0]
    context = "\n".join(documents)
    return context

# answer generation
def generate_answer(question):
    context = retrieve_context(question)
    prompt = f"""
You are a helpful AI assistant.

Answer ONLY from the provided context.

Context:
{context}

Question:
{question}
"""
    model = genai.GenerativeModel("gemini-3-flash-preview")
    response = model.generate_content(prompt)

    return response.text

# routes
@app.get("/")
def home():
    return {"message": "Manual RAG system running"}

@app.post("/ingest")
def ingest():
    total_chunks = ingest_document()

    return {
        "message": "documents.txt ingested successfully",
        "chunks_stored": total_chunks
    }

@app.post("/ask")
def ask_question(request: QueryReq):
    answer = generate_answer(request.question)
    
    return {
        "question": request.question,
        "answer": answer
    } 