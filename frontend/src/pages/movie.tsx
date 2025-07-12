import { motion, useScroll, useTransform } from "motion/react";
import { MovieCard } from "../components/movie_card.component";
import { MdHome } from "react-icons/md";
import { Footer } from "../components/footer.component";
import { FullPageLoader } from "../components/full_page_loader.component";
import { useGetMovie } from "../hooks/useGetMovie";
import { useNavigate, useParams } from "react-router";
import { MovieOverview } from "../components/movie_overview.component";

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
      {isLoading && <FullPageLoader />}
      {error && (
        <div className="text-red-500 text-center p-4 h-screen">
          Error: {error.message}
        </div>
      )}
      {data && (
        // Full page banner with movie details
        <div className="flex flex-col items-center gap-3.5">
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
              genres={data.searched_movie.genres}
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
          <Footer />
        </div>
      )}
    </div>
  );
};
