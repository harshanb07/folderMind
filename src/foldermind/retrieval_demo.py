from pathlib import Path
import chromadb

from chunking import chunk_document

# Read our test file
path = Path("demo_data/foldermind_manufacturing_demo.txt")
text = path.read_text(encoding="utf-8")

# use our chunking function from chunking.py
chunks = chunk_document(text)

# Connect to a persistent local vector database
client = chromadb.PersistentClient(path="./chroma_db") 
# PersistentClient creates db that survives restasrting

collection = client.get_or_create_collection(
    name="foldermind_demo"
) #basically creates the db if not existent
#create_collection would raise an error if db exists

#at this point, the collection variable is basically an object for us
#using this object, we can store and query our document chunks...

# Index chunks
# upsert inserts new chunks 
# chroma generates embeddings (cuz we j supply text)

#upsert = update or insert
collection.upsert(
    ids=[f"chunk_{i}" for i in range(len(chunks))],
    documents=chunks,
    metadatas=[
        {"source": path.name, "chunk_index": i}
        for i in range(len(chunks))
    ],
)

print(f"Indexed {collection.count()} chunks")

# Search
question = "What happens if part AX-204 fails inspection?"

#chromadb accepts list of queries, not just one string, hence why we need list
results = collection.query(
    query_texts=[question],
    n_results=10, #topK concept
) #we tell chromadb to search embeddings in the collections and retrieve records similar to the question

#results is a dictionary, fields like id, documents, metadatas(source)
for rank, (document, metadata, distance) in enumerate(
    zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ),
    start=1,
):
    print(f"\n--- RANK {rank} ---")
    print("Distance:", round(distance, 4))
    print("Source:", metadata["source"])
    print("Text:", document[:200])