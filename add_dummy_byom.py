import chromadb
from chromadb.utils import embedding_functions

# Add dummy data to collection_byom for testing
client_db = chromadb.PersistentClient(path="./prism_db")
ef = embedding_functions.DefaultEmbeddingFunction()
collection_byom = client_db.get_or_create_collection(name="prism_byom", embedding_function=ef)

text_chunk = "This is a test PDF content. The mitochondria is the powerhouse of the cell. It generates energy."

collection_byom.upsert(
    documents=[text_chunk],
    ids=["test_byom_chunk"],
    metadatas=[{"page": 1, "chunk": 0}]
)

print("Dummy data added to collection_byom")