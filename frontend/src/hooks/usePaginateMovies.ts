import { useInfiniteQuery } from "@tanstack/react-query";
import {
  CustomApiMovieRepository,
  type MovieRepository,
} from "../repositories/movie";
import { useInfiniteScroll } from "./useInfiniteScroll";
import { useRef, useState } from "react";
import { useFilters } from "./useFilters";

export const usePaginateMovies = () => {
  const repository = useRef<MovieRepository>(new CustomApiMovieRepository());
  const filtersContext = useFilters();
  const [isFiltersOpen, setIsFiltersOpen] = useState(false);

  const { data, fetchNextPage, isFetchingNextPage, refetch, isLoading } =
    useInfiniteQuery({
      queryKey: ["movies", filtersContext.filters],
      queryFn: ({ pageParam = 1 }) => {
        return repository.current.fetchMovies(pageParam, {
          genre: filtersContext.filters.genre,
          certification: filtersContext.filters.certification,
        });
      },
      initialPageParam: 1,
      getNextPageParam: (lastPage, _, lastPageParam) => {
        if (!lastPage || lastPage.length === 0) {
          return undefined;
        }
        return lastPageParam + 1;
      },
    });

  useInfiniteScroll(() => {
    fetchNextPage();
  });

  const onSearch = () => {
    refetch();
    setIsFiltersOpen(false);
  };

  return {
    data,
    isFetchingNextPage,
    isFiltersOpen,
    setIsFiltersOpen,
    onSearch,
    isLoading,
  };
};
