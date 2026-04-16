import os
import json
import chromadb
import logging
from PyPDF2 import PdfReader
from chromadb.utils import embedding_functions

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# 1. Initialize ChromaDB
client = chromadb.PersistentClient(path="./prism_db")
ef = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(name="prism_curriculum", embedding_function=ef)

def chunk_text(text, chunk_size=1000, overlap=200):
    """Breaks text into smaller overlapping chunks for better semantic retrieval."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def ingest_data(target_grade=None, target_subject=None):
    kb_path = "knowledge_base"
    
    if not os.path.exists(kb_path):
        logging.error(f"Folder '{kb_path}' not found! Ensure it is in your root directory.")
        return

    # 1. Iterate through Grade folders (grade6, grade7, etc.)
    for grade_folder in os.listdir(kb_path):
        # ISOLATION: Skip if it doesn't match our target grade
        if target_grade and grade_folder != target_grade:
            continue
            
        grade_path = os.path.join(kb_path, grade_folder)
        if not os.path.isdir(grade_path): continue

        # 2. Iterate through Subject folders (science, social_science)
        for subject_folder in os.listdir(grade_path):
            # ISOLATION: Skip if it doesn't match our target subject
            if target_subject and subject_folder != target_subject:
                continue

            subject_path = os.path.join(grade_path, subject_folder)
            if not os.path.isdir(subject_path): continue

            mapping_file = os.path.join(subject_path, "mapping.json")
            if not os.path.exists(mapping_path := mapping_file):
                logging.warning(f"No mapping.json found in {subject_path}. Skipping.")
                continue

            with open(mapping_path, 'r') as f:
                mapping = json.load(f)

            logging.info(f"--- Processing {grade_folder.upper()} | {subject_folder.upper()} ---")

            # 3. Process each chapter defined in mapping.json
            for ch_num, ch_data in mapping.items():
                ch_name = ch_data['name']
                filename = ch_data['file']
                file_path = os.path.join(subject_path, filename)

                if not os.path.exists(file_path):
                    logging.error(f"File {filename} (Ch {ch_num}) missing in {subject_path}")
                    continue

                logging.info(f"Ingesting Chapter {ch_num}: {ch_name}")

                try:
                    reader = PdfReader(file_path)
                    for page_num, page in enumerate(reader.pages):
                        text = page.extract_text()
                        if not text: continue

                        chunks = chunk_text(text)
                        
                        for c_idx, chunk in enumerate(chunks):
                            unique_id = f"{grade_folder}_{subject_folder}_ch{ch_num}_p{page_num}_c{c_idx}"
                            
                            collection.upsert(
                                documents=[chunk],
                                ids=[unique_id],
                                metadatas=[{
                                    "grade": grade_folder,
                                    "subject": subject_folder,
                                    "chapter_number": ch_num,
                                    "chapter_name": ch_name,
                                    "chapter_name_normalized": " ".join(ch_name.strip().lower().split()),
                                    "page": page_num
                                }]
                            )
                except Exception as e:
                    logging.error(f"Failed to process {filename}: {e}")

    logging.info(f"Ingestion Complete! Total vectors in DB: {collection.count()}")

if __name__ == "__main__":
    # --- ISOLATION MODE FOR FAST TESTING ---
    # Set these to the specific folder names you want to test right now.
    # To run the ENTIRE library later, change both values to None.
    
    TEST_GRADE = "grade6"       # e.g., "grade6", "grade7", or None
    TEST_SUBJECT = "science"    # e.g., "science", "social_science", or None
    
    logging.info(f"Starting ingestion. Target Grade: {TEST_GRADE} | Target Subject: {TEST_SUBJECT}")
    ingest_data(target_grade=TEST_GRADE, target_subject=TEST_SUBJECT)