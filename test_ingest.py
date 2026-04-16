import chromadb
from chromadb.utils import embedding_functions

def setup_test_db():
    print("Initializing test database...")
    client = chromadb.PersistentClient(path="./prism_db")
    ef = embedding_functions.DefaultEmbeddingFunction()
    
    collection = client.get_or_create_collection(name="prism_curriculum", embedding_function=ef)
    
    text_chunk = "The mitochondria is the powerhouse of the cell. It generates most of the chemical energy needed to power the cell's biochemical reactions."
    
    # We are injecting the exact same text under three different chapter 
    # names to ensure your UI button clicks find a match.
    collection.upsert(
        documents=[text_chunk, text_chunk, text_chunk],
        ids=["test_mitochondria_ch1", "test_mitochondria_cell", "test_mitochondria_temp"],
        metadatas=[
            {
                "grade": "grade6",
                "subject": "science",
                "chapter_number": "1",
                "chapter_name": "Chapter 1", # Fallback match
                "page": 1
            },
            {
                "grade": "grade6",
                "subject": "science",
                "chapter_number": "2",
                "chapter_name": "Cell Structure", # Exact match
                "page": 1
            },
            {
                "grade": "grade6",
                "subject": "science",
                "chapter_number": "3",
                "chapter_name": "Temperature", # The button you clicked earlier
                "page": 1
            }
        ]
    )
    
    print(f"✅ Test data injected! Total vectors: {collection.count()}")

if __name__ == "__main__":
    setup_test_db()