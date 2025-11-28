import pandas as pd

df = pd.read_csv("data/anime.csv")

# FILTERS – You can change these if needed
df = df[(df["rating"] >= 7) & (df["members"] >= 20000)]

# KEEP TOP 300 MOST POPULAR
df = df.sort_values("members", ascending=False).head(300)

df.to_csv("data/anime_filtered.csv", index=False)

print("Filtered dataset created:", len(df), "rows saved as anime_filtered.csv")
