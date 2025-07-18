import { useRef, useState } from "react";
import type { Movie } from "../models/movie";
import { motion } from "motion/react";
import { useNavigate } from "react-router";

interface MovieCardProps {
  movie: Movie;
  index: number;
  similarity?: number;
  certification: string;
}

export const MovieCard = ({
  movie: { title, poster_path: backdrop_path, id },
  similarity,
  index,
  certification,
}: MovieCardProps) => {
  const [loaded, setLoaded] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/movie/${id}`);
  };

  return (
    <motion.div
      ref={ref}
      className={`movie-card relative aspect-[2/3] overflow-hidden shadow-lg bg-[#181a36] transition-all duration-300 ease-in-out cursor-pointer`}
      style={{ borderRadius: "0.5rem" }}
      whileHover={{ scale: 1.05, borderRadius: "1rem" }}
      onClick={handleClick}
      key={`movie-card-${index}`}
    >
      {!loaded && (
        <div className="absolute inset-0 bg-[#2c2e4f] animate-pulse rounded-md" />
      )}

      {/* Display a triangle in the top right corner if similarity is provided */}
      {similarity && (
        <div className="absolute top-2 right-2 bg-blue-500 text-white text-xs px-2 py-1 rounded">
          Parecido: {similarity.toFixed(2)}%
        </div>
      )}
      {/* Display a triangle in the top left corner if certification is provided */}
      <div className="absolute top-2 left-2 bg-[#181a36] text-white text-xs px-2 py-1 rounded">
        {certification}
      </div>

      {/* Movie poster image */}

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
