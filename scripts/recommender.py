import pandas as pd
from typing import Dict, List


# -------------------------------------------------------------------
# Mood → Genre weights (you can tweak these later if you want)
# -------------------------------------------------------------------
MOOD_GENRE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "happy": {
        "comedy": 1.0,
        "slice of life": 0.9,
        "music": 0.8,
        "romance": 0.7,
        "school": 0.6,
        "sports": 0.6,
        "adventure": 0.5,
        "fantasy": 0.4,
    },
    "sad": {
        "drama": 1.0,
        "psychological": 0.8,
        "romance": 0.7,
        "slice of life": 0.6,
        "supernatural": 0.5,
    },
    "chill": {
        "slice of life": 1.0,
        "comedy": 0.8,
        "romance": 0.6,
        "music": 0.6,
        "fantasy": 0.4,
    },
    "energetic": {
        "action": 1.0,
        "sports": 0.9,
        "adventure": 0.8,
        "mecha": 0.6,
        "shounen": 0.6,
        "sci-fi": 0.5,
    },
    "scared": {
        "horror": 1.0,
        "mystery": 0.9,
        "supernatural": 0.7,
        "psychological": 0.7,
        "thriller": 0.6,
    },
    "romantic": {
        "romance": 1.0,
        "drama": 0.8,
        "slice of life": 0.7,
        "school": 0.6,
        "shoujo": 0.6,
    },
    # fallback mood if something else is typed
    "default": {}  # handled in code
}


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def _normalize(s: pd.Series) -> pd.Series:
    """Min–max normalize a numeric Series to [0, 1]."""
    if s.empty:
        return s
    min_v = s.min()
    max_v = s.max()
    if min_v == max_v:
        return pd.Series(0.5, index=s.index)
    return (s - min_v) / (max_v - min_v)


def _jaccard(a: List[str], b: List[str]) -> float:
    """Jaccard similarity between two genre lists."""
    set_a = set(g.lower() for g in a or [])
    set_b = set(g.lower() for g in b or [])
    if not set_a and not set_b:
        return 0.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union else 0.0


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds normalized rating & members columns.
    Returns a copy.
    """
    out = df.copy()
    out["rating_norm"] = _normalize(out["rating"])
    out["members_norm"] = _normalize(out["members"])
    return out


# -------------------------------------------------------------------
# Mood scoring
# -------------------------------------------------------------------
def _compute_mood_scores(df: pd.DataFrame, mood: str) -> pd.Series:
    """
    Compute a mood match score [0,1] for each anime based on
    genre_list + primary_genre and MOOD_GENRE_WEIGHTS.
    """
    mood_key = mood.strip().lower()
    weights = MOOD_GENRE_WEIGHTS.get(mood_key)

    # If mood not defined, return mid scores so rating/popularity dominate
    if not weights:
        return pd.Series(0.5, index=df.index)

    scores = []

    for _, row in df.iterrows():
        genre_list = row.get("genre_list", []) or []
        primary = str(row.get("primary_genre", "")).lower()
        score = 0.0

        for g in genre_list:
            g_lower = g.lower()
            w = weights.get(g_lower)
            if not w:
                continue

            # boost if this is the primary genre
            if g_lower == primary:
                w *= 1.2

            score += w

        scores.append(score)

    scores_series = pd.Series(scores, index=df.index)
    return _normalize(scores_series)


# -------------------------------------------------------------------
# PUBLIC: recommend by mood
# -------------------------------------------------------------------
def recommend_by_mood(
    df: pd.DataFrame,
    mood: str,
    top_n: int = 20,
    min_rating: float = 0.0,
) -> pd.DataFrame:
    """
    Advanced recommender:
    final_score = 0.5 * mood_score + 0.3 * rating_norm + 0.2 * members_norm

    Returns top_n rows sorted by final_score.
    """
    df_feat = prepare_features(df)
    mood_scores = _compute_mood_scores(df_feat, mood)

    out = df_feat.copy()
    out["mood_score"] = mood_scores
    out["final_score"] = (
        0.5 * out["mood_score"]
        + 0.3 * out["rating_norm"]
        + 0.2 * out["members_norm"]
    )

    mask = (out["rating"] >= min_rating) & (out["mood_score"] > 0)
    ranked = out[mask].sort_values("final_score", ascending=False)

    return ranked.head(top_n)


# -------------------------------------------------------------------
# PUBLIC: more-like-this
# -------------------------------------------------------------------
def more_like_this(
    df: pd.DataFrame,
    anime_name: str,
    top_n: int = 12,
) -> pd.DataFrame:
    """
    Find similar anime based on:
    - same primary_genre (big weight)
    - genre list overlap (Jaccard)
    - rating similarity

    Returns a DataFrame with an extra 'similarity_score' column.
    """
    df_feat = prepare_features(df)

    target_rows = df_feat[df_feat["name"].str.lower() == anime_name.lower()]
    if target_rows.empty:
        raise ValueError(f"Anime not found: {anime_name}")

    target = target_rows.iloc[0]

    sims = []
    for idx, row in df_feat.iterrows():
        if row["name"] == target["name"]:
            continue

        same_primary = 1.0 if row["primary_genre"] == target["primary_genre"] else 0.0
        genre_overlap = _jaccard(row.get("genre_list", []), target.get("genre_list", []))

        rating_sim = 1.0 - min(abs(row["rating_norm"] - target["rating_norm"]), 1.0)

        # Composite similarity score
        sim_score = (
            0.5 * same_primary +
            0.3 * genre_overlap +
            0.2 * rating_sim
        )

        sims.append((idx, sim_score))

    sims_sorted = sorted(sims, key=lambda x: x[1], reverse=True)[:top_n]

    similar_df = df_feat.loc[[idx for idx, _ in sims_sorted]].copy()
    similar_df["similarity_score"] = [score for _, score in sims_sorted]

    return similar_df.sort_values("similarity_score", ascending=False)


# -------------------------------------------------------------------
# PUBLIC: explanation for UI
# -------------------------------------------------------------------
def build_explanations(recs: pd.DataFrame, mood: str) -> pd.DataFrame:
    """
    Add a human-readable 'explanation' column for each recommended anime.
    Useful to show in the UI under each card.
    """
    mood_lower = mood.strip().lower()

    def _explain(row: pd.Series) -> str:
        reasons = []

        reasons.append(f"Matches the '{row['primary_genre']}' genre")

        if row.get("mood_score", 0) >= 0.7:
            reasons.append(f"Strong match for your mood '{mood_lower}'")
        elif row.get("mood_score", 0) >= 0.4:
            reasons.append(f"Moderate match for your mood '{mood_lower}'")

        if row["rating"] >= 9:
            reasons.append("Critically acclaimed (rating ≥ 9)")
        elif row["rating"] >= 8.5:
            reasons.append("Highly rated by users")

        if row["members"] >= 300_000:
            reasons.append("Very popular among viewers")
        elif row["members"] >= 100_000:
            reasons.append("Popular choice")

        if not reasons:
            reasons.append("Good balance of mood, rating and popularity")

        return " • ".join(reasons)

    out = recs.copy()
    out["explanation"] = out.apply(_explain, axis=1)
    return out
