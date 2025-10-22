import pandas as pd
import os

def load_anime(data_dir="data"):
    """Load and clean anime.csv file."""
    anime_path = os.path.join(data_dir, "anime.csv")

    if not os.path.exists(anime_path):
        raise FileNotFoundError(f"{anime_path} not found. Please add dataset.")

    anime = pd.read_csv(anime_path)
    anime.columns = [c.strip().lower() for c in anime.columns]

    rename_map = {}
    if 'title' in anime.columns:
        rename_map['title'] = 'name'
    if 'genres' in anime.columns:
        rename_map['genres'] = 'genre'
    if 'score' in anime.columns:
        rename_map['score'] = 'rating'
    if rename_map:
        anime = anime.rename(columns=rename_map)

    anime = anime.dropna(subset=['genre', 'rating'])
    anime['rating'] = pd.to_numeric(anime['rating'], errors='coerce')
    anime = anime.dropna(subset=['rating'])
    anime['genre'] = anime['genre'].astype(str)

    return anime


def merge_ratings_if_present(anime, data_dir="data"):
    """If rating.csv exists, attach mean_user_rating to anime DataFrame."""
    rating_path = os.path.join(data_dir, "rating.csv")
    if not os.path.exists(rating_path):
        return anime

    ratings = pd.read_csv(rating_path)
    if 'anime_id' in ratings.columns and 'anime_id' in anime.columns:
        agg = ratings.groupby('anime_id')['rating'].mean().reset_index()
        agg = agg.rename(columns={'rating': 'mean_user_rating'})
        anime = anime.merge(agg, on='anime_id', how='left')

    return anime
