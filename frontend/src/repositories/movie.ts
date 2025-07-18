import type { Movie, MovieRecomendation } from "../models/movie";

export abstract class MovieRepository {
  abstract fetchMovies(
    page: number,
    filters?: {
      genre?: string[];
      certification?: string | null;
    }
  ): Promise<Movie[]>;
  abstract fetchMovieById(
    id: string,
    maximum_certification?: string
  ): Promise<MovieRecomendation>;
}

export class CustomApiMovieRepository extends MovieRepository {
  async fetchMovies(
    page: number,
    filters: { genre?: string[]; certification?: string | null } = {}
  ): Promise<Movie[]> {
    //
    try {
      console.log("Fetching movies from custom API with filters:", filters);
      const reqGenres = filters.genre || [];
      const reqCertification = filters.certification || "";
      const body = {
        page,
        page_size: 20,
        genres: reqGenres,
        maximum_certification: reqCertification,
      };

      const url = `${import.meta.env.VITE_API_URL}/movies`;

      const options = {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
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

  async fetchMovieById(
    id: string,
    maximum_certification?: string
  ): Promise<MovieRecomendation> {
    try {
      const url = `${
        import.meta.env.VITE_API_URL
      }/movies/${id}?maximum_certification=${maximum_certification || ""}`;

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
