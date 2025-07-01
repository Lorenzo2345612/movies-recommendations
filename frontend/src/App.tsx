// Use tailwindcss for styling
import { motion } from "motion/react";
import { use, useCallback, useEffect, useState } from "react";

interface Movie {
  title: string;
  year: number;
  poster_path: string;
  overview?: string;
}

interface MovieCardProps {
  movie: Movie;
  setHoveredIndex: (index: number) => void;
  hoveredIndex: number;
  index: number;
}

const MovieCard = ({
  movie: { title, poster_path: backdrop_path },
  setHoveredIndex,
  hoveredIndex,
  index,
}: MovieCardProps) => {
  const handleMouseEnter = () => {
    if (setHoveredIndex) {
      setHoveredIndex(index);
    }
  };
  const handleMouseLeave = () => {
    if (setHoveredIndex) {
      setHoveredIndex(-1);
    }
  };

  const bluredClasses =
    hoveredIndex != -1 && hoveredIndex !== index ? "blur-sm brightness-75" : "";

  return (
    <motion.div
      className={`relative aspect-[2/3] overflow-hidden shadow-lg bg-slate-400 ${bluredClasses} transition-all duration-300 ease-in-out cursor-pointer`}
      style={{
        borderRadius: "0.5rem",
      }}
      whileHover={{ scale: 1.05, borderRadius: "1rem" }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <img
        src={`https://image.tmdb.org/t/p/original${backdrop_path}`}
        alt={`${title} poster`}
        className="w-full h-full object-cover"
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
  const [movies, setMovies] = useState<Movie[]>([]);
  const [hoveredIndex, setHoveredIndex] = useState<number>(-1);
  const [page, setPage] = useState<number>(1);

  const fetchMovies = useCallback(async () => {
    try {
      const url = `https://api.themoviedb.org/3/movie/popular?api_key=e6a366c561d20cfdccb9ee9c4c4765a8&language=es&page=${page}`;
      const options = {
        method: "GET",
        headers: { accept: "application/json" },
      };

      const response = await fetch(url, options);
      const data = await response.json();
      setMovies((prevMovies) => [...prevMovies, ...data.results]);
    } catch (error) {
      console.error("Error fetching movies:", error);
    }
  }, [page]);

  useInfiniteScroll(() => {
    setPage((prevPage) => prevPage + 1);
  });

  useEffect(() => {
    fetchMovies();
  }, [fetchMovies]);

  return (
    <>
      <div
        className="flex flex-col w-full min-h-screen bg-gray-100"
        style={{ backgroundColor: "#181a36" }}
      >
        <header className="text-white p-4 text-center h-16">
          <h1 className="text-2xl font-bold">Movie List</h1>
        </header>
        <main
          className="grid grid-cols-2 p-6 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-8"
          style={{ backgroundColor: "#181a36" }}
        >
          {/* Using motion.div for animation effects */}
          {movies.map((movie, index) => (
            <MovieCard
              key={index}
              movie={movie}
              index={index}
              hoveredIndex={hoveredIndex}
              setHoveredIndex={setHoveredIndex}
            />
          ))}
        </main>
      </div>
    </>
  );
}

export default App;
