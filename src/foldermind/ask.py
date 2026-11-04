
from .retrieval import retrieve_documents
from .generation import generate_answer
from .citations import validate_citations, resolve_citations


def ask_foldermind(username: str, question: str) -> str:

    # 1. Retrieve only documents this user can access
    results = retrieve_documents(username, question)

    if not results:
        return "Access denied or no authorized documents."

    documents = results["documents"][0] #retrive chunks for that first question, we ask one question at a time
    metadatas = results["metadatas"][0]

    if not documents:
        return "No relevant documents found."

    # 2. Build the context for Ollama
    context_parts = []

    for i, (document, metadata) in enumerate(
        zip(documents, metadatas), start=1
    ):
        context_parts.append(
            f"[Source {i}]\n"
            f"File: {metadata['source']}\n"
            f"Content: {document}"
        )

    context = "\n\n".join(context_parts)

    # 3. Give Ollama the question and retrieved context
    answer = generate_answer(question, context)


    # Check whether the LLM used valid source references
    if answer != "The provided documents do not establish this information.":
        if not validate_citations(answer, len(documents)):
            return "Answer generated, but citations are missing or invalid."

    # Match source references back to their actual files
    retrieved_chunks = [
        {
            "text": document,
            "source": metadata["source"],
            "chunk_index": metadata["chunk_index"],
        }
        for document, metadata in zip(documents, metadatas)
    ]

    sources = resolve_citations(answer, retrieved_chunks)

    print("CITED SOURCES:", sources)
    return answer


if __name__ == "__main__":
    answer = ask_foldermind(
        username="sam",
        question="What is Jordan Ellis's salary?"
    )

    print("\nFOLDERMIND ANSWER:\n")
    print(answer)
