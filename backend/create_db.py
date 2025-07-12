from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, HnswConfigDiff, PointStruct
from transformers import pipeline
import requests
from db.movies import Movie, Genre
from db.db import init_db, SessionLocal
import os
from sqlalchemy import text
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline


# Environment variables for TMDB API and Qdrant URL
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

# URL for the TMDB API to get popular movies in Spanish
url = "https://api.themoviedb.org/3/movie/popular"

headers = {
    "accept": "application/json"
}

# Initialize the SentenceTransformer model
model = SentenceTransformer('all-mpnet-base-v2')

# Initialize the zero-shot classifier

SEXUAL_CATEGORIES = ["sexual content", "erotic scenes", "nudity", "pornographic", "intimate scenes"]

# Initialize the Qdrant client (assuming you have a Qdrant instance running)
qdrant_client = QdrantClient(url=QDRANT_URL)

# Delete the existing collection if it exists
try:
    qdrant_client.delete_collection(collection_name='movies')
except Exception as e:
    print(f"Error deleting collection: {e}")

qdrant_client.recreate_collection(
    collection_name='movies',
    vectors_config=VectorParams(
        size=768,
        distance=Distance.COSINE,
        hnsw_config=HnswConfigDiff(
            m=16,
            ef_construct=200,
            full_scan_threshold=1000
        )
    )
)


""" def has_sexual_content(movie: dict) -> bool:

    Detecta si una película probablemente contiene contenido sexual basado en su título y overview.
    Usa zero-shot classification.

    title = movie.get("title", "")
    overview = movie.get("overview", "")
    genres = ', '.join(movie.get('genres', []))

    text = f"{title}. {overview}. {genres}"
    result = classifier(text, candidate_labels=SEXUAL_CATEGORIES)
    top_label = result["labels"][0]
    top_score = result["scores"][0]

    return top_score >= 0.7 and top_label in SEXUAL_CATEGORIES """


def get_movie_genres():
    url_genres = "https://api.themoviedb.org/3/genre/movie/list"
    params = {
        "language": "es",
        "api_key": TMDB_API_KEY
    }
    response = requests.get(url_genres, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return {genre['id']: genre['name'] for genre in data['genres']}
    else:
        raise Exception(f"Error fetching genres: {response.status_code} - {response.text}")


def get_movies(page: int):
    params = {
        "language": "es",
        "page": page,
        "api_key": TMDB_API_KEY,
        "adult": "false",
        "include_adult": "false",
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['results']
    else:
        raise Exception(f"Error fetching movies: {response.status_code} - {response.text}")


def clean_movie_data(movie, genres):
    movie_clean = dict()
    movie_clean['id'] = movie.get('id')
    movie_clean['overview'] = movie.get('overview')
    movie_clean['title'] = movie.get('title')
    movie_clean['genres'] = []
    movie_clean['release_date'] = movie.get('release_date')
    movie_clean['popularity'] = movie.get('popularity')
    movie_clean['vote_average'] = movie.get('vote_average')
    movie_clean['vote_count'] = movie.get('vote_count')
    movie_clean['poster_path'] = movie.get('poster_path')
    movie_clean['backdrop_path'] = movie.get('backdrop_path')
    movie_clean['adult'] = movie.get('adult', False)
    movie_clean['origin_country'] = movie.get('origin_country', [])
    movie_clean['original_language'] = movie.get('original_language', 'es')
    for i in movie.get('genre_ids', []):
        movie_clean['genres'].append(genres.get(i, 'Unknown'))
    return movie_clean


def clean_movies_data(movies, genres):
    return [clean_movie_data(movie, genres) for movie in movies]


def get_movie_embeddings(movie):
    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie['id']}",
            headers=headers,
            params={
                "api_key": TMDB_API_KEY,
            }
        )

        if response.status_code == 200:
            data = response.json()
            title = data.get('title', '')
            overview = data.get('overview', title)
            genres = ', '.join([genre['name'] for genre in data.get('genres', [])])
            productors = ', '.join([prod['name'] for prod in data.get('production_companies', [])])

            text = f"{title}. {overview}. {genres}. {productors}"
            print(f"Generating embeddings for movie ID {movie['id']}: {text}")
            return model.encode(text, convert_to_tensor=True).tolist()
        else:
            print(f"Error fetching movie details for ID {movie['id']}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception while fetching movie details for ID {movie['id']}: {e}")
        return None

SAFE_GENRE_IDS = {
    "Acción",
    "Aventura",
    "Animación",
    "Documental",
    "Familia",
    "Fantasía",
    "Música",
    "Ciencia ficción",
    "Película de TV"
}

