# main.py
from scripts.data_cleaning import load_anime, merge_ratings_if_present
from scripts.utils import MOOD_MAP, genre_match_mask, score_anime
import os

def run_cli():
    print("Mood-Based Anime Recommender — CLI demo")
    anime = load_anime()
    anime = merge_ratings_if_present(anime)

    print("\nAvailable moods:", ', '.join(MOOD_MAP.keys()))
    mood = input("Enter your mood: ").strip().lower()
    if mood not in MOOD_MAP:
        print("Mood not recognized — defaulting to 'happy'")
        mood = 'happy'
    genres = MOOD_MAP[mood]

    mask = genre_match_mask(anime, genres)
    filtered = anime[mask].copy()
    if filtered.empty:
        print("No anime found for this mood. Try a different mood.")
        return

    scored = score_anime(filtered)
    top = scored.sort_values('score', ascending=False).head(15)
    output_path = os.path.join('data', 'results.csv')
    top.to_csv(output_path, index=False)
    print(f"\nTop recommendations for mood '{mood}':\n")
    print(top[['name','genre','rating']].head(10).to_string(index=False))
    print(f"\nSaved top results to {output_path}")

if __name__ == "__main__":
    run_cli()
