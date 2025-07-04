// Use tailwindcss for styling
import { useInfiniteQuery } from "@tanstack/react-query";
import { motion } from "motion/react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { Movie } from "./models/movie";
import {
  CustomApiMovieRepository,
  type MovieRepository,
} from "./repositories/movie";

interface MovieCardProps {
  movie: Movie;
  index: number;
}

const MovieCard = ({
  movie: { title, poster_path: backdrop_path },
  index,
}: MovieCardProps) => {
  console.log(index);
  const [loaded, setLoaded] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  return (
    <motion.div
      ref={ref}
      className={`relative aspect-[2/3] overflow-hidden shadow-lg bg-[#181a36] group-hover:blur-sm hover:!blur-none transition-all duration-300 ease-in-out cursor-pointer`}
      style={{ borderRadius: "0.5rem" }}
      whileHover={{ scale: 1.05, borderRadius: "1rem" }}
    >
      {!loaded && (
        <div className="absolute inset-0 bg-[#2c2e4f] animate-pulse rounded-md" />
      )}

      <img
        src={`https://image.tmdb.org/t/p/original${backdrop_path}`}
        alt={`${title} poster`}
        className={`w-full h-full object-cover transition-opacity duration-500 ${
          loaded ? "opacity-100" : "opacity-0"
        }`}
        onLoad={() => setLoaded(true)}
      />

      <div className="absolute inset-0 p-2 bg-gradient-to-t from-black via-transparent to-transparent opacity-0 hover:opacity-100 transition-opacity">
        <div className="absolute bottom-0 p-4 text-white">
          <h3 className="font-bold text-lg">{title}</h3>
        </div>
      </div>
    </motion.div>
  );
};

const useInfiniteScroll = (callback: () => void) => {
  useEffect(() => {
    const handleScroll = () => {
      if (
        window.innerHeight + window.scrollY >=
        document.body.offsetHeight - 100
      ) {
        callback(); // Llama a la función para cargar más
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [callback]);
};

function App() {
  const repository = useRef<MovieRepository>(new CustomApiMovieRepository());

  const { data, fetchNextPage, isFetchingNextPage } = useInfiniteQuery({
    queryKey: ["projects"],
    queryFn: ({ pageParam = 1 }) => {
      return repository.current.fetchMovies(pageParam);
    },
    initialPageParam: 1,
    getNextPageParam: (lastPage, allPages, lastPageParam) => {
      if (lastPageParam >= 500) return undefined; // Limita a 500 páginas
      return lastPageParam + 1;
    },
  });

  useInfiniteScroll(() => {
    fetchNextPage();
  });

  if (!data) {
    return <div className="text-white text-center p-4">Loading...</div>;
  }

  const allMovies = data.pages.flat();

  return (
    <>
      <div
        className="flex flex-col w-full min-h-screen bg-gray-100"
        style={{ backgroundColor: "#181a36" }}
      >
        <header className="text-white p-4 h-20 sticky top-0 z-10 bg-[#181a36] shadow-md flex flex-row items-center">
          <img
            src="/icon.png"
            alt="Logo"
            style={{
              height: "100%",
              aspectRatio: "1/1",
              marginRight: "0.75rem",
            }}
          />
          <h1 className="text-3xl font-bold">Mi Siguiente Película</h1>
        </header>
        <main
          className="grid grid-cols-2 p-6 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-8 group"
          style={{ backgroundColor: "#181a36" }}
        >
          {/* Using motion.div for animation effects */}
          {allMovies.map((movie, index) => (
            <MovieCard key={index} movie={movie} index={index} />
          ))}
        </main>
        {isFetchingNextPage && (
          <div className="text-white text-center p-4">
            Cargando más películas...
          </div>
        )}
      </div>
    </>
  );
}

export default App;
