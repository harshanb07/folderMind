
from pathlib import Path
import chromadb

from scanner import scan_directory
from chunking import chunk_document


def index_directory(directory: str):
    root = Path(directory)

    # Connect to our local vector database
    client = chromadb.PersistentClient(path="./chroma_db")

    collection = client.get_or_create_collection(
        name="foldermind_documents"
    )

    # STEP 1: Find all the .txt files
    paths = scan_directory(directory)

    for path in paths:
        # Skip the original root-level demo document
        if path.parent == root:
            continue

        # STEP 2: Read the file and split it into chunks
        text = path.read_text(encoding="utf-8")
        chunks = chunk_document(text)

        if not chunks:
            continue

        # STEP 3: Identify the file and department
        relative_path = path.relative_to(root).as_posix()
        department = path.relative_to(root).parts[0]

        # STEP 4: Prepare records for ChromaDB
        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{relative_path}:{i}"

            metadata = {
                "source": relative_path,
                "directory": department,
                "chunk_index": i,
            }

            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append(metadata)

        # STEP 5: Save chunks into ChromaDB
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        print(f"Indexed {len(chunks)} chunks from {relative_path}")

    print(f"Total chunks in collection: {collection.count()}")


if __name__ == "__main__":
    index_directory("demo_data")
