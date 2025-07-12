import type { Movie, MovieRecomendation } from "../models/movie";

export abstract class MovieRepository {
  abstract fetchMovies(page: number): Promise<Movie[]>;
  abstract fetchMovieById(id: string): Promise<MovieRecomendation>;
}

export class CustomApiMovieRepository extends MovieRepository {
  async fetchMovies(page: number): Promise<Movie[]> {
    try {
      const body = JSON.stringify({ page, page_size: 20 });
      const url = `${import.meta.env.VITE_API_URL}/movies`;

      const options = {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body,
      };

      const response = await fetch(url, options);

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const data = await response.json();
      return data.items as Movie[];
    } catch {
      throw new Error("Failed to fetch movies from custom API");
    }
  }

  async fetchMovieById(id: string): Promise<MovieRecomendation> {
    try {
      const url = `${import.meta.env.VITE_API_URL}/movies/${id}`;

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const data = await response.json();
      return data as MovieRecomendation;
    } catch {
      throw new Error("Failed to fetch movie by ID from custom API");
    }
  }
}
