from pathlib import Path
import chromadb

from .scanner import scan_directory
from .chunking import chunk_document
from .parsers.txt_parser import parse_txt


def index_directory(directory: str):
    root = Path(directory) #creating path objects to help breakdown

    # Connect to ChromaDB
    client = chromadb.PersistentClient(path="./chroma_db")

    collection = client.get_or_create_collection(
        name="foldermind_documents"
    )

    # Find all TXT files within the req'd directory
    paths = scan_directory(directory)

    # Process each file
    for path in paths: 

        # Skip root-level demo files
        if path.parent == root: #only for the case where in our 'demo_docs' folders hass some standalone file that isn't in a specific directory like production
            continue

        # Parse this file into Document objects
        parsed_documents = parse_txt(path, root) #returns a list containing document object

        # Process every Document returned by the parser, technically one 1 document for txt files. more possible for pdfs
        for document_index, document in enumerate(parsed_documents):

            # Split this Document's text into chunks
            chunks = chunk_document(document.text) #we can access via '.text' because Document is a dataclass

            if not chunks:
                continue

            # Prepare parallel lists for ChromaDB
            ids = []
            texts = []
            metadatas = []

            for i, chunk in enumerate(chunks): #iterate over respective chunk and its index (to create unique keys)

                # Unique ID for this chunk
                chunk_id = f"{document.source}:{document_index}:{i}" #this means every literal chunk has a different index, but also every PAGE in a pdf would also have a different index, so source overlapping not possible

                # Preserve parser metadata
                metadata = {
                    **document.metadata, #dictionary unpacking, so all metadata from document class is copied over to this new dict
                    "source": document.source, #keps source separate in dataclass because EVERY chunk needs a source
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
