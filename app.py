import streamlit as st
import pandas as pd
import plotly.express as px
import ast
import random
import json
import os
import sys


# Import the logic for the recommender system
sys.path.append(os.path.abspath("scripts"))
from recommender import recommend_by_mood, more_like_this, build_explanations


# Utilities
def upscale_mal_image(url):
    """Return a nicer MAL image (strip 't' thumbnail if present)."""
    try:
        if isinstance(url, str) and url.endswith("t.jpg"):
            return url.replace("t.jpg", ".jpg")
    except Exception:
        pass
    if not isinstance(url, str) or not url.startswith("http"):
        return "https://i.imgur.com/ZKMnXce.png"
    return url


def fix_genre_list(x):
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        try:
            val = ast.literal_eval(x)
            return val if isinstance(val, list) else []
        except Exception:
            return []
    return []


def rating_to_stars(r):
    """Convert 0–10 score into 0–5 stars."""
    if pd.isna(r):
        return "☆☆☆☆☆"
    stars = int(round(r / 2))
    stars = max(0, min(5, stars))
    return "⭐" * stars + "☆" * (5 - stars)


def compute_match_score(row, mood, max_members):
    """Simple heuristic: rating + popularity + mood/genre alignment."""
    score = (row["rating"] / 10) * 60

    pop_factor = min(row["members"] / max_members, 1.0) if max_members else 0
    score += pop_factor * 20

    mood_map = {
        "happy": ["Comedy", "Slice of Life", "Music"],
        "sad": ["Drama", "Romance"],
        "chill": ["Slice of Life", "Iyashikei", "Music"],
        "energetic": ["Action", "Sports", "Shounen"],
        "scared": ["Horror", "Thriller", "Mystery", "Supernatural"],
        "romantic": ["Romance", "Shoujo"],
    }

    primary = row.get("primary_genre", "")
    if primary in mood_map.get(mood, []):
        score += 20
    else:
        score += 8  # small base

    return int(max(0, min(100, score)))


# Load the Data

@st.cache_data
def load_data():
    df = pd.read_csv("data/cleaned_anime.csv")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0.0)
    df["members"] = pd.to_numeric(df.get("members", 0), errors="coerce").fillna(0).astype(int)
    df["genre_list"] = df["genre_list"].apply(fix_genre_list)
    return df


df = load_data()
MAX_MEMBERS = df["members"].max()


# Favorites system save file
FAV_FILE = "favorites.json"


def load_favorites():
    if os.path.exists(FAV_FILE):
        try:
            with open(FAV_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_favorites(favs):
    with open(FAV_FILE, "w") as f:
        json.dump(favs, f)


favorites = load_favorites()


# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="MARS – Anime Recommender",
    page_icon="🍥",
    layout="wide",
)

# HEADER
st.markdown("## 🪐 MARS – Mood-Based Anime Recommender System")
st.write(
    "Let your **mood**, **vibes**, and **energy** pick the next anime. "
    "Tell **MARS** how you wanna feel,  "
    "MARS will handle the rest."
)
st.markdown("---")


# Siderbar with emojis
st.sidebar.header("⚙️ Controls")

mood_emojis = {
    "happy": "😊",
    "sad": "😢",
    "chill": "🍃",
    "energetic": "🔥",
    "scared": "👻",
    "romantic": "💘",
}

mood = st.sidebar.selectbox(
    "Choose mood",
    list(mood_emojis.keys()),
    format_func=lambda m: f"{mood_emojis[m]} {m}",
)

top_n = st.sidebar.slider("Number of anime to show", 3, 12, 6)
min_rating = st.sidebar.slider("Minimum rating", 0.0, 10.0, 7.5)

genre_filter = st.sidebar.multiselect(
    "Filter by genres",
    sorted({g for gl in df["genre_list"] for g in gl}),
)

search_query = st.sidebar.text_input("🔍 Search anime")

if st.sidebar.button("🎲 Surprise Me"):
    st.session_state["surprise"] = True
else:
    # don't reset automatically if not clicked, please 
    st.session_state.setdefault("surprise", False)

st.sidebar.markdown("---")
st.sidebar.caption("Made with ❤️ by Nitin")


# RESULTS PRIORITY: Surprise > Search > Genre > Mood
st.subheader("✨ Results")

results = None
mode_label = ""

# 1) Surprise mode
if st.session_state.get("surprise"):
    results = df.sample(1)
    mode_label = "🎲 Surprise Pick"
    # reset after showing once
    st.session_state["surprise"] = False

# 2) Search mode
elif search_query.strip():
    results = df[df["name"].str.contains(search_query, case=False, na=False)].head(20)
    mode_label = f"🔍 Search: {search_query}"

# 3) Genre mode
elif genre_filter:
    mask = df["genre_list"].apply(lambda gl: any(g in gl for g in genre_filter))
    results = df[mask].sort_values("rating", ascending=False).head(top_n)
    mode_label = f"🎭 Genres: {', '.join(genre_filter)}"

