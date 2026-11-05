
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

    answer = generate_answer(question, context)

    print("FIRST ANSWER:", answer)

    abstention = "The provided documents do not establish this information."

    # Only factual answers require citations
    if answer.strip() != abstention:

        if not validate_citations(answer, len(documents)):

            print("Citation missing or invalid. Retrying...")

            retry_question = (
                f"{question}\n\n"
                "IMPORTANT: Every factual answer MUST include a citation "
                "in the exact format [Source 1] or [Source 2]. "
                "Use only source numbers provided in the evidence. "
                "Never invent a citation. "
                "If the evidence does not answer the question, respond exactly: "
                f"{abstention}"
            )

            answer = generate_answer(retry_question, context)

            print("RETRY ANSWER:", answer)

            if (
                answer.strip() != abstention
                and not validate_citations(answer, len(documents))
            ):
                return "Could not generate an answer with valid citations."
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
