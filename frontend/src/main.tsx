import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createBrowserRouter, RouterProvider } from "react-router";
import { IndexPage } from "./pages";
import { MoviePage } from "./pages/movie";
import { FiltersProvider } from "./contexts/useFiltersContext";

const queryClient = new QueryClient();

const router = createBrowserRouter([
  {
    path: "/",
    element: <IndexPage />,
  },
  {
    path: "/movie/:id",
    element: <MoviePage />,
  },
]);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <FiltersProvider>
        <RouterProvider router={router} />
      </FiltersProvider>
    </QueryClientProvider>
  </StrictMode>
);
