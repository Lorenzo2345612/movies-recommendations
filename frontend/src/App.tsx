// Use tailwindcss for styling
import { useInfiniteQuery } from "@tanstack/react-query";
import { motion } from "motion/react";
import { useEffect, useState } from "react";

interface Movie {
  title: string;
  year: number;
  poster_path: string;
  overview?: string;
}

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
  const [loaded, setLoaded] = useState(false);

  const handleMouseEnter = () => {
    if (setHoveredIndex) setHoveredIndex(index);
  };

  const handleMouseLeave = () => {
    if (setHoveredIndex) setHoveredIndex(-1);
  };

  const bluredClasses =
    hoveredIndex != -1 && hoveredIndex !== index ? "blur-sm brightness-75" : "";

  return (
    <motion.div
      className={`relative aspect-[2/3] overflow-hidden shadow-lg bg-[#181a36] ${bluredClasses} transition-all duration-300 ease-in-out cursor-pointer`}
      style={{ borderRadius: "0.5rem" }}
      whileHover={{ scale: 1.05, borderRadius: "1rem" }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
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
  const [hoveredIndex, setHoveredIndex] = useState<number>(-1);

  const { data, fetchNextPage } = useInfiniteQuery({
    queryKey: ["projects"],
    queryFn: fetchMovies,
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
          className="grid grid-cols-2 p-6 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-8"
          style={{ backgroundColor: "#181a36" }}
        >
          {/* Using motion.div for animation effects */}
          {allMovies.map((movie, index) => (
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
