from pathlib import Path
import chromadb

from .scanner import scan_directory
from .chunking import chunk_document
from .parsers.txt_parser import parse_txt


def index_directory(directory: str):
    root = Path(directory)

    # Connect to ChromaDB
    client = chromadb.PersistentClient(path="./chroma_db")

    collection = client.get_or_create_collection(
        name="foldermind_documents"
    )

    # Find all TXT files
    paths = scan_directory(directory)

    # Process each file
    for path in paths:

        # Skip root-level demo files
        if path.parent == root:
            continue

        # Parse this file into Document objects
        parsed_documents = parse_txt(path, root)

        # Process every Document returned by the parser
        for document_index, document in enumerate(parsed_documents):

            # Split this Document's text into chunks
            chunks = chunk_document(document.text)

            if not chunks:
                continue

            # Prepare parallel lists for ChromaDB
            ids = []
            texts = []
            metadatas = []

            for i, chunk in enumerate(chunks):

                # Unique ID for this chunk
                chunk_id = f"{document.source}:{document_index}:{i}"

                # Preserve parser metadata
                metadata = {
                    **document.metadata,
                    "source": document.source,
                    "chunk_index": i,
                }

                ids.append(chunk_id)
                texts.append(chunk)
                metadatas.append(metadata)

            # Store this Document's chunks in ChromaDB
            collection.upsert(
                ids=ids,
                documents=texts,
                metadatas=metadatas,
            )

            print(
                f"Indexed {len(chunks)} chunks "
                f"from {document.source}"
            )

    print(f"Total chunks: {collection.count()}")


if __name__ == "__main__":
    index_directory("demo_data")
