from qdrant_client import QdrantClient
import json

QDRANT_URL = "qdrant-production-cd7e.up.railway.app"


embeddings = []

with open("movies_data.json", "rb") as file:
    movies_data = json.load(file)
    
    for i in movies_data:
        if "embeddings" in i:
            embeddings.append(i["embeddings"])

        if len(embeddings) >= 100:
            break

client = QdrantClient(url=QDRANT_URL)

# Find the 10 nearest neighbors for every embedding
print(f"Searching for nearest neighbors... for {len(embeddings)} embeddings...")
for embedding in embeddings:
    try:
        results = client.search(
            collection_name="movies",
            query_vector=embedding,
            limit=10,
            with_payload=True
        )
        
        print(f"Results for embedding {embedding[:5]}...:")  # Print first 5 elements of the embedding
        for result in results:
            print(f"ID: {result.id}, Score: {result.score}, Payload: {result.payload}")
        print("\n")
    except Exception as e:
        print(f"An error occurred: {e}")
        continue