from scripts.data_cleaning import load_anime

df = load_anime("data/anime_filtered.csv")
df.to_csv("data/cleaned_anime.csv", index=False)

print("cleaned_anime.csv created successfully")