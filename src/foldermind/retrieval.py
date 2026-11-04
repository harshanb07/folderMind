import chromadb
from .permissions import get_allowed_directories

def retrieve_documents(username: str, question: str):
    # 1. Find which directories the user can access (folders)
    allowed = get_allowed_directories(username)

    # 2. Deny access if they have no grants
    if not allowed:
        return []

    # 3. Connect to the database you already created
    client = chromadb.PersistentClient(path="./chroma_db")

    collection = client.get_collection(
        name="foldermind_documents"
    )

    # 4. Search ONLY authorized directories
    results = collection.query(
        query_texts=[question],
        n_results=3,
        where={ #most important line; tells chromaDB to search where the directory is in the allowed dictionary
            # works because we stored the directory in the metadata in indexer.py 
            # 'where' is a special parameter built into chromadb that filters metadata
            "directory": {
                "$in": sorted(allowed)
            } 
        }
    )

    return results


if __name__ == "__main__":
    question = "What is Jordan Ellis's salary?"

    for user in ["alex", "maya", "sam", "unknown"]:
        results = retrieve_documents(user, question)

        if not results:
            print(f"{user}: ACCESS DENIED")
            continue

        directories = [
            metadata["directory"]
            for metadata in results["metadatas"][0]
        ]

        print(f"{user}: {directories}")