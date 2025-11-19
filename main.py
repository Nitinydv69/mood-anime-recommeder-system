import os
import sys
from pathlib import Path
import pandas as pd

# ---------- PATH SETUP ----------
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
CSV_PATH = DATA_DIR / "anime.csv"

# Make scripts importable
sys.path.append(str(PROJECT_ROOT / "scripts"))

from data_cleaning import load_anime
from recommend import (
    MOOD_GENRE_MAP,
    get_mood_recommendations,
    get_similar_by_genre,
)


# ---------- CLI FUNCTIONS ----------
def print_header():
    print("\n")
    print("🍥 MARS — Mood-Based Anime Recommender System 🪐")
    print("------------------------------------------------")
    print("Welcome to MARS CLI! Explore anime by mood and similarity.\n")


def choose_mood():
    """
    Let the user type the mood name instead of numbers.
    Accepts things like 'happy', ' Happy  ', etc.
    """
    moods = list(MOOD_GENRE_MAP.keys())
    print("Available moods:")
    for m in moods:
        print(f"  - {m}")

    while True:
        choice = input("\nType your mood (e.g. happy, sad, calm): ").strip().lower()
        if choice in moods:
            return choice
        print("❌ Invalid mood. Please type one of:", ", ".join(moods))


def choose_anime(recommendations: pd.DataFrame):
    """
    Show recommendations numbered 1..N and let user pick one by number.
    """
    if recommendations.empty:
        return None

    print("\nChoose an anime to see similar ones:")

    # enumerate from 1 so numbers are clean: 1, 2, 3...
    for display_idx, (_, row) in enumerate(recommendations.iterrows(), start=1):
        print(f"{display_idx}. {row['name']} (Rating {row['rating']:.2f})")

    print("0. Skip")

    while True:
        raw = input("\nEnter number: ").strip()
        try:
            choice = int(raw)
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            continue

        if choice == 0:
            return None

        if 1 <= choice <= len(recommendations):
            # iloc uses 0-based index → choice-1
            return recommendations.iloc[choice - 1]["name"]

        print("❌ Invalid choice. Try again.")


# ---------- MAIN CLI ----------
def run_cli():
    print_header()

    # Load dataset
    df = load_anime(str(CSV_PATH))

    # 1. Choose mood (by typing name)
    mood = choose_mood()
    print(f"\n🎭 You chose mood: {mood}")
    print(f"Mapped genres: {', '.join(MOOD_GENRE_MAP[mood])}")

    # 2. Mood-based recommendations
    print("\n✨ Top Recommendations:")
    recs = get_mood_recommendations(df, mood, n=9)

    if recs.empty:
        print("No recommendations found for this mood.")
        return

    # print list with clean 1..N numbers
    for display_idx, (_, row) in enumerate(recs.iterrows(), start=1):
        print(f"{display_idx}. {row['name']}  | Rating: {row['rating']:.2f}")

    # 3. Choose anime → see similar ones
    chosen = choose_anime(recs)

    if chosen:
        print(f"\n🛰 Finding anime similar to: {chosen}")
        similar = get_similar_by_genre(df, chosen, n=9)

        if similar.empty:
            print("No similar anime found.")
        else:
            print("\n✨ More Like This:")
            for display_idx, (_, row) in enumerate(similar.iterrows(), start=1):
                print(f"{display_idx}. {row['name']}  | Rating: {row['rating']:.2f}")
    else:
        print("\n🚀 Skipped similarity search.")

    print("\n🌕 Thank you for using MARS CLI!")
    print("------------------------------------------------\n")


# ---------- RUN ----------
if __name__ == "__main__":
    run_cli()
