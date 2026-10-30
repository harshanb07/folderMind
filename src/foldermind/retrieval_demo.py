from pathlib import Path
import chromadb

from chunking import chunk_document
from generation import generate_answer #getting the llm call and prompt
from citations import validate_citations, resolve_citations

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
questions = [
    "What caused the machine stoppage on WO-7312?"
]

for question in questions:
    print(f"\nQUESTION: {question}")

    results = collection.query(
        query_texts=[question],
        n_results=1,
    )

    retrieved_chunks = []

    for chunk_id, document, metadata in zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
    ):
        retrieved_chunks.append({
            "id": chunk_id,
            "text": document,
            "source": metadata["source"],
            "chunk_index": metadata["chunk_index"],
        })

    for rank, (document, distance) in enumerate(
        zip(
            results["documents"][0],
            results["distances"][0],
        ),
        start=1,
    ):
        print(f"\nRank {rank}, Distance {distance:.4f}")
        print(document[:250])


    context = "\n\n".join(
        f"[Source {i}]\n"
        f"File: {chunk['source']}\n"
        f"Content: {chunk['text']}"
        for i, chunk in enumerate(retrieved_chunks, start=1)
    )

    answer = generate_answer(question, context)

    is_valid = validate_citations(
        answer,
        len(retrieved_chunks),
    )

    if is_valid:
        sources = resolve_citations(answer, retrieved_chunks)
        print("\nFOLDERMIND ANSWER:")
        print(answer)
        print("\nACTUAL CITED SOURCES:")

        for source in sources:
            print(f"File: {source['source']}")
            print(f"Chunk ID: {source['id']}")
            print(f"Chunk Index: {source['chunk_index']}")
            print("---")
    else:
        print("\nCitation validation failed.")
        print("Candidate answer (not verified):")
        print(answer)

