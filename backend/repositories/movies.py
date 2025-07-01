from abc import ABC, abstractmethod
from models.pagination import Pagination, PaginatedResponse
import requests
import os

class MoviesRepository(ABC):
    def __init__(self, db):
        self.db = db
    @abstractmethod
    async def get_popular_movies(self, pagination: Pagination) -> PaginatedResponse:
        """
        Get a paginated list of popular movies from the database.

        Args:
            pagination (Pagination): Pagination parameters including page and page_size.

        Returns:
            PaginatedResponse: A paginated response containing total count, current page, page size, and items.
        """
        pass

class MoviesRepositoryTMDB(MoviesRepository):
    url = "https://api.themoviedb.org/3/"
    async def get_popular_movies(self, pagination: Pagination) -> PaginatedResponse:
        """
        Get a paginated list of popular movies from TMDB.

        Args:
            pagination (Pagination): Pagination parameters including page and page_size.

        Returns:
            PaginatedResponse: A paginated response containing total count, current page, page size, and items.
        """
        # Load the API key from environment variables
        api_key = os.getenv("TMDB_API_KEY")
        if not api_key:
            raise Exception("TMDB API key not found in environment variables.")
        
        params = {
            "language": "es",
            "page": pagination.page,
            "api_key": api_key,
        }
        
        response = requests.get(f"{self.url}movie/popular", params=params)
        
        if response.status_code == 200:
            data = response.json()
            return PaginatedResponse(
                total_count=data['total_results'],
                current_page=pagination.page,
                page_size=pagination.page_size,
                items=data['results']
            )
        else:
            raise Exception(f"Error fetching popular movies: {response.status_code} - {response.text}")
        