import { motion } from "motion/react";
import { useState } from "react";

export interface MovieOverviewProps {
  title: string;
  overview?: string;
  genres: string[];
}

export const MovieOverview = ({
  title,
  overview,
  genres,
}: MovieOverviewProps) => {
  const [isOverviewExpaned, setIsOverviewExpanded] = useState(false);
  return (
    <motion.div
      layout
      className="flex flex-col text-white p-2 sm:p-4 md:p-8 lg:p-12 w-full h-screen sm:w-[80%] max-h-screen overflow-hidden"
    >
      <motion.div layout className="flex-1"></motion.div>
      <motion.h1
        layout
        className="font-bold text-4xl sm:text-6xl md:text-6xl lg:text-7xl flex-3 flex items-center justify-start"
      >
        {title}
      </motion.h1>
      <motion.div
        layout
        className="flex gap-4 items-center flex-1 justify-start"
      >
        {genres.map((genre, index) => (
          <motion.span
            key={index}
            className="text-sm bg-gray-800 px-2 py-1 rounded"
          >
            {genre}
          </motion.span>
        ))}
      </motion.div>

      {overview ? (
        overview.length > 150 ? (
          <motion.div layout className="flex flex-col gap-4 items-start flex-4">
            <motion.p
              layout
              className={`text-lg sm:text-sm md:text-lg lg:text-xl ${
                isOverviewExpaned ? "line-clamp-6" : "line-clamp-3"
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
          <motion.div className="flex flex-col gap-4 items-start flex-4">
            <motion.p className="text-lg sm:text-xl md:text-2xl lg:text-3xl">
              {overview}
            </motion.p>
          </motion.div>
        )
      ) : (
        <motion.div className="flex flex-col gap-4 items-start flex-4">
          <p className="text-lg sm:text-xl md:text-2xl lg:text-3xl"></p>
        </motion.div>
      )}
    </motion.div>
  );
};
