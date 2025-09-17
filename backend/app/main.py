from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import asyncio
import httpx
import csv

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

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

async def _tmdb_search(query: str, limit: int) -> List[Movie]:
    if not TMDB_API_KEY:
        return []
    params = {"query": query, "include_adult": "false", "language": "en-US", "page": 1}
    headers = {"Authorization": f"Bearer {TMDB_API_KEY}", "accept": "application/json"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{TMDB_BASE}/search/movie", params=params, headers=headers)
        if resp.status_code != 200:
            return []
        data = resp.json()
        results = []
        for item in data.get("results", [])[:limit]:
            poster_path = item.get("poster_path")
            year = None
            if item.get("release_date"):
                try:
                    year = int(item["release_date"].split("-")[0])
                except Exception:
                    year = None
            results.append(
                Movie(
                    id=str(item.get("id")),
                    title=item.get("title") or item.get("name") or "Untitled",
                    overview=item.get("overview"),
                    poster_url=f"{TMDB_IMG}{poster_path}" if poster_path else None,
                    release_year=year,
                    rating=float(item.get("vote_average")) if item.get("vote_average") is not None else None,
                )
            )
        return results

@app.get("/movies/search")
async def search_movies(q: str, limit: int = 10) -> RecommendResponse:
    """Search movies by title via TMDB if configured, else fallback sample."""
    results = await _tmdb_search(q, limit)
    if not results:
        sample = [
            Movie(id="603", title="The Matrix", overview="A computer hacker learns about the true nature of reality", poster_url=f"{TMDB_IMG}/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg", release_year=1999, rating=8.7),
            Movie(id="27205", title="Inception", overview="A thief who steals corporate secrets through dream-sharing technology", poster_url=f"{TMDB_IMG}/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg", release_year=2010, rating=8.8),
            Movie(id="238", title="The Godfather", overview="The aging patriarch of an organized crime dynasty", poster_url=f"{TMDB_IMG}/3bhkrj58Vtu7enYsRolD1fZdja1.jpg", release_year=1972, rating=9.2),
        ]
        filtered = [m for m in sample if q.lower() in m.title.lower()]
        return RecommendResponse(results=filtered[:limit])
    return RecommendResponse(results=results)

def _load_popular_from_csv(path: str, limit: int) -> List[Movie]:
    if not os.path.exists(path):
        return []
    items: List[Movie] = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append(
                Movie(
                    id=str(row.get('movieId') or row.get('id') or ''),
                    title=row.get('title') or 'Untitled',
                    overview=None,
                    poster_url=row.get('poster_url') or None,
                    release_year=int(row['release_year']) if row.get('release_year') else None,
                    rating=float(row['rating']) if row.get('rating') else None,
                )
            )
            if len(items) >= limit:
                break
    return items

@app.post("/recommend", response_model=RecommendResponse)
async def recommend(body: RecommendRequest) -> RecommendResponse:
    """Get personalized movie recommendations (popularity fallback)."""
    # TODO: replace with hybrid recommender (collaborative + content-based)
    popular_path = os.path.join(os.path.dirname(__file__), 'data', 'top_movies.csv')
    items = _load_popular_from_csv(popular_path, body.limit)
    if items:
        return RecommendResponse(results=items)
    # fallback curated if no data file
    sample = [
        Movie(id="603", title="The Matrix", overview="A computer hacker learns about the true nature of reality", poster_url=f"{TMDB_IMG}/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg", release_year=1999, rating=8.7),
        Movie(id="27205", title="Inception", overview="A thief who steals corporate secrets through dream-sharing technology", poster_url=f"{TMDB_IMG}/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg", release_year=2010, rating=8.8),
        Movie(id="238", title="The Godfather", overview="The aging patriarch of an organized crime dynasty", poster_url=f"{TMDB_IMG}/3bhkrj58Vtu7enYsRolD1fZdja1.jpg", release_year=1972, rating=9.2),
        Movie(id="155", title="The Dark Knight", overview="When the menace known as the Joker wreaks havoc on Gotham", poster_url=f"{TMDB_IMG}/qJ2tW6WMUDux911r6m7haRef0WH.jpg", release_year=2008, rating=9.0),
        Movie(id="13", title="Forrest Gump", overview="The presidencies of Kennedy and Johnson, the Vietnam War", poster_url=f"{TMDB_IMG}/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg", release_year=1994, rating=8.8),
    ]
    return RecommendResponse(results=sample[: body.limit])
