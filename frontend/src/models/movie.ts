export interface Movie {
  id: string;
  title: string;
  year: number;
  poster_path: string;
  backdrop_path: string;
  overview?: string;
  genres: string[];
  certification: string;
}

export interface MovieRecomendation {
  searched_movie: Movie;
  results: {
    similarity_score: number;
    movie: Movie;
  }[];
}
