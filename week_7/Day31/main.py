from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = TextLoader("documents.txt")
docs = loader.load()

# diff chunking experiments
chunk_setting = [
    {
        "chunk_size": 70,
        "chunk_overlap": 10
    },
    {
        "chunk_size": 100,
        "chunk_overlap": 20
    },
    {
        "chunk_size": 300,
        "chunk_overlap": 50 
    }
]

# test diff settings
for setting in chunk_setting:
    print("\n" + "=" * 60)
    print(f"Chunk Size: {setting['chunk_size']}")
    print(f"Chunk_overlap: {setting['chunk_overlap']}")
    print("=" * 60)
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = setting["chunk_size"],
        chunk_overlap = setting["chunk_overlap"]
    )
    chunks = splitter.split_documents(docs)
    print(f"\n Total chunks: {len(chunks)}\n")

    for index, chunk in enumerate(chunks):
        print(f"chunk {index + 1}: \n")
        print(chunk.page_content)
        print("\n" + "-" *50)
