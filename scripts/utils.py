# scripts/utils.py
import pandas as pd
from math import log1p

# 🎭 Mood → Genre dictionary (refined for less overlap)
MOOD_MAP = {
    'happy': ['Comedy', 'Slice of Life', 'Music'],
    'sad': ['Drama', 'Romance', 'Psychological'],
    'energetic': ['Action', 'Sports', 'Martial Arts'],
    'calm': ['Iyashikei', 'Slice of Life', 'Healing'],
    'excited': ['Action', 'Fantasy', 'Sci-Fi'],
    'nostalgic': ['Historical', 'Drama', 'School'],
    'romantic': ['Romance', 'Shoujo', 'Josei']
}

def genre_match_mask(df, genres):
    """
    Return mask (True/False) for rows where the genre column contains any given genres.
    Works with either 'genre' or 'genres' column.
    """
    col = 'genre'
    if 'genres' in df.columns:
        col = 'genres'

    if not genres or col not in df.columns:
        return pd.Series([False] * len(df), index=df.index)

    mask = pd.Series(False, index=df.index)
    for g in genres:
        mask = mask | df[col].str.contains(g, case=False, na=False)
    return mask

def score_anime(df, mood_genres=None):
    """
    Add a 'score' column for ranking anime with:
    - rating
    - popularity (members) if available
    - mean_user_rating if available
    - mood overlap ratio (extra boost)
    """
    df = df.copy()
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)

    # Base score from rating and popularity
    if 'members' in df.columns:
        pop = pd.to_numeric(df['members'], errors='coerce').fillna(0)
        df['score'] = df['rating'] * 0.75 + pop.apply(lambda x: log1p(x)) * 0.1
    else:
        df['score'] = df['rating']

    # Include mean_user_rating if dataset has it
    if 'mean_user_rating' in df.columns:
        df['score'] = df['score'] * 0.85 + df['mean_user_rating'] * 0.15

    # Mood overlap ratio boost
    if mood_genres:
        def overlap_ratio(genre_str):
            genre_list = [g.strip().lower() for g in str(genre_str).split(',')]
            mood_list = [m.lower() for m in mood_genres]
            matches = sum(g in mood_list for g in genre_list)
            return matches / max(1, len(genre_list))

        df['score'] += df['genre'].apply(overlap_ratio) * 2.0  # weight=2.0 boost

    return df
