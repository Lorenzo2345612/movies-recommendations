from fastapi import APIRouter, HTTPException
from models.pagination import PaginatedResponse, Pagination
from services.movies import MovieService
from repositories.movies import MoviesRepositoryLocal
from models.movie import MovieRecommendationResponse

movies_router = APIRouter()

# Initialize the movie service with the TMDB repository
movie_service = MovieService(MoviesRepositoryLocal())


@movies_router.post("/movies", response_model=PaginatedResponse, description="Get a paginated list of movies")
async def get_movies(pagination: Pagination):
    """
    Endpoint to get a paginated list of movies.
    
    Args:
        pagination (Pagination): Pagination parameters including page and page_size.
    
    Returns:
        PaginatedResponse: A paginated response containing total count, current page, page size, and items.
    """
    try:
        return await movie_service.get_popular_movies(pagination)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching movies: {str(e)}"
        )
    
@movies_router.get("/movies/{movie_id}", response_model=MovieRecommendationResponse, description="Get movie details by ID")
async def get_movie_by_id(movie_id: int, maximum_certification: str = None):
    """
    Endpoint to get movie details by ID.
    
    Args:
        movie_id (int): The ID of the movie to retrieve.
    
    Returns:
        MovieRecommendationResponse: An object containing movie details and recommendations.

    """
    try:
        print(f"Fetching movie with ID: {movie_id} and maximum certification: {maximum_certification}")
        return await movie_service.get_movie_by_id(movie_id, maximum_certification)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching movie by ID {movie_id}: {str(e)}"
        )
    