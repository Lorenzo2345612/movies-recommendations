import asyncio
import aiohttp
import os
import requests
import time
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, HnswConfigDiff, PointStruct
from sqlalchemy import text
from db.movies import Movie, Genre, Certification
from db.db import SessionLocal
from aiolimiter import AsyncLimiter

# Config
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
START_PAGE = 1
END_PAGE = 1

MAX_RATE = 45
MINIMUM_TIME = 1

headers = {"accept": "application/json"}
model = SentenceTransformer('all-mpnet-base-v2')
qdrant_client = QdrantClient(url=QDRANT_URL)

UNSAFE_CERTIFICATIONS = {"NC-17", "X", "18+", "C", "D", "MA", "TV-MA"}
VALID_CERTIFICATIONS = {
    "G": 0, "PG": 10, "PG-13": 13, "R": 17, "NC-17": 18,
    "TV-G": 0, "TV-PG": 10, "TV-14": 14, "TV-MA": 18,
}

def get_movie_genres():
    url_genres = "https://api.themoviedb.org/3/genre/movie/list"
    params = {"language": "es", "api_key": TMDB_API_KEY}
    response = requests.get(url_genres, headers=headers, params=params)
    if response.status_code == 200:
        return {genre['id']: genre['name'] for genre in response.json()['genres']}
    raise Exception(f"Error fetching genres: {response.status_code}")

def clean_movie_data(movie, genres):
    return {
        'id': movie['id'],
        'overview': movie.get('overview') or '',
        'title': movie['title'],
        'genres': [genres.get(i, 'Unknown') for i in movie.get('genre_ids', [])],
        'release_date': movie.get('release_date'),
        'popularity': movie.get('popularity'),
        'vote_average': movie.get('vote_average'),
        'vote_count': movie.get('vote_count'),
        'poster_path': movie.get('poster_path'),
        'backdrop_path': movie.get('backdrop_path'),
        'adult': movie.get('adult', False),
        'origin_country': movie.get('origin_country', []),
        'original_language': movie.get('original_language', 'es')
    }

def clean_movies_data(movies, genres):
    return [clean_movie_data(movie, genres) for movie in movies]

async def fetch_movie_page(session, page, rate_limiter):
    url = "https://api.themoviedb.org/3/movie/popular"
    params = {"language": "es", "page": page, "api_key": TMDB_API_KEY, "include_adult": "false"}
    try:
        async with rate_limiter:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status != 200:
                    print(f"Error fetching page {page}: {response.status}")
                    return []
                data = await response.json()
                return data.get("results", [])
    except Exception as e:
        print(f"Error fetching page {page}: {e}")
        return []

async def fetch_movie_pages_in_range(start_page, end_page):
    movies = []
    connector = aiohttp.TCPConnector(limit=10)
    rate_limiter = AsyncLimiter(MAX_RATE, MINIMUM_TIME)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_movie_page(session, page, rate_limiter) for page in range(start_page, end_page + 1)]
        results = await asyncio.gather(*tasks)
        for page_movies in results:
            movies.extend(page_movies)
    return movies

async def fetch_certification(session, movie_id, rate_limiter):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/release_dates"
    try:
        async with rate_limiter:
            async with session.get(url, params={"api_key": TMDB_API_KEY}, headers=headers) as resp:
                if resp.status != 200:
                    return movie_id, None
                data = await resp.json()
                for result in data.get("results", []):
                    if result["iso_3166_1"] == "US":
                        for release in result.get("release_dates", []):
                            cert = release.get("certification", "").strip()
                            if cert:
                                return movie_id, cert
    except:
        pass
    return movie_id, None

async def get_certifications_for_movies(movie_list):
    result = {}
    connector = aiohttp.TCPConnector(limit=20)
    limiter = AsyncLimiter(MAX_RATE, MINIMUM_TIME)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_certification(session, m["id"], limiter) for m in movie_list]
        for future in asyncio.as_completed(tasks):
            mid, cert = await future
            if cert:
                result[mid] = cert
    return result

def get_movie_embeddings(movie):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie['id']}"
        response = requests.get(url, headers=headers, params={"api_key": TMDB_API_KEY})
        if response.status_code == 200:
            data = response.json()
            text = f"{data.get('title', '')}. {data.get('overview', '')}. " + \
                   ", ".join([g['name'] for g in data.get('genres', [])]) + ". " + \
                   ", ".join([p['name'] for p in data.get('production_companies', [])])
            return model.encode(text, convert_to_tensor=True).tolist()
    except Exception as e:
        print(f"Error embedding movie {movie['id']}: {e}")
    return None

def upload_movies_to_db(movies):
    session = SessionLocal()

    certifications = asyncio.run(get_certifications_for_movies(movies))
    processed_ids = set()

    existing_certs = {c.certification for c in session.query(Certification).all()}
    for cert, min_age in VALID_CERTIFICATIONS.items():
        if cert not in existing_certs:
            session.add(Certification(certification=cert, min_age=min_age))

    qdrant_movies = []

    for movie in movies:
        if movie['adult'] or movie['original_language'] in ['zh', 'ja', 'ko', 'th', 'vi']:
            continue
        if any(c in ['JP', 'CN', 'KR', 'TW', 'HK'] for c in movie['origin_country']):
            continue
        if not movie['genres']:
            continue

        cert = certifications.get(movie['id'])
        if cert not in VALID_CERTIFICATIONS:
            continue

        movie['certification'] = cert
        embedding = get_movie_embeddings(movie)
        if not embedding:
            continue

        if movie['id'] in processed_ids:
            continue
        processed_ids.add(movie['id'])

        movie['embeddings'] = embedding

        try:
            qdrant_movies.append(PointStruct(id=movie['id'], vector=embedding, payload={'title': movie['title']}))
        except Exception as e:
            print(f"Error creating Qdrant point for movie {movie['id']}: {e}")
            continue

        certification_obj = session.query(Certification).filter_by(certification=cert).first()
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
            certification=certification_obj,
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
        qdrant_client.upsert(collection_name='movies', points=qdrant_movies)

    session.commit()
    session.close()


def main():
    start_time = time.time()
    genres = get_movie_genres()
    print(f"Descargando páginas {START_PAGE} a {END_PAGE}...")
    raw_movies = asyncio.run(fetch_movie_pages_in_range(START_PAGE, END_PAGE))
    cleaned = clean_movies_data(raw_movies, genres)
    upload_movies_to_db(cleaned)
    end_time = time.time()
    print(f"Carga completada en {end_time - start_time:.2f} segundos.")

if __name__ == "__main__":
    main()