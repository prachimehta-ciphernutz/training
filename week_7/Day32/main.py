import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()
loader = TextLoader("documents.txt")
documents = loader.load()

# chunking
splitter = RecursiveCharacterTextSplitter(
    chunk_size = 80,
    chunk_overlap = 30
)

chunks = splitter.split_documents(documents)

# embedding models

embed_models = {
    "Gemini Embedding":
        GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            google_api_key=os.getenv("GEMINI_API_KEY")
        ),
    "MiniLM Embedding":
        HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
}

# test que
query = "How do computers understand human language?"

# compare embedding models

for model_name, embed_model in embed_models.items():
    print("\n" + "=" * 60)
    print(f"Testing: {model_name}")
    print("=" * 60)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embed_model,
        collection_name=model_name.replace(" ", "_")
    )
    
    retriever = vectorstore.as_retriever(
        search_kwargs={"k":2}
    )

    results = retriever.invoke(query)
    print("\n Retrieved Chunks: \n")
    
    for index, result in enumerate(results):
        print(f"Chunk {index + 1}: \n")
        print(result.page_content)
        print("\n" + "-" * 50)