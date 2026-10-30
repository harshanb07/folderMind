import re

#ollama previously generated 'Source N' during a test run, so this can help catch and reject these references

def validate_citations(answer: str, source_count: int) -> bool:
    references = re.findall(
        r"\[Source\s+([^\]]+)\]",
        answer,
        flags=re.IGNORECASE,
    )

    if not references:
        return False

    for reference in references:
        if not reference.isdigit():
            return False

        number = int(reference)

        if not 1 <= number <= source_count:
            return False

    return True

# this goes into the retrieved chunks and actually figures out the info 'source X' has 
def resolve_citations(answer: str, retrieved_chunks: list[dict]) -> list[dict]:
    source_numbers = re.findall(r"\[Source (\d+)\]", answer)
    sources = []

    for number in source_numbers:
        index = int(number) - 1

        if 0 <= index < len(retrieved_chunks):
            sources.append(retrieved_chunks[index])

    return sources