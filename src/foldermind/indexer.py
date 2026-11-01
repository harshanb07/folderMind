from pathlib import Path

from scanner import scan_directory
from chunking import chunk_document


def index_directory(directory: str):
    root = Path(directory)

    paths = scan_directory(directory)

    for path in paths:
        # Ignore the root-level manufacturing demo for now.
        if path.parent == root:
            continue

        text = path.read_text(encoding="utf-8")
        chunks = chunk_document(text)

        relative_path = path.relative_to(root).as_posix()
        department = path.relative_to(root).parts[0]

        for i, chunk in enumerate(chunks):
            chunk_id = f"{relative_path}:{i}"

            metadata = {
                "source": relative_path,
                "directory": department,
                "chunk_index": i,
            }

            print("CHUNK ID:", chunk_id)
            print("METADATA:", metadata)
            print("TEXT:", chunk[:100])
            print("---")


if __name__ == "__main__":
    index_directory("demo_data")