import { createContext, useContext } from "react";

export const certifications = [
  "G",
  "PG",
  "PG-13",
  "R",
  "NC-17",
  "TV-G",
  "TV-PG",
  "TV-14",
  "TV-MA",
];

export const genres = [
  "Acción",
  "Aventura",
  "Animación",
  "Documental",
  "Familia",
  "Fantasía",
  "Música",
  "Ciencia ficción",
  "Película de TV",
  "Crimen",
  "Drama",
  "Historia",
  "Terror",
  "Misterio",
  "Romance",
  "Suspense",
  "Bélica",
  "Western",
  "Comedia",
];

interface FiltersContextProps {
  filters: {
    genre: string[];
    certification: string | null;
  };
  setFilters: React.Dispatch<
    React.SetStateAction<{
      genre: string[];
      certification: string | null;
    }>
  >;
  resetFilters: () => void;
}

export const FiltersContext = createContext<FiltersContextProps | undefined>(
  undefined
);

export const useFilters = () => {
  const context = useContext(FiltersContext);

  if (!context) {
    throw new Error("useFilters must be used within a FiltersProvider");
  }

  return context;
};
