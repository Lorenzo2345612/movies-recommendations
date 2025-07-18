import React, { useState } from "react";
import { FiltersContext } from "../hooks/useFilters";

export const FiltersProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [filters, setFilters] = useState<{
    genre: string[];
    certification: string | null;
  }>({
    genre: [],
    certification: null,
  });

  const resetFilters = () => {
    setFilters({
      genre: [],
      certification: null,
    });
  };

  return (
    <FiltersContext.Provider value={{ filters, setFilters, resetFilters }}>
      {children}
    </FiltersContext.Provider>
  );
};
