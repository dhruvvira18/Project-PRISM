import chromadb
from chromadb.utils import embedding_functions

client_db = chromadb.PersistentClient(path="./prism_db")
ef = embedding_functions.DefaultEmbeddingFunction()
collection_byom = client_db.get_or_create_collection(name="prism_byom", embedding_function=ef)

print("Count:", collection_byom.count())
results = collection_byom.query(query_texts=["powerhouse"], n_results=5)
print("Results:", results)