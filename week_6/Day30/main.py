import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import RetrievalQA

load_dotenv()
app = FastAPI()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# embedding model
embed_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-2-preview",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

loader = TextLoader("documents.txt")
documents=loader.load()

# chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

docs = text_splitter.split_documents(documents)

# chroma vectordatabase
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embed_model,
    persist_directory="chroma_db"
)

# retriever
retriever = vectorstore.as_retriever()

# RAG chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff"
)

class QueReq(BaseModel):
    question: str

# routes
@app.get("/")
def home():
    return {"message": "LangChain RAG running"}

@app.post("/ask")
def ask_question(request: QueReq):
    response = qa_chain.invoke({
        "query": request.question
    })
    return {
        "question": request.question,
        "answer": response["result"]
    }