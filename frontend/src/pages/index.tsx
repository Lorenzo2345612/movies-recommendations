import { FiltersComponent } from "../components/filters.component";
import { Footer } from "../components/footer.component";
import { FullPageLoader } from "../components/full_page_loader.component";
import { MovieCard } from "../components/movie_card.component";
import { usePaginateMovies } from "../hooks/usePaginateMovies";

export const IndexPage = () => {
  const {
    data,
    isFetchingNextPage,
    onSearch,
    isFiltersOpen,
    setIsFiltersOpen,
    isLoading,
  } = usePaginateMovies();

  if (!data) {
    return <div className="text-white text-center p-4">Loading...</div>;
  }

  if (isLoading) {
    return <FullPageLoader></FullPageLoader>;
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
          <button
            onClick={() => setIsFiltersOpen(!isFiltersOpen)}
            className="ml-auto bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2 px-4 rounded-lg transition"
            aria-label="Abrir filtros"
          >
            Filtros
          </button>
        </header>
        {/* Filters and Search Bar can be added here */}
        <FiltersComponent
          isClosed={isFiltersOpen}
          onClose={() => setIsFiltersOpen(false)}
          onSearch={onSearch}
        />

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
              certification={movie.certification}
            />
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
