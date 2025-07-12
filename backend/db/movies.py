from sqlalchemy import Column, Integer, String, Float, Date, Table, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from db.db import Base

movie_genre = Table(
    'movie_genre',
    Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id')),
    Column('genre_id', Integer, ForeignKey('genres.id'))
)

class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    overview = Column(String)
    release_date = Column(Date, nullable=True)
    popularity = Column(Float)
    vote_average = Column(Float)
    vote_count = Column(Integer)
    poster_path = Column(String, nullable=True)
    backdrop_path = Column(String, nullable=True)
    embeddings = Column(String, nullable=True)

    genres = relationship("Genre", secondary=movie_genre, back_populates="movies")

class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    movies = relationship("Movie", secondary=movie_genre, back_populates="genres")
