# main.py — CLI for 🍥 MARS — Mood-Based Anime Recommender System 🪐

import pandas as pd
import matplotlib.pyplot as plt
import os

from scripts.data_cleaning import load_anime, merge_ratings_if_present
from scripts.utils import MOOD_MAP, genre_match_mask, score_anime
from scripts.storage import like, dislike, load_likes, load_dislikes


def plot_scores(df: pd.DataFrame, mood: str) -> None:
    """Plot a horizontal bar chart of score vs. anime name."""
    if df.empty:
        print("No data to plot.")
        return

    os.makedirs("data", exist_ok=True)
    plt.figure(figsize=(10, 4))
    plt.barh(df["name"], df["score"])
    plt.xlabel("MARS score")
    plt.ylabel("Anime title")
    plt.title(f"MARS top picks for mood: {mood}")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    out_path = f"data/{mood}_chart.png"
    plt.savefig(out_path, dpi=150)
    print(f"Chart saved to {out_path}")
    try:
        plt.show()
    except Exception:
        # On headless systems this will fail; that's fine.
        pass


def pick_batch(scored: pd.DataFrame,
               dislikes: set[str],
               shown: set[str],
               batch_size: int = 10,
               pool_size: int = 50) -> pd.DataFrame:
    """
    From a scored dataframe:
    - drop disliked
    - from top pool_size, drop already shown
    - sample up to batch_size items
    """
    df = scored.copy()
    if dislikes:
        df = df[~df["name"].isin(dislikes)]
    df = df.sort_values("score", ascending=False).head(pool_size)
    if shown:
        df = df[~df["name"].isin(shown)]
    if df.empty:
        return df
    return df.sample(min(batch_size, len(df)))


def run_cli() -> None:
    print("\n🍥 MARS — Mood-Based Anime Recommender System 🪐 (CLI)\n")

    anime_df = load_anime()
    anime_df = merge_ratings_if_present(anime_df)

    likes = load_likes()
    dislikes = load_dislikes()

    while True:
        print("\nAvailable moods:")
        print(", ".join(MOOD_MAP.keys()))
        mood = input("\nEnter your mood (or 'q' to quit): ").strip().lower()

        if mood == "q":
            print("\n👋 See you next time, space traveler.")
            return

        if mood not in MOOD_MAP:
            print("❌ Invalid mood. Try again.")
            continue

        target_genres = MOOD_MAP[mood]
        mask = genre_match_mask(anime_df, target_genres)
        filtered = anime_df[mask].copy()

        filtered["rating"] = pd.to_numeric(
            filtered.get("rating", 0), errors="coerce"
        ).fillna(0)
        filtered = filtered[filtered["rating"] >= 6.0]

        scored = score_anime(filtered, target_genres)
        shown_for_mood: set[str] = set()

        while True:
            batch = pick_batch(scored, dislikes, shown_for_mood,
                               batch_size=10, pool_size=50)
            if batch.empty:
                print("⚠️ No more unique anime for this mood. Resetting…")
                shown_for_mood.clear()
                batch = pick_batch(scored, dislikes, shown_for_mood,
                                   batch_size=10, pool_size=50)
                if batch.empty:
                    print("Still no anime. Try another mood.")
                    break

            shown_for_mood.update(batch["name"].tolist())

            print(f"\n✨ MARS picks for mood '{mood}':\n")
            print(batch[["name", "genre", "rating", "score"]]
                  .to_string(index=False))

            plot_scores(batch, mood)

            action = input(
                "\n[l]ike / [d]islike / [r]efresh / [b]ack to moods / [q]uit: "
            ).strip().lower()

            if action == "q":
                print("\n👋 See you next time, space traveler.")
                return
            if action == "b":
                break
            if action == "r":
                continue

            if action in ("l", "d"):
                title = input(
                    "Type the EXACT anime name from the list: "
                ).strip()
                if title not in batch["name"].values:
                    print("❌ That title is not in the current list.")
                    continue

                if action == "l":
                    like(title)
                    likes.add(title)
                    print(f"✅ Added to likes: {title}")
                else:
                    dislike(title)
                    dislikes.add(title)
                    print(f"🚫 Added to dislikes: {title}")
            else:
                print("❌ Invalid option. Try again.")


if __name__ == "__main__":
    run_cli()
