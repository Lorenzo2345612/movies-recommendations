from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from controllers.movies import movies_router
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
origins = "*"

app = FastAPI()
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the movies router
app.include_router(movies_router, prefix="/api", tags=["movies"])