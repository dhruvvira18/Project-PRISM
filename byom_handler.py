import os
import io
import chromadb
from chromadb.utils import embedding_functions
from PyPDF2 import PdfReader
import logging
from fastapi import HTTPException

logging.basicConfig(level=logging.INFO)

# Initialize ChromaDB for BYOM
client_db = chromadb.PersistentClient(path="./prism_db")
ef = embedding_functions.DefaultEmbeddingFunction()
collection_byom = client_db.get_or_create_collection(name="prism_byom", embedding_function=ef)

def chunk_text(text, chunk_size=1000, overlap=200):
    """Breaks text into smaller overlapping chunks for better semantic retrieval."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def process_byom_pdf(file_bytes):
    """Process uploaded PDF for BYOM: extract text, check page limit, chunk, and upsert to isolated collection."""
    try:
        # Wrap bytes in BytesIO for PdfReader
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        if len(reader.pages) > 15:
            raise HTTPException(status_code=400, detail="PDF exceeds 15-page limit. Please upload a shorter document.")

        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        if not text.strip():
            raise HTTPException(status_code=400, detail="No extractable text found in the PDF.")

        # Clear existing documents in prism_byom for isolation
        existing_ids = collection_byom.get()["ids"]
        if existing_ids:
            collection_byom.delete(ids=existing_ids)

        # Chunk the text
        chunks = chunk_text(text)

        # Upsert chunks
        documents = chunks
        ids = [f"byom_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"page": i // 10 + 1, "chunk": i} for i in range(len(chunks))]  # Simple metadata

        collection_byom.upsert(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )

        logging.info(f"BYOM PDF processed: {len(chunks)} chunks upserted.")
        return {"message": "PDF uploaded and processed successfully. You can now proceed to the calibration test."}

    except Exception as e:
        logging.error(f"BYOM PDF processing error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process the PDF. Please try again.")