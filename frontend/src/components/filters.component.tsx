import { certifications, genres, useFilters } from "../hooks/useFilters";

interface FiltersComponentProps {
  onClose: () => void;
  isClosed: boolean;
  onSearch: () => void;
}

export const FiltersComponent = ({
  onClose,
  isClosed,
}: FiltersComponentProps) => {
  const filters = useFilters();
  return (
    isClosed && (
      <div className="fixed top-25 bg-[#1f223f] text-white p-6 rounded-2xl shadow-xl w-[90vw] sm:w-[500px] z-50 self-center sm:self-end sm:mr-3.5">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white transition"
          aria-label="Cerrar filtros"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
        <h2 className="text-2xl font-semibold mb-4">Filtros</h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Géneros */}
          <div>
            <h3 className="text-lg font-medium mb-2">Géneros</h3>
            <div className="max-h-40 overflow-y-auto pr-1 space-y-1">
              {genres.map((genre) => (
                <label
                  key={genre}
                  className="flex items-center space-x-2 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={filters.filters.genre.includes(genre)}
                    onChange={() => {
                      const selectedGenres = filters.filters.genre.includes(
                        genre
                      )
                        ? filters.filters.genre.filter((g) => g !== genre)
                        : [...filters.filters.genre, genre];

                      filters.setFilters({
                        ...filters.filters,
                        genre: selectedGenres,
                      });
                    }}
                    className="accent-purple-600"
                  />
                  <span>{genre}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Certificación */}
          <div>
            <h3 className="text-lg font-medium mb-2">Certificación</h3>
            <select
              value={filters.filters.certification || ""}
              onChange={(e) =>
                filters.setFilters({
                  ...filters.filters,
                  certification: e.target.value,
                })
              }
              className="w-full p-2 rounded bg-gray-700 border border-gray-600 focus:outline-none"
            >
              <option value="">Todos</option>
              {certifications.map((cert) => (
                <option key={cert} value={cert}>
                  {cert}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Botones */}
        <div className="flex justify-between mt-6 gap-4">
          <button
            onClick={filters.resetFilters}
            className="flex-1 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg transition"
          >
            Reiniciar
          </button>
        </div>
      </div>
    )
  );
};
