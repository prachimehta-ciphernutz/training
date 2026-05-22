from dotenv import load_dotenv
import os
import uuid

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings
)
from langchain_chroma import Chroma
from app.redis_cache import get_cache, set_cache
from app.logger import logger

load_dotenv()

# embedding model
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

CHROMA_PATH = "chroma_db"

# process pdf
def process_pdf(file_path):
    
    try: 
        # load pdf
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        logger.info(f"Loaded {len(docs)} pages from PDF")

        # split text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=50
        )

        split_docs = text_splitter.split_documents(docs)
        logger.info(f"Created {len(split_docs)} chunks")

        # extract only text
        texts = []

        for doc in split_docs:
            text = doc.page_content.strip()
            if text:
                texts.append(text)

        if len(texts) == 0:
            logger.warning("No valid text found in PDF")
            return
        
        ids = [
            str(uuid.uuid4())
            for _ in range(len(texts))
        ]

        Chroma.from_texts(
            texts=texts,
            embedding=embedding_model,
            ids=ids,
            persist_directory=CHROMA_PATH
        )
        logger.info("Embeddings stored in ChromaDB successfully")
    
    except Exception as e:
        logger.error(f"Error while processing PDF: {str(e)}")
        raise e

# retrieve similar chunks
def get_similar_chunks(query):

    try: 
        logger.info(f"Searching similar chunk for query: {query}")
        normalized_query = query.strip().lower()
        cache_key = f"embedding: {normalized_query}"

        cached_context = get_cache(cache_key)
        
        if cached_context:
            logger.info("Embedding Cache hit")
            return cached_context
        
        logger.info("Embedding cache miss")

        vectorstore = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embedding_model
        )

        docs = vectorstore.similarity_search(
            query,
            k=3
        )

        logger.info(f"Retrieved {len(docs)} similar chunks")

        context = "\n".join(
            [doc.page_content for doc in docs]
        )

        # save in redis
        set_cache(cache_key, context)
        logger.info("Context cached successfully")
        
        return context
    
    except Exception as e:
        logger.error(
            f"Error during similarity search: {str(e)}"
        )
        return ""
