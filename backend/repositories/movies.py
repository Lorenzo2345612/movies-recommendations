from abc import ABC, abstractmethod
import requests
import os
from models.movie import MovieDetails, Movie
from db.movies import Certification, Movie as MovieModel, Genre as GenreModel
from db.db import SessionLocal
from models.pagination import Pagination, PaginatedResponse
from sqlalchemy import select, func

class MoviesRepository(ABC):

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

    @abstractmethod
    async def get_movie_details_by_id(self, movie_id: int) -> MovieDetails:
        """
        Get a movie by its ID.

        Args:
            movie_id (int): The ID of the movie to retrieve.

        Returns:
            Movie: An instance of the Movie class containing movie details.
        """
        pass

    @abstractmethod
    async def get_movie_by_id(self, movie_id: int, maximum_certification: str = None) -> Movie:
        """
        Get a movie by its ID.

        Args:
            movie_id (int): The ID of the movie to retrieve.
            maximum_certification (str, optional): The maximum certification to filter movies.

        Returns:
            Movie: An instance of the Movie class containing movie details.
        """
        pass

    @abstractmethod
    async def get_embedding_by_id(self, movie_id: int) -> list:
        """
        Get the embedding of a movie by its ID.

        Args:
            movie_id (int): The ID of the movie to retrieve the embedding for.

        Returns:
            list: A list containing the embedding of the movie.
        """
        pass

class MoviesRepositoryLocal(MoviesRepository):
    def __init__(self):
        self.session = SessionLocal()

    async def get_popular_movies(self, pagination: Pagination) -> PaginatedResponse:
        """
        Get a paginated list of popular movies from the local database.

        Args:
            pagination (Pagination): Pagination parameters including page and page_size.

        Returns:
            PaginatedResponse: A paginated response containing total count, current page, page size, and items.
        """
        query = self.session.query(MovieModel).order_by(MovieModel.popularity.desc())
        # Apply genre filtering if provided
        if pagination.genres:
            num_genres = len(pagination.genres)

            query = (
                query
                .join(MovieModel.genres)
                .filter(GenreModel.name.in_(pagination.genres))
                .group_by(MovieModel.id)
                .having(func.count(func.distinct(GenreModel.name)) == num_genres)
    )
        # Apply certification filtering if provided
        if pagination.maximum_certification:
            subquery = select(Certification.min_age).where(
                Certification.certification == pagination.maximum_certification
            ).scalar_subquery()
            query = query.join(MovieModel.certification).filter(
                MovieModel.certification.has(Certification.min_age <= subquery)
            )
        
        total_count = query.count()
        total_pages = (total_count + pagination.page_size - 1) // pagination.page_size

        print(f"Certification filter: {pagination.maximum_certification}")
        print(f"Genre filter: {pagination.genres}")

        print(f"Fetching popular movies from local database: Total count = {total_count}, Page = {pagination.page}, Page Size = {pagination.page_size} , Total Pages = {total_pages}")
        
        items = query.offset((pagination.page - 1) * pagination.page_size).limit(pagination.page_size).all()
        
        return PaginatedResponse(
            total=total_count,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
            items=Movie.from_db_model_list(items) if items else []
        )

    async def get_movie_details_by_id(self, movie_id: int) -> MovieDetails:
        """
        Get a movie by its ID from the local database.

        Args:
            movie_id (int): The ID of the movie to retrieve.

        Returns:
            Movie: An instance of the Movie class containing movie details.
        """
        model = self.session.query(MovieModel).filter(MovieModel.id == movie_id).first()
        if model:
            return MovieDetails.from_db_model(model)
        else:
            return None
        
    async def get_movie_by_id(self, movie_id: int, maximum_certification: str = None) -> Movie:
        """
        Get a movie by its ID from the local database.

        Args:
            movie_id (int): The ID of the movie to retrieve.

        Returns:
            Movie: An instance of the Movie class containing movie details.
        """
        query = self.session.query(MovieModel).filter(MovieModel.id == movie_id)
        # Apply certification filtering if provided
        if maximum_certification:
            subquery = select(Certification.min_age).where(
                Certification.certification == maximum_certification
            ).scalar_subquery()
            query = query.join(MovieModel.certification).filter(
                MovieModel.certification.has(Certification.min_age <= subquery)
            )
        model = query.first()
        if model:
            return Movie.from_db_model(model)
        else:
            return None
        
    async def get_embedding_by_id(self, movie_id: int) -> list:
        """
        Get the embedding of a movie by its ID from the local database.

        Args:
            movie_id (int): The ID of the movie to retrieve the embedding for.

        Returns:
            list: A list containing the embedding of the movie.
        """
        model = self.session.query(MovieModel).filter(MovieModel.id == movie_id).first()
        if model:
            return eval(model.embeddings) if model.embeddings else []
        else:
            raise Exception(f"Movie with ID {movie_id} not found in the local database.")

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

        print(f"Fetching popular movies from TMDB: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            return PaginatedResponse(
                total=data['total_results'],
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=data['total_pages'],
                items=MovieDetails.from_dict_list(data['results'])
            )
        else:
            raise Exception(f"Error fetching popular movies: {response.status_code} - {response.text}")
        
    async def get_movie_details_by_id(self, movie_id: int) -> MovieDetails:
        """
        Get a movie by its ID from TMDB.

        Args:
            movie_id (int): The ID of the movie to retrieve.

        Returns:
            Movie: An instance of the Movie class containing movie details.
        """
        # Load the API key from environment variables
        api_key = os.getenv("TMDB_API_KEY")
        if not api_key:
            raise Exception("TMDB API key not found in environment variables.")
        
        params = {
            "language": "es",
            "api_key": api_key,
        }
        
        response = requests.get(f"{self.url}movie/{movie_id}", params=params)

        print(f"Fetching movie by ID {movie_id} from TMDB: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            return MovieDetails.from_dict(data)
        else:
            raise Exception(f"Error fetching movie by ID {movie_id}: {response.status_code} - {response.text}")
        
    async def get_embedding_by_id(self, movie_id: int) -> list:
        """
        Get the embedding of a movie by its ID from TMDB.

        Args:
            movie_id (int): The ID of the movie to retrieve the embedding for.

        Returns:
            list: A list containing the embedding of the movie.
        """
        # TMDB does not provide embeddings, so this method is not applicable.
        raise NotImplementedError("TMDB does not provide embeddings for movies.")
    
    async def get_movie_by_id(self, movie_id: int) -> Movie:
        """
        Get a movie by its ID from TMDB.

        Args:
            movie_id (int): The ID of the movie to retrieve.

        Returns:
            Movie: An instance of the Movie class containing movie details.
        """
        # Load the API key from environment variables
        api_key = os.getenv("TMDB_API_KEY")
        if not api_key:
            raise Exception("TMDB API key not found in environment variables.")
        
        params = {
            "language": "es",
            "api_key": api_key,
        }
        
        response = requests.get(f"{self.url}movie/{movie_id}", params=params)

        print(f"Fetching movie by ID {movie_id} from TMDB: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            return Movie.from_dict(data)
        else:
            raise Exception(f"Error fetching movie by ID {movie_id}: {response.status_code} - {response.text}")
        