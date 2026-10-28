from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_document(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )
    return splitter.split_text(text)


if __name__ == "__main__":
    from pathlib import Path

    path = Path("demo_data/foldermind_manufacturing_demo.txt")
    text = path.read_text(encoding="utf-8")

    chunks = chunk_document(text)
    print(f"Generated {len(chunks)} chunks")