RISKY_GENRE_IDS = {
"Crimen",
    "Drama",
    "Historia",
    "Terror",
    "Misterio",
    "Romance",
    "Suspense",
    "Bélica",
    "Western",
        "Comedia"
}



def is_genre_combination_risky(genres: list[str]) -> bool:
    """
    Devuelve True si la película tiene al menos un género riesgoso
    y ninguno seguro.
    """
    genres_set = set(genres)
    has_risky = bool(genres_set & RISKY_GENRE_IDS)
    has_safe = bool(genres_set & SAFE_GENRE_IDS)
    
    return has_risky and not has_safe


def upload_movies_to_db(movies):
    init_db()
    session = SessionLocal()

    session.execute(text("DELETE FROM movie_genre"))
    session.execute(text("DELETE FROM movies"))
    session.execute(text("DELETE FROM genres"))
    session.commit()

    count = session.query(Movie).count()
    print(f"Number of movies in the database before upload: {count}")

    qdrant_movies: list = []

    initial_movie_count = len(movies)
    print(f"Initial number of movies to process: {initial_movie_count}")

    movies_country = 0
    movies_sexual_content = 0

    for movie in movies:
        # Filtro de contenido sexual o adult
        if bool(movie['adult']) or 'adult' in movie['genres'] or movie['original_language'] in ['zh', 'ja', 'ko', 'th', 'vi']:
            print(f"Skipping adult/marked movie: {movie['id']} - {movie['title']}")
            initial_movie_count -= 1
            movies_country += 1
            continue

        for country in movie['origin_country']:
            if country in ['JP', 'CN', 'KR', 'TW', 'HK']:
                print(f"Skipping movie from Asian country: {movie['id']} - {movie['title']}")
                initial_movie_count -= 1
                movies_country += 1
                continue

        if movie['genres'] is None or len(movie['genres']) == 0:
            print(f"Skipping movie with no genres: {movie['id']} - {movie['title']}")
            initial_movie_count -= 1
            continue

        # Clasificación de contenido sexual
        if is_genre_combination_risky(movie['genres']):
            print(f"Skipping risky genre combination movie: {movie['id']} - {movie['title']}")
            initial_movie_count -= 1
            movies_sexual_content += 1
            continue
        """ if has_sexual_content(movie):
            print(f"Skipping sexual content movie: {movie['id']} - {movie['title']}")
            initial_movie_count -= 1
            movies_sexual_content += 1
            continue """

        embeding = get_movie_embeddings(movie)
        if not embeding:
            print(f"Skipping movie due to missing embeddings: {movie['id']} - {movie['title']}")
            initial_movie_count -= 1
            continue
        movie['embeddings'] = embeding

        qdrant_movies.append(
            PointStruct(
                id=movie['id'],
                vector=movie['embeddings'],
                payload={
                    'title': movie['title']
                }
            )
        )

        if qdrant_movies and len(qdrant_movies) % 100 == 0:
            qdrant_client.upsert(
                collection_name='movies',
                points=qdrant_movies
            )
            qdrant_movies = []

        if session.query(Movie).filter_by(id=movie['id']).first():
            continue

        movie_obj = Movie(
            id=movie['id'],
            title=movie['title'],
            overview=movie['overview'],
            release_date=movie['release_date'] if movie['release_date'] else None,
            popularity=movie['popularity'],
            vote_average=movie['vote_average'],
            vote_count=movie['vote_count'],
            poster_path=movie['poster_path'],
            backdrop_path=movie['backdrop_path'],
            embeddings=str(movie['embeddings'])
        )

        for genre_name in movie['genres']:
            genre = session.query(Genre).filter_by(name=genre_name).first()
            if not genre:
                genre = Genre(name=genre_name)
                session.add(genre)
            movie_obj.genres.append(genre)

        session.add(movie_obj)

    if qdrant_movies:
        qdrant_client.upsert(
            collection_name='movies',
            points=qdrant_movies
        )

    session.commit()

    count = session.query(Movie).count()
    print(f"Number of movies in the database after upload: {count}")

    print(f"Total movies processed: {initial_movie_count}")
    print(f"Movies skipped due to country filter: {movies_country}")
    print(f"Movies skipped due to sexual content: {movies_sexual_content}")


# Main script to fetch, clean, and upload movies to the database

genres = get_movie_genres()
movies = []
for page in range(1, 501):
    print(f"Fetching page {page}")
    movies_page = get_movies(page)
    cleaned_movies = clean_movies_data(movies_page, genres)
    movies.extend(cleaned_movies)

upload_movies_to_db(movies)