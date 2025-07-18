from pydantic import BaseModel
from db.movies import Movie as MovieModel, Genre as GenreModel

class Movie(BaseModel):
    """
    Movie model representing a movie entity.
    """
    id: int
    title: str
    release_date: str | None = None  # Optional field for release date
    poster_path: str | None = None  # Optional field for poster image
    certification: str

    @staticmethod
    def from_dict(data: dict):
        """
        Create a Movie instance from a dictionary.
        
        Args:
            data (dict): Dictionary containing movie data.
        
        Returns:
            Movie: An instance of the Movie class.
        """
        return Movie(
            id=data.get('id'),
            title=data.get('title'),
            release_date=data.get('release_date'),
            poster_path=data.get('poster_path'),
            certification=data.get('certification', 'N/A')  # Default to 'N/A' if not provided
        )
    
    @staticmethod
    def from_dict_list(data_list: list):
        """
        Create a list of Movie instances from a list of dictionaries.
        
        Args:
            data_list (list): List of dictionaries containing movie data.
        
        Returns:
            list: A list of Movie instances.
        """
        return [Movie.from_dict(data) for data in data_list] if data_list else []
    
    def from_db_model(db_model: MovieModel):
        """
        Create a Movie instance from a database model.
        
        Args:
            db_model (MovieModel): Database model instance.
        
        Returns:
            Movie: An instance of the Movie class.
        """
        return Movie(
            id=db_model.id,
            title=db_model.title,
            release_date=db_model.release_date.isoformat() if db_model.release_date else None,
            poster_path=db_model.poster_path,
            certification=db_model.certification.certification if db_model.certification else 'N/A'  # Default to 'N/A' if not provided
        )
    
    def from_db_model_list(db_model_list: list):
        """
        Create a list of Movie instances from a list of database models.
        
        Args:
            db_model_list (list): List of database model instances.
        
        Returns:
            list: A list of Movie instances.
        """
        return [Movie.from_db_model(db_model) for db_model in db_model_list] if db_model_list else []

class MovieDetails(BaseModel):
    """
    Movie model representing a movie entity.
    """
    id: int
    title: str
    overview: str
    release_date: str | None = None
    poster_path: str | None = None  # Optional field for poster image
    backdrop_path: str | None = None  # Optional field for backdrop image
    genres: list[str] = []  # List of genre names associated with the movie
    certification: str

    @staticmethod
    def from_dict(data: dict):
        """
        Create a Movie instance from a dictionary.
        
        Args:
            data (dict): Dictionary containing movie data.
        
        Returns:
            Movie: An instance of the Movie class.
        """
        return MovieDetails(
            id=data.get('id'),
            title=data.get('title'),
            overview=data.get('overview'),
            release_date=data.get('release_date'),
            poster_path=data.get('poster_path'),
            backdrop_path=data.get('backdrop_path', None),  # Optional field
            genres=data.get('genres', []),  # List of genre names
            certification=data.get('certification', 'N/A')  # Default to 'N/A' if not provided
        )
    
    @staticmethod
    def from_dict_list(data_list: list):
        """
        Create a list of Movie instances from a list of dictionaries.
        
        Args:
            data_list (list): List of dictionaries containing movie data.
        
        Returns:
            list: A list of Movie instances.
        """
        return [MovieDetails.from_dict(data) for data in data_list] if data_list else []
    
    def from_db_model(db_model: MovieModel):
        """
        Create a Movie instance from a database model.
        
        Args:
            db_model (MovieModel): Database model instance.
        
        Returns:
            Movie: An instance of the Movie class.
        """
        return MovieDetails(
            id=db_model.id,
            title=db_model.title,
            overview=db_model.overview,
            release_date=db_model.release_date.isoformat() if db_model.release_date else None,
            poster_path=db_model.poster_path,
            backdrop_path=db_model.backdrop_path if db_model.backdrop_path else None,  # Optional field
            genres=[genre.name for genre in db_model.genres] if db_model.genres else [],  # List of genre names
            certification=db_model.certification.certification if db_model.certification else 'N/A'  # Default to 'N/A' if not provided
        )
    
    def from_db_model_list(db_model_list: list):
        """
        Create a list of Movie instances from a list of database models.
        
        Args:
            db_model_list (list): List of database model instances.
        
        Returns:
            list: A list of Movie instances.
        """
        return [MovieDetails.from_db_model(db_model) for db_model in db_model_list] if db_model_list else []
    
class MovieRecommendation(BaseModel):
    """
    MovieRecommendation model representing a movie recommendation entity.
    """
    movie: Movie
    similarity_score: float


    @staticmethod
    def from_dict(data: dict):
        """
        Create a MovieRecommendation instance from a dictionary.
        
        Args:
            data (dict): Dictionary containing movie recommendation data.
        
        Returns:
            MovieRecommendation: An instance of the MovieRecommendation class.
        """
        return MovieRecommendation(
            movie=Movie.from_dict(data.get('movie')),
            similarity_score=data.get('similarity_score', 0.0),
        )
    
    @staticmethod
    def from_dict_list(data_list: list):
        """
        Create a list of MovieRecommendation instances from a list of dictionaries.
        
        Args:
            data_list (list): List of dictionaries containing movie recommendation data.
        
        Returns:
            list: A list of MovieRecommendation instances.
        """
        return [MovieRecommendation.from_dict(data) for data in data_list] if data_list else []
    
    def from_db_model(db_model: MovieModel, similarity_score: float):
        """
        Create a MovieRecommendation instance from a database model and similarity score.
        
        Args:
            db_model (MovieModel): Database model instance.
            similarity_score (float): Similarity score for the recommendation.
        
        Returns:
            MovieRecommendation: An instance of the MovieRecommendation class.
        """
        return MovieRecommendation(
            movie=Movie.from_db_model(db_model),
            similarity_score=similarity_score,
        )
    
    def from_db_model_list(db_model_list: list, similarity_scores: list):
        """
        Create a list of MovieRecommendation instances from a list of database models and similarity scores.
        
        Args:
            db_model_list (list): List of database model instances.
            similarity_scores (list): List of similarity scores for the recommendations.
        
        Returns:
            list: A list of MovieRecommendation instances.
        """
        return [MovieRecommendation.from_db_model(db_model, score) for db_model, score in zip(db_model_list, similarity_scores)] if db_model_list else []
    
class MovieRecommendationResponse(BaseModel):
    """
    MovieRecommendationResponse model representing a response containing movie recommendations.
    """
    results: list[MovieRecommendation]
    searched_movie: MovieDetails