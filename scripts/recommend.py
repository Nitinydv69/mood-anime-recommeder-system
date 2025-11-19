import pandas as pd
from typing import List, Dict


# Mood → genres mapping
MOOD_GENRE_MAP: Dict[str, List[str]] = {
    "happy": ["Comedy", "Slice of Life", "Kids"],
    "sad": ["Drama", "Romance"],
    "energetic": ["Action", "Adventure", "Sports", "Shounen"],
    "calm": ["Slice of Life", "Iyashikei"],
    "dark": ["Horror", "Thriller", "Psychological"],
    "nostalgic": ["School", "Drama", "Shoujo"],
}


def score_for_mood(df: pd.DataFrame, mood: str) -> pd.DataFrame:
    """
    Create a score column for how well each anime matches the given mood.
    Uses rating + genre overlap + members (popularity) as tie-breaker.
    """
    df = df.copy()
    mood_genres = MOOD_GENRE_MAP.get(mood, [])

    df["score"] = df["rating"] / 2.0  # base on rating (0–5 ish)

    def genre_boost(row):
        g_list = row.get("genre_list", [])
        hits = sum(1 for mg in mood_genres if mg in g_list)
        return hits * 0.7  # each matching genre adds 0.7

    df["score"] += df.apply(genre_boost, axis=1)

    # Popularity factor (scaled)
    if "members" in df.columns:
        members_max = df["members"].max() or 1
        df["score"] += (df["members"] / members_max) * 0.8

    return df.sort_values("score", ascending=False)


def get_mood_recommendations(
    df: pd.DataFrame, mood: str, n: int = 9, exclude_names=None
) -> pd.DataFrame:
    """
    Top-N recommendations for a mood, optionally excluding some titles.
    """
    scored = score_for_mood(df, mood)
    if exclude_names:
        scored = scored[~scored["name"].isin(exclude_names)]
    return scored.head(n)


def get_similar_by_genre(
    df: pd.DataFrame, base_title: str, n: int = 9
) -> pd.DataFrame:
    """
    Find anime similar to base_title based on genre overlap + rating.
    """
    df = df.copy()
    base_row = df[df["name"] == base_title]

    if base_row.empty:
        return df.head(0)  # empty

    base_row = base_row.iloc[0]
    base_genres = set(base_row.get("genre_list", []))

    if not base_genres:
        return df.head(0)

    def similarity(row):
        g = set(row.get("genre_list", []))
        overlap = len(base_genres & g)
        # Combine overlap and rating
        return overlap * 1.0 + (row["rating"] / 4.0)

    df["sim_score"] = df.apply(similarity, axis=1)

    # Exclude itself
    df = df[df["name"] != base_title]
    df = df.sort_values("sim_score", ascending=False)
    return df.head(n)
