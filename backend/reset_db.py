from qdrant_client import QdrantClient
from sqlalchemy import text
from db.db import init_db, SessionLocal
from db.movies import Movie, Genre, Certification
import os
from dotenv import load_dotenv
from qdrant_client.models import VectorParams, Distance, HnswConfigDiff, PointStruct
from sentence_transformers import SentenceTransformer
load_dotenv()

qdrant_client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
model = SentenceTransformer('all-mpnet-base-v2')

print("Eliminando colección 'movies' en Qdrant...")
if qdrant_client.collection_exists("movies"):
    qdrant_client.delete_collection("movies")
    print("Colección eliminada.")
else:
    print("No existía colección previa.")
print("Reiniciando base de datos...")

qdrant_client.create_collection(
    collection_name="movies",
    vectors_config=VectorParams(
        size=model.get_sentence_embedding_dimension(),
        distance=Distance.COSINE,
        hnsw_config=HnswConfigDiff(ef_construct=200, m=16)
    )
)


print("Limpiando base de datos...")
init_db()
session = SessionLocal()
session.execute(text("DELETE FROM certifications"))
session.execute(text("DELETE FROM movie_genre"))
session.execute(text("DELETE FROM movies"))
session.execute(text("DELETE FROM genres"))
session.commit()
session.close()
print("Base de datos reiniciada.")