# 4) Mood mode
else:
    recs = recommend_by_mood(df, mood, top_n=top_n * 4, min_rating=min_rating)
    results = build_explanations(recs, mood).head(top_n)
    mode_label = f"✨ Recommended for {mood_emojis[mood]} {mood.capitalize()}"

st.markdown(f"### {mode_label}")


#Result Cards
if results is None or results.empty:
    st.write("No anime found.")
else:
    cols = st.columns(3)

    for i, (_, row) in enumerate(results.iterrows()):
        with cols[i % 3]:
            img = upscale_mal_image(row.get("image_url", ""))
            st.image(img, width=260)

            st.markdown(f"### {row['name']}")

            # Type + episodes
            typ = row.get("type", "N/A")
            eps = row.get("episodes", "?")
            st.caption(f"`{typ}` · `{eps} eps`")

            # Genre badges
            if row["genre_list"]:
                st.caption("  ".join(f"`{g}`" for g in row["genre_list"][:6]))

            # Rating + stars
            stars = rating_to_stars(row["rating"])
            st.write(f"{stars} **{row['rating']:.2f}/10**")

            # Mood match score & explanation only in mood mode
            if not search_query and not genre_filter and mode_label.startswith("✨ Recommended"):
                score = compute_match_score(row, mood, MAX_MEMBERS)
                st.write(f"**Match Score: {score}%**")
                st.caption(row.get("explanation", ""))

            # Extra details (hover via expander)
            with st.expander("More info"):
                st.write(f"**Members:** {row['members']:,}")
                st.write(f"**Type:** {typ}")
                st.write(f"**Episodes:** {eps}")
                st.write(f"**Genres:** {', '.join(row['genre_list'])}")

            # Watch link
            st.markdown(f"[Watch on Crunchyroll]({row['crunchyroll']})")

            # Favorites button
            fav_label = "❤️ Add to Favorites" if row["name"] not in favorites else "✅ In Favorites"
            if st.button(fav_label, key=f"fav_{row['name']}"):
                favorites = load_favorites()
                if row["name"] not in favorites:
                    favorites.append(row["name"])
                    save_favorites(favorites)
                st.success("Added to favorites!")
            st.write("---")



# Favorites
st.markdown("---")
st.subheader("❤️ Favorites")

favorites = load_favorites()
if not favorites:
    st.write("You haven't added any favorites yet. Click **'Add to Favorites'** under an anime card.")
else:
    fav_df = df[df["name"].isin(favorites)]
    cols_f = st.columns(3)
    for i, (_, row) in enumerate(fav_df.iterrows()):
        with cols_f[i % 3]:
            img = upscale_mal_image(row.get("image_url", ""))
            st.image(img, width=220)
            st.markdown(f"**{row['name']}**")
            st.caption(", ".join(row["genre_list"]))
            st.markdown(f"[Watch on Crunchyroll]({row['crunchyroll']})")
            # remove button
            if st.button("Remove", key=f"rem_{row['name']}"):
                favs = load_favorites()
                if row["name"] in favs:
                    favs.remove(row["name"])
                    save_favorites(favs)
                st.experimental_rerun()

# INSIGHTS
st.markdown("---")
st.subheader("📊 Insights")

col1, col2 = st.columns(2)

# LEFT: DONUT CHART
with col1:
    st.caption("Primary genre distribution")

    genre_counts = df["primary_genre"].value_counts()

    fig1 = px.pie(
        names=genre_counts.index,
        values=genre_counts.values,
        title="Primary Genre Distribution",
        hole=0.45
    )

    st.plotly_chart(fig1, use_container_width=True)

# RIGHT: TOP 25 BAR CHART 
with col2:
    st.caption("Top rated anime")

    top25 = df.sort_values("rating", ascending=False).head(25)

    fig2 = px.bar(
        top25,
        x="name",
        y="rating",
        title="Top 25 Highest Rated Anime",
    )

    fig2.update_layout(
        xaxis_tickangle=-45,
        showlegend=False
    )

    st.plotly_chart(fig2, use_container_width=True)


## More like this
st.markdown("---")
st.subheader("🔍 More Like This")

selected = st.selectbox("Pick an anime you like:", df["name"].unique())
similar = more_like_this(df, selected, top_n=6)

cols2 = st.columns(3)
for i, (_, row) in enumerate(similar.iterrows()):
    with cols2[i % 3]:
        img = upscale_mal_image(row.get("image_url", ""))
        st.image(img, width=220)
        st.markdown(f"**{row['name']}**")
        st.caption(", ".join(row["genre_list"]))
        st.markdown(f"[Watch on Crunchyroll]({row['crunchyroll']})")
        st.write("---")


## Footer 
st.markdown("---")
st.caption("🪐 MARS – Mood-Based Anime Recommender · Built with Streamlit, pandas, and a lot of coffee by Nitin.")
