import pandas as pd
import os


def load_anime(csv_path: str) -> pd.DataFrame:
    """
    Load and lightly clean the anime dataset.
    Expects at least columns: 'name', 'genre', 'rating'.
    Others (like 'members', 'episode', 'Type') are ignored.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"anime.csv not found at: {csv_path}")

    df = pd.read_csv(csv_path)

    # Basic cleaning
    if "name" not in df.columns:
        raise ValueError("Dataset must have a 'name' column.")

    df["name"] = df["name"].astype(str)

    if "genre" not in df.columns:
        # create empty genre column if missing
        df["genre"] = ""

    df["genre"] = df["genre"].fillna("").astype(str)

    if "rating" not in df.columns:
        df["rating"] = 0.0

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0.0)

    # Optional columns
    if "members" in df.columns:
        df["members"] = pd.to_numeric(df["members"], errors="coerce").fillna(0)
    elif "popularity" in df.columns:
        df["members"] = -pd.to_numeric(df["popularity"], errors="coerce").fillna(0)
    else:
        df["members"] = 0

    # Make a parsed genre list
    df["genre_list"] = df["genre"].apply(
        lambda g: [x.strip() for x in str(g).split(",")] if g else []
    )

    return df
