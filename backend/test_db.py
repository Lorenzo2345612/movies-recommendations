from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import requests

# URL for the TMDB API to get popular movies in Spanish

url = "https://api.themoviedb.org/3/movie/popular"

headers = {
    "accept": "application/json"
}

# Initialize the SentenceTransformer model

model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize the Qdrant client (assuming you have a Qdrant instance running)
qdrant_client = QdrantClient(host='localhost', port=6333)


def get_movie_genres():
    """
    Function to get the list of movie genres from TMDB.
    
    Returns:
        dict: A dictionary containing genre IDs and names.
    """
    
    url_genres = "https://api.themoviedb.org/3/genre/movie/list"
    
    params = {
        "language": "es",
        #"api_key": "None"
    }
    
    response = requests.get(url_genres, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return {genre['id']: genre['name'] for genre in data['genres']}
    else:
        raise Exception(f"Error fetching genres: {response.status_code} - {response.text}")


def get_movies(page: int):
    """
    Function to get a list of movies for a given page.
    
    Args:
        page (int): The page number to retrieve.
    
    Returns:
        list: A list of movies for the specified page.
    """
    
    params = {
        "language": "es",
        "page": page,
        "api_key": "e6a366c561d20cfdccb9ee9c4c4765a8"
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data['results']
    else:
        raise Exception(f"Error fetching movies: {response.status_code} - {response.text}")
    
def clean_movie_data(movie, genres):
    """
    Function to clean movie data by removing unnecessary fields.
    
    Args:
        movie (dict): The movie data to clean.
    
    Returns:
        dict: Cleaned movie data.
    """
    movie_clean = dict()
    movie_clean['id'] = movie.get('id')
    movie_clean['overview'] = movie.get('overview')
    movie_clean['title'] = movie.get('title')
    movie_clean['genres'] = []

    for i in movie.get('genre_ids', []):
        movie_clean['genres'].append(genres.get(i, 'Unknown'))

    return movie_clean


def clean_movies_data(movies, genres):
    """
    Function to clean a list of movies by removing unnecessary fields.
    
    Args:
        movies (list): The list of movies to clean.
    
    Returns:
        list: A list of cleaned movie data.
    """
    
    return [clean_movie_data(movie, genres) for movie in movies]

def get_movie_embeddings(movie):
    """
    Function to get the embeddings for a movie's overview.
    
    Args:
        movie (dict): The movie data containing the overview.
    
    Returns:
        list: The embeddings for the movie's overview.
    """
    
    title = movie.get('title', '')
    overview = movie.get('overview', '')
    genres = ', '.join(movie.get('genres', []))
    text = f"{title} {overview} {genres}"
    return model.encode([text])[0].tolist()


# Main script to fetch, clean, and upload movies to the database

genres = get_movie_genres()

movies = []
for page in range(6, 7):  # Fetching first 5 pages
    movies_page = get_movies(page)
    cleaned_movies = clean_movies_data(movies_page, genres)
    movies.extend(cleaned_movies)

import json

resultados_json = {}

for movie in movies:
    query_id = movie["id"]
    query_info = {
        "id": query_id,
        "title": movie.get("title"),
        "overview": movie.get("overview"),
        "genres": movie.get("genres", [])
    }

    # Obtener resultados desde Qdrant
    resultados = qdrant_client.search(
        collection_name="movies",
        query_vector=get_movie_embeddings(movie),
        limit=5,
        with_payload=True
    )

    resultados_similares = []
    for result in resultados:
        resultados_similares.append({
            "id": result.id,
            "score": float(result.score),  # Asegúrate que sea serializable
            "title": result.payload.get("title"),
            "overview": result.payload.get("overview"),
            "genres": result.payload.get("genres")
        })

    # Guardar en el JSON
    resultados_json[query_id] = {
        "query": query_info,
        "results": resultados_similares
    }

# Guardar en archivo
with open("resultados_similares.json", "w", encoding="utf-8") as f:
    json.dump(resultados_json, f, ensure_ascii=False, indent=4)



        