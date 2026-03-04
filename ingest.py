import os
import chromadb
from PyPDF2 import PdfReader
from chromadb.utils import embedding_functions

# 1. Force the persistent path
client = chromadb.PersistentClient(path="./db")
ef = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_or_create_collection(name="grade6_syllabus", embedding_function=ef)

def chunk_text(text, chunk_size=1000, overlap=200):
    """Breaks text into smaller overlapping chunks for sharper RAG retrieval."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def ingest_data():
    # Use os.path.join for cross-platform compatibility (Windows/Mac/Linux)
    base_data_path = os.path.join( "data")
    
    if not os.path.exists(base_data_path):
        print(f"❌ ERROR: Base folder '{base_data_path}' not found!")
        print("Make sure your folders are set up like: grade6_assistant/data/science/ and grade6_assistant/data/social_studies/")
        return

    # Iterate through subject folders (e.g., 'science', 'social_studies')
    for subject_folder in os.listdir(base_data_path):
        subject_path = os.path.join(base_data_path, subject_folder)
        
        # Skip if it's not a directory
        if not os.path.isdir(subject_path):
            continue

        print(f"\n📂 Processing subject: {subject_folder.capitalize()}")
        
        for filename in os.listdir(subject_path):
            # Only process PDF files
            if not filename.lower().endswith(".pdf"):
                continue

            print(f"  📄 Reading: {filename}")
            file_path = os.path.join(subject_path, filename)
            
            try:
                reader = PdfReader(file_path)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        # Chunk the text for better precision
                        chunks = chunk_text(text)
                        
                        for chunk_idx, chunk in enumerate(chunks):
                            # Create a unique, descriptive ID
                            doc_id = f"{subject_folder}_{filename}_p{i}_c{chunk_idx}"
                            
                            # Use UPSERT to prevent crashing if you run the script multiple times
                            collection.upsert(
                                documents=[chunk],
                                ids=[doc_id],
                                metadatas=[{
                                    "source": filename, 
                                    "subject": subject_folder.capitalize(), 
                                    "page": i
                                }]
                            )
            except Exception as e:
                print(f"  ❌ Error processing {filename}: {e}")

    print(f"\n✅ Success! Total chunks in DB: {collection.count()}")

if __name__ == "__main__":
    ingest_data()