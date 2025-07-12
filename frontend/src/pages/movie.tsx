import { useQuery } from "@tanstack/react-query";
import { useRef, useState } from "react";
import { useNavigate, useParams } from "react-router";
import {
  CustomApiMovieRepository,
  type MovieRepository,
} from "../repositories/movie";
import { motion, useScroll, useTransform } from "motion/react";
import { MovieCard } from "../components/movie_card.component";
import { MdHome } from "react-icons/md";
import { Footer } from "../components/footer.component";

const useGetMovie = (id: string | undefined) => {
  const repository = useRef<MovieRepository>(new CustomApiMovieRepository());

  const { data, isLoading, error } = useQuery({
    queryKey: ["movie", id],
    queryFn: async () => {
      if (!id) {
        throw new Error("Movie ID is required");
      }
      return await repository.current.fetchMovieById(id);
    },
  });

  return { data, isLoading, error };
};

interface MovieOverviewProps {
  title: string;
  overview?: string;
}

const MovieOverview = ({ title, overview }: MovieOverviewProps) => {
  const [isOverviewExpaned, setIsOverviewExpanded] = useState(false);
  return (
    <motion.div
      layout
      className="flex flex-col text-white gap-[10%] p-2 sm:p-4 md:p-8 lg:gap-[20%] lg:p-12 w-full h-screen sm:w-[80%] max-h-screen"
    >
      <motion.div layout className="flex-1"></motion.div>
      <motion.h1
        layout
        className="font-bold text-4xl sm:text-6xl md:text-6xl lg:text-7xl flex-2"
      >
        {title}
      </motion.h1>
      {overview ? (
        overview.length > 150 ? (
          <motion.div layout className="flex flex-col gap-4 items-start flex-3">
            <motion.p
              layout
              className={`text-lg sm:text-sm md:text-lg lg:text-xl ${
                isOverviewExpaned ? "line-clamp-none" : "line-clamp-3"
              }`}
            >
              {overview}
            </motion.p>
            <motion.button
              layout
              onClick={() => setIsOverviewExpanded(!isOverviewExpaned)}
              className="text-blue-500 hover:underline"
            >
              {isOverviewExpaned ? "Ver menos" : "Ver más"}
            </motion.button>
          </motion.div>
        ) : (
          <motion.div className="flex flex-col gap-4 items-start flex-3">
            <motion.p className="text-lg sm:text-xl md:text-2xl lg:text-3xl">
              {overview}
            </motion.p>
          </motion.div>
        )
      ) : (
        <motion.div className="flex flex-col gap-4 items-start flex-3">
          <p className="text-lg sm:text-xl md:text-2xl lg:text-3xl"></p>
        </motion.div>
      )}
    </motion.div>
  );
};

export const MoviePage = () => {
  const { id } = useParams();
  const { data, isLoading, error } = useGetMovie(id);
  const scrollRef = useScroll();
  const opacity = useTransform(scrollRef.scrollYProgress, [0, 1], [1, 0.7]);
  const imageScale = useTransform(scrollRef.scrollYProgress, [0, 1], [1.05, 1]);

  const navigator = useNavigate();
  if (!id) {
    return (
      <div className="text-white text-center p-4">Movie ID not found.</div>
    );
  }
  return (
    <div className="w-full bg-[#181a36]">
      {/* Home icon to go back to home page top-rigth corner*/}
      <MdHome
        className="text-white text-3xl fixed top-4 right-4 cursor-pointer hover:text-blue-500 transition-colors z-10"
        onClick={() => navigator("/", { replace: true })}
      />
      {isLoading && (
        <div className="text-white text-center p-4 h-screen">Loading...</div>
      )}
      {error && (
        <div className="text-red-500 text-center p-4 h-screen">
          Error: {error.message}
        </div>
      )}
      {data && (
        // Full page banner with movie details
        <div className="flex flex-col items-center">
          <motion.img
            src={`https://image.tmdb.org/t/p/original${data.searched_movie.backdrop_path}`}
            alt={`${data.searched_movie.title} poster`}
            initial={{ scale: 1.05 }}
            style={{ scale: imageScale }}
            className="w-full h-full object-cover filter-blur-sm fixed inset-0"
          />
          {/*Left gradient overlay*/}
          <motion.div
            style={{ opacity, position: "fixed" }}
            initial={{ opacity: 1 }}
            className="w-full h-full bg-gradient-to-r from-black to-transparent"
          />

          <div className="w-full relative px-4 sm:px-8 md:px-12 lg:px-16">
            <MovieOverview
              overview={data.searched_movie.overview}
              title={data.searched_movie.title}
            />
            {data.results.length > 0 && (
              <div className="flex flex-col">
                <h3 className="text-white text-2xl font-bold mb-4">
                  Recomendaciones
                </h3>
                {/* Horizontal carousel of movie recomendations */}
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-8">
                  {data.results.map((movie, index) => (
                    <MovieCard
                      key={index}
                      movie={movie.movie}
                      index={index}
                      similarity={movie.similarity_score * 100}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      <Footer />
    </div>
  );
};
