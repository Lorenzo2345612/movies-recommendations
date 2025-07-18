import { useRef } from "react";
import {
  CustomApiMovieRepository,
  type MovieRepository,
} from "../repositories/movie";
import { useQuery } from "@tanstack/react-query";
import { useFilters } from "./useFilters";

export const useGetMovie = (id: string | undefined) => {
  const repository = useRef<MovieRepository>(new CustomApiMovieRepository());
  const filters = useFilters();

  const { data, isLoading, error } = useQuery({
    queryKey: ["movie", id, filters.filters.certification],
    queryFn: async () => {
      if (!id) {
        throw new Error("Movie ID is required");
      }
      const maximumCertification = filters.filters.certification || undefined;
      return await repository.current.fetchMovieById(id, maximumCertification);
    },
  });

  return { data, isLoading, error };
};
