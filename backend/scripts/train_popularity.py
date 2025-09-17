import pandas as pd
from pathlib import Path
import os

"""
Train a simple popularity baseline using MovieLens data.
Downloads the small dataset if not present and outputs top_movies.csv used by the API.
"""

DATA_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"

def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data-cache"
    data_dir.mkdir(exist_ok=True)
    zip_path = data_dir / "ml-latest-small.zip"

    if not zip_path.exists():
        import requests
        r = requests.get(DATA_URL, timeout=30)
        r.raise_for_status()
        zip_path.write_bytes(r.content)

    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(data_dir)

    ratings = pd.read_csv(data_dir / "ml-latest-small" / "ratings.csv")
    movies = pd.read_csv(data_dir / "ml-latest-small" / "movies.csv")

    popularity = ratings.groupby('movieId').agg(avg_rating=('rating','mean'), num=('rating','count')).reset_index()
    # score: weighted by count
    popularity['score'] = popularity['avg_rating'] * (1 + popularity['num'] / popularity['num'].max())
    top = popularity.sort_values('score', ascending=False).head(200)

    df = top.merge(movies, on='movieId', how='left')
    # Extract year if present in title format "Title (1999)"
    def extract_year(title: str):
        if isinstance(title, str) and title.endswith(')') and '(' in title:
            try:
                return int(title.split('(')[-1].strip(')'))
            except Exception:
                return None
        return None

    df['release_year'] = df['title'].apply(extract_year)
    df.rename(columns={'avg_rating': 'rating'}, inplace=True)
    df_out = df[['movieId','title','release_year','rating']].copy()
    # Use env var POPULARITY_CSV_PATH if provided, else default to app/data
    env_path = os.getenv('POPULARITY_CSV_PATH')
    if env_path:
        out_dir = Path(env_path).parent
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = Path(env_path)
    else:
        out_dir = root / 'app' / 'data'
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / 'top_movies.csv'
    df_out.to_csv(out_path, index=False)
    print(f"Wrote {out_path}")

if __name__ == '__main__':
    main()

