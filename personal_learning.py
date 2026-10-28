


from pathlib import Path

def read_document(path: str) -> str:
    read_path = Path(path)
    return read_path.read_text(encoding="utf-8")

content = read_document(
    "demo_data/foldermind_manufacturing_demo.txt"
)

print(content[:200])