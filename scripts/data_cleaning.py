import pandas as pd
import requests
import time
import ast


def get_image_url(name: str) -> str:
    try:
        url = f"https://api.jikan.moe/v4/anime?q={name}&limit=1"
        r = requests.get(url, timeout=10)
        data = r.json()

        if "data" in data and len(data["data"]) > 0:
            return data["data"][0]["images"]["jpg"]["large_image_url"]

        return "https://via.placeholder.com/300x450?text=No+Image"

    except:
        return "https://via.placeholder.com/300x450?text=No+Image"


def crunchyroll(name: str) -> str:
    return f"https://www.crunchyroll.com/search?q={name.replace(' ', '+')}"


def split_genres(v):
    if isinstance(v, str):
        return [x.strip() for x in v.split(",")]
    return []


def load_anime(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0)
    df["members"] = df.get("members", 0).fillna(0).astype(int)

    df["genre_list"] = df["genre"].apply(split_genres)
    df["primary_genre"] = df["genre_list"].apply(lambda x: x[0] if x else "Unknown")

    df["crunchyroll"] = df["name"].apply(crunchyroll)

    urls = []
    for i, name in enumerate(df["name"]):
        urls.append(get_image_url(name))
        time.sleep(1)
    df["image_url"] = urls

    return df
