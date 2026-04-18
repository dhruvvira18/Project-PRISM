import io
import logging
import chromadb
from PyPDF2 import PdfReader


def create_or_get_byom_collection():
    client = chromadb.PersistentClient(path="./prism_db")
    try:
        return client.get_collection(name="prism_byom")
    except Exception:
        try:
            return client.create_collection(name="prism_byom")
        except Exception as e:
            logging.error(f"Failed to create or access BYOM collection: {e}")
            raise


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    normalized = " ".join(text.split())
    if not normalized:
        return []

    chunks = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(normalized):
            break
        start += chunk_size - overlap
    return chunks


def process_byom_pdf(file_bytes: bytes):
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except Exception as e:
        logging.error(f"PDF parsing failed: {e}")
        raise ValueError("Could not read the PDF file. Please upload a valid PDF.")

    pages = len(reader.pages)
    if pages == 0:
        raise ValueError("PDF contains no readable pages.")
    if pages > 15:
        raise ValueError("BYOM uploads are limited to 15 pages.")

    document_text = ""
    for idx, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
            document_text += page_text + "\n\n"
        except Exception as e:
            logging.warning(f"Unable to extract text from page {idx}: {e}")

    if not document_text.strip():
        raise ValueError("Could not extract text from the PDF. Try a different document.")

    chunks = chunk_text(document_text, chunk_size=1000, overlap=200)
    if not chunks:
        raise ValueError("The PDF did not produce any usable text chunks.")

    collection = create_or_get_byom_collection()

    try:
        existing = collection.get()
        existing_ids = existing.get("ids", [])
        if existing_ids:
            collection.delete(ids=existing_ids)
    except Exception as delete_error:
        logging.warning(f"Failed to clear previous BYOM data: {delete_error}")

    ids = [f"byom-{i + 1}" for i in range(len(chunks))]
    metadatas = [
        {
            "subject": "byom",
            "chapter_name": "Uploaded Document",
            "page_index": i + 1,
        }
        for i in range(len(chunks))
    ]

    collection.add(ids=ids, metadatas=metadatas, documents=chunks)
    logging.info(f"BYOM PDF processed: {len(chunks)} chunks upserted.")
    return len(chunks)
