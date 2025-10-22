import pandas as pd
from math import log1p

MOOD_MAP = {
    'happy': ['Comedy', 'Slice of Life', 'Adventure'],
    'sad': ['Drama', 'Romance', 'Psychological'],
    'energetic': ['Action', 'Sports', 'Shounen'],
    'calm': ['Slice of Life', 'Music'],
    'excited': ['Action', 'Fantasy', 'Sci-Fi'],
    'nostalgic': ['Slice of Life', 'Drama'],
    'romantic': ['Romance', 'Drama']
}

def genre_match_mask(df, genres):
    """Return a boolean mask where df['genre'] contains any genre in genres."""
    if not genres:
        return pd.Series([False]*len(df), index=df.index)
    pattern = '|'.join([g.strip() for g in genres if g.strip()])
    return df['genre'].str.contains(pattern, case=False, na=False)

def score_anime(df):
    """Compute a simple ranking score mixing rating and popularity."""
    df = df.copy()
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
    pop = pd.to_numeric(df['members'], errors='coerce').fillna(0) if 'members' in df.columns else pd.Series([0]*len(df))
    df['score'] = df['rating'] * 0.75 + pop.apply(lambda x: log1p(x)) * 0.1
    if 'mean_user_rating' in df.columns:
        df['score'] = df['score'] * 0.85 + df['mean_user_rating'] * 0.15
    return df