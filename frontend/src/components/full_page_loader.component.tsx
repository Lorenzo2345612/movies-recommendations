import { LoaderComponent } from "./loader.component";

export const FullPageLoader = () => {
  return (
    <div className="flex items-center justify-center h-screen">
      <LoaderComponent />
    </div>
  );
};
