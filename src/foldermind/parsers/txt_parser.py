from pathlib import Path
from ..documents import Document


def parse_txt(path: Path, root: Path) -> list[Document]:

    text = path.read_text(encoding="utf-8") #read the file and store txt

    # Step 2: Find its path relative to our document directory
    relative_path = path.relative_to(root)

    # Step 3: Create a standardized Document
    document = Document(
        text=text,
        source=relative_path.as_posix(),
        metadata={
            "file_type": "txt",
            "directory": relative_path.parts[0],
        },
    )

    return [document]
