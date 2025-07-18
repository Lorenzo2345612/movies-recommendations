import json
import os
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, HnswConfigDiff, PointStruct
from dotenv import load_dotenv
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
print(f"Conectando a Qdrant en {QDRANT_URL}")
INPUT_FILE = "movies_data.json"

def upload_to_qdrant(movies):
    client = QdrantClient(url=QDRANT_URL)
    collection = "movies"

    if client.collection_exists(collection):
        client.delete_collection(collection)
        print("Colección existente eliminada.")

    client.create_collection(
        collection_name=collection,
        vectors_config=VectorParams(
            size=len(movies[0]['embeddings']),
            distance=Distance.COSINE,
            hnsw_config=HnswConfigDiff(ef_construct=200, m=16)
        )
    )

    print("Subiendo puntos a Qdrant...")
    batch = []
    ids = set()
    for movie in movies:
        if movie['id'] in ids:
            print(f"[WARN] ID duplicado encontrado: {movie['id']}")
            continue
        ids.add(movie['id'])
        batch.append(
            PointStruct(
                id=movie['id'],
                vector=movie['embeddings'],
                payload={
                    'title': movie['title'],
                    'genres': movie['genres'],
                    'certification': movie['certification']
                }
            )
        )
        if len(batch) >= 100:
            client.upsert(collection_name=collection, points=batch)
            batch = []

    if batch:
        client.upsert(collection_name=collection, points=batch)

    print(f"Subida completada. Total: {len(movies)}")

def main():
    with open(INPUT_FILE, encoding='utf-8') as f:
        movies = json.load(f)
    upload_to_qdrant(movies)

if __name__ == "__main__":
    main()
