"""Stage [1] Document Ingestion + Stage [2] Chunking.

load_documents()  -> read every .txt file in documents/
chunk_documents() -> split one document's text into paragraph-based chunks
"""

import re
from pathlib import Path

DOCUMENTS_DIR = Path(__file__).parent / "documents"

# A paragraph is a run of text bounded by one or more blank lines.
PARAGRAPH_SEPARATOR = re.compile(r"\n\s*\n")


def load_documents(documents_dir=DOCUMENTS_DIR):
    """Load all .txt files from the documents folder.

    Returns a list of dicts, one per file, each with keys:
        "filename" -> the file name (e.g. "quora.txt")
        "text"     -> the full raw text of the file
    """
    documents = []
    for path in sorted(Path(documents_dir).glob("*.txt")):
        documents.append(
            {
                "filename": path.name,
                "text": path.read_text(encoding="utf-8"),
            }
        )
    return documents


def chunk_documents(text, filename):
    """Chunk `text` using the paragraph-based strategy (no overlap).

    Paragraphs are separated by blank lines. Internal newlines are collapsed
    so each chunk is a tidy block, and empty paragraphs are dropped.

    Returns a list of dicts, each with keys:
        "text"     -> the chunk text
        "chunk_id" -> a unique identifier, e.g. "quora.txt_1"
    """
    chunks = []
    index = 1
    for para in PARAGRAPH_SEPARATOR.split(text):
        para = " ".join(para.split()).strip()
        if not para:
            continue
        chunks.append({"text": para, "chunk_id": f"{filename}_{index}"})
        index += 1
    return chunks
