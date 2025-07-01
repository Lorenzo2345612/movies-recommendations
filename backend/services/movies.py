from models.pagination import Pagination, PaginatedResponse

class MovieService:
    def __init__(self, movie_repository):
        self.movie_repository = movie_repository

    def get_popular_movies(self, pagination):
        """
        Get a paginated list of popular movies.

        Args:
            pagination (Pagination): Pagination parameters including page and page_size.

        Returns:
            PaginatedResponse: A paginated response containing total count, current page, page size, and items.
        """
        return self.movie_repository.get_popular_movies(pagination)