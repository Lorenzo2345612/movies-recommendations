from models.pagination import Pagination, PaginatedResponse
from repositories.movies import MoviesRepository
from repositories.recommendations import RecommendationsRepositoryTMDB
from models.movie import MovieRecommendationResponse

class MovieService:
    def __init__(self, movie_repository: MoviesRepository):
        self.movie_repository = movie_repository
        self.recommendations_repository = RecommendationsRepositoryTMDB(movie_repository)

    async def get_popular_movies(self, pagination):
        """
        Get a paginated list of popular movies.

        Args:
            pagination (Pagination): Pagination parameters including page and page_size.

        Returns:
            PaginatedResponse: A paginated response containing total count, current page, page size, and items.
        """
        return await self.movie_repository.get_popular_movies(pagination)
    
    async def get_movie_by_id(self, movie_id: int, maximum_certification: str = None):
        """
        Get a movie by its ID.

        Args:
            movie_id (int): The ID of the movie to retrieve.

        Returns:
            Movie: An instance of the Movie class containing movie details.
        """
        try:
            movie = await self.movie_repository.get_movie_details_by_id(movie_id)
            embedding = await self.movie_repository.get_embedding_by_id(movie_id)
            if not movie:
                raise ValueError(f"Movie with ID {movie_id} not found.")
            recommended_movies = await self.recommendations_repository.get_recommendations_by_movie(embedding, movie_id, maximum_certification)

            return MovieRecommendationResponse(
                results=recommended_movies,
                searched_movie=movie
            )
        except Exception as e:
            raise Exception(f"Error fetching movie by ID {movie_id}: {str(e)}")
