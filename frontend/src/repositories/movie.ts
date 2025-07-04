import type { Movie } from "../models/movie";

/*
const fetchMovies = async ({ pageParam }) => {
  try {
    const url = `https://api.themoviedb.org/3/movie/popular?api_key=${
      import.meta.env.VITE_TMDB_API_KEY
    }&language=es&page=${pageParam}`;
    const options = {
      method: "GET",
      headers: { accept: "application/json" },
    };

    const response = await fetch(url, options);
    const data = await response.json();
    return data.results as Movie[];
  } catch (error) {
    console.error("Error fetching movies:", error);
    throw new Error("Failed to fetch movies");
  }
};

const fetchMoviesCustomApi = async (page: number) => {
  try {
    const body = JSON.stringify({
      page,
    });
    const url = `localhost:3000/api/movies`;

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
    return data.results as Movie[];
  } catch (error) {
    console.error("Error fetching movies from custom API:", error);
    throw new Error("Failed to fetch movies from custom API");
  }
};
*/

export abstract class MovieRepository {
  abstract fetchMovies(page: number): Promise<Movie[]>;
}

export class CustomApiMovieRepository extends MovieRepository {
  async fetchMovies(page: number): Promise<Movie[]> {
    try {
      const body = JSON.stringify({ page });
      const url = `http://localhost:8000/api/movies`;

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
      console.log("Fetched movies:", data.items);
      return data.items as Movie[];
    } catch (error) {
      console.error("Error fetching movies from custom API:", error);
      throw new Error("Failed to fetch movies from custom API");
    }
  }
}
