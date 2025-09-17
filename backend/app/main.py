from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Movie Recs API", version="0.1.0")

# CORS for local dev frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendRequest(BaseModel):
    user_id: str | None = None
    liked_movie_ids: List[str] | None = None
    limit: int = 10

class Movie(BaseModel):
    id: str
    title: str
    overview: str | None = None
    poster_url: str | None = None
    release_year: int | None = None
    rating: float | None = None

class RecommendResponse(BaseModel):
    results: List[Movie]

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

@app.get("/movies/search")
async def search_movies(q: str, limit: int = 10) -> RecommendResponse:
    """Search movies by title"""
    # TODO: implement real search with TMDB API
    sample = [
        Movie(id="603", title="The Matrix", overview="A computer hacker learns about the true nature of reality", poster_url="https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg", release_year=1999, rating=8.7),
        Movie(id="27205", title="Inception", overview="A thief who steals corporate secrets through dream-sharing technology", poster_url="https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg", release_year=2010, rating=8.8),
        Movie(id="238", title="The Godfather", overview="The aging patriarch of an organized crime dynasty", poster_url="https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg", release_year=1972, rating=9.2),
    ]
    filtered = [m for m in sample if q.lower() in m.title.lower()]
    return RecommendResponse(results=filtered[:limit])

@app.post("/recommend", response_model=RecommendResponse)
async def recommend(body: RecommendRequest) -> RecommendResponse:
    """Get personalized movie recommendations"""
    # TODO: replace with hybrid recommender (collaborative + content-based)
    sample = [
        Movie(id="603", title="The Matrix", overview="A computer hacker learns about the true nature of reality", poster_url="https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg", release_year=1999, rating=8.7),
        Movie(id="27205", title="Inception", overview="A thief who steals corporate secrets through dream-sharing technology", poster_url="https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg", release_year=2010, rating=8.8),
        Movie(id="238", title="The Godfather", overview="The aging patriarch of an organized crime dynasty", poster_url="https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg", release_year=1972, rating=9.2),
        Movie(id="155", title="The Dark Knight", overview="When the menace known as the Joker wreaks havoc on Gotham", poster_url="https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg", release_year=2008, rating=9.0),
        Movie(id="13", title="Forrest Gump", overview="The presidencies of Kennedy and Johnson, the Vietnam War", poster_url="https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg", release_year=1994, rating=8.8),
    ]
    return RecommendResponse(results=sample[:body.limit])
