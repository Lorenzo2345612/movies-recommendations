import json
import os
from sqlalchemy import text
from db.db import init_db, SessionLocal
from db.movies import Movie, Genre, Certification

INPUT_FILE = "movies_data.json"

VALID_CERTIFICATIONS = {
    "G": 0,
    "PG": 10,
    "PG-13": 13,
    "R": 17,
    "NC-17": 18,
    "TV-G": 0,
    "TV-PG": 10,
    "TV-14": 14,
    "TV-MA": 18,
}

def upload_movies_to_postgres(movies):
    init_db()
    session = SessionLocal()

    print("Limpiando tablas...")
    session.execute(text("DELETE FROM certifications"))
    session.execute(text("DELETE FROM movie_genre"))
    session.execute(text("DELETE FROM movies"))
    session.execute(text("DELETE FROM genres"))
    session.commit()

    print("Agregando certificaciones...")
    existing_certs = {c.certification for c in session.query(Certification).all()}
    for cert, min_age in VALID_CERTIFICATIONS.items():
        if cert not in existing_certs:
            session.add(Certification(certification=cert, min_age=min_age))
    session.commit()

    ids = set()

    for movie in movies:
        try:
            cert_obj = session.query(Certification).filter_by(certification=movie['certification']).first()
            if not cert_obj:
                print(f"[WARN] Certificación no encontrada: {movie['certification']}")
                continue

            if movie['id'] in ids:
                print(f"[WARN] ID duplicado encontrado: {movie['id']}")
                continue
            ids.add(movie['id'])

            movie_obj = Movie(
                id=movie['id'],
                title=movie['title'],
                overview=movie['overview'],
                release_date=movie['release_date'],
                popularity=movie['popularity'],
                vote_average=movie['vote_average'],
                vote_count=movie['vote_count'],
                poster_path=movie['poster_path'],
                backdrop_path=movie['backdrop_path'],
                certification=cert_obj,
                embeddings=str(movie['embeddings'])  # Puede ser array también, depende del tipo de columna
            )

            for genre_name in movie['genres']:
                genre = session.query(Genre).filter_by(name=genre_name).first()
                if not genre:
                    genre = Genre(name=genre_name)
                    session.add(genre)
                    session.flush()  # Asegura que tenga ID para el many-to-many
                movie_obj.genres.append(genre)

            session.add(movie_obj)

        except Exception as e:
            print(f"[ERROR] Error con película {movie['id']}: {e}")
            session.rollback()
        else:
            session.commit()

    print(f"Se cargaron {len(movies)} películas a PostgreSQL.")

def main():
    with open(INPUT_FILE, encoding='utf-8') as f:
        movies = json.load(f)
    upload_movies_to_postgres(movies)

if __name__ == "__main__":
    main()
