import { useInfiniteQuery } from "@tanstack/react-query";
import {
  CustomApiMovieRepository,
  type MovieRepository,
} from "../repositories/movie";
import { useInfiniteScroll } from "./useInfiniteScroll";
import { useRef } from "react";

export const usePaginateMovies = () => {
  const repository = useRef<MovieRepository>(new CustomApiMovieRepository());

  const { data, fetchNextPage, isFetchingNextPage } = useInfiniteQuery({
    queryKey: ["projects"],
    queryFn: ({ pageParam = 1 }) => {
      return repository.current.fetchMovies(pageParam);
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

  return {
    data,
    isFetchingNextPage,
  };
};
