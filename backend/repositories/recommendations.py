from abc import ABC, abstractmethod
from models.movie import MovieDetails, MovieRecommendation
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient as QdrantClientLib
from repositories.movies import MoviesRepository
import os
import requests
import asyncio


class RecommendationsRepository(ABC):
    def __init__(self, movies_repository: MoviesRepository):
        self.movies_repository = movies_repository
        super().__init__()

    @abstractmethod
    def get_recommendations_by_movie(self, embedding: list[float]) -> list[MovieRecommendation]:
        pass


class QdrantClient:
    def __init__(self, url: str = "http://localhost:6333", port: int = 6333):
        self.qdrant_client = QdrantClientLib(url=url, port=port)

    def get_recommendations(self, collection_name: str, embedding: list[float], id: int, limit: int = 10) -> list[tuple[int, float]]:
        """
        Get movie recommendations based on an embedding vector.

        Args:
            embedding (list[float]): The embedding vector for the movie.
            limit (int): The maximum number of recommendations to return.

        Returns:
            list[int]: A list of recommended movie IDs.
        """
        search_result = self.qdrant_client.search(
            collection_name=collection_name,
            query_vector=embedding,
            limit=limit + 15
        )
        

        return [(result.id, result.score) for result in search_result if result.id != id and result.score > 0.49][:limit]
    
class EmbeddingClient:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def get_embedding(self, movie: MovieDetails) -> list[float]:
        """
        Get the embedding vector for a movie.

        Args:
            movie (Movie): The movie for which the embedding is to be generated.

        Returns:
            list[float]: The embedding vector for the movie.
        """
        return self.model.encode(movie.title + " " + movie.overview, convert_to_tensor=True).tolist()

class RecommendationsRepositoryTMDB(RecommendationsRepository):
    url = "https://api.themoviedb.org/3/"

    def __init__(self, movies_repository: MoviesRepository):
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant_client = QdrantClient(url=qdrant_url)
        super().__init__(movies_repository)

    async def get_recommendations_by_movie(self, embedding: list[float], id:int) -> list[MovieDetails]:
        """
        Get a list of recommended movies based on a given movie from TMDB.

        Args:
            movie (Movie): The movie for which recommendations are to be fetched.

        Returns:
            list[Movie]: A list of recommended movies.
        """
        
        try:

            # Get recommendations from Qdrant
            recommended_ids = self.qdrant_client.get_recommendations(
                collection_name="movies",
                embedding=embedding,
                id=id,
                limit=10

            )

            # Fetch movie details from TMDB
            tasks = [
                self.movies_repository.get_movie_by_id(movie_id[0])
                for movie_id in recommended_ids
            ]

            recommendations = await asyncio.gather(*tasks)

            

            response = [
                MovieRecommendation(
                    movie=movie,
                    similarity_score=movie_id[1]
                ) for movie, movie_id in zip(recommendations, recommended_ids) if movie is not None
            ]

            return response
        except Exception as e:
            raise Exception(f"Error fetching recommendations: {str(e)}")