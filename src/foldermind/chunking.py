from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path

def chunk_document(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    ) #the langchain library handles all splitting logic

    return splitter.split_text(text)


file_path = Path("demo_data/foldermind_manufacturing_demo.txt")
text_doc = file_path.read_text(encoding="utf-8")
chunks = chunk_document(text_doc)

for i, chunk in enumerate(chunks):
    print(f"\n--- CHUNK {i + 1} ---")
    print(chunk)