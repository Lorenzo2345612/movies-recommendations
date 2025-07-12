import { Footer } from "../components/footer.component";
import { MovieCard } from "../components/movie_card.component";
import { usePaginateMovies } from "../hooks/usePaginateMovies";

export const IndexPage = () => {
  const { data, isFetchingNextPage } = usePaginateMovies();

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
            <MovieCard key={index} movie={movie} index={index} />
          ))}
        </main>
        {isFetchingNextPage && (
          <div className="text-white text-center p-4">
            Cargando más películas...
          </div>
        )}
        <Footer />
      </div>
    </>
  );
};
