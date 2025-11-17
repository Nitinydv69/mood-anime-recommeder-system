import os
import sys
import streamlit as st
import pandas as pd
import requests

# ============================================================
# 🔥 ABSOLUTE PROJECT PATH (WORKS REGARDLESS OF CWD)
# ============================================================
PROJECT_ROOT = "/Users/nitinyadav/Documents/mood-anime-recommeder-system"
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

LIKES_FILE = os.path.join(DATA_DIR, "likes.txt")
DISLIKES_FILE = os.path.join(DATA_DIR, "dislikes.txt")

os.makedirs(DATA_DIR, exist_ok=True)

sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# 🔥 LOAD INTERNAL MODULES
# ============================================================
from scripts.data_cleaning import load_anime, merge_ratings_if_present
from scripts.utils import MOOD_MAP, genre_match_mask, score_anime


# ============================================================
# 🔥 STORAGE HELPERS
# ============================================================
def load_list(path):
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}

def append_item(path, item):
    # Debug print to screen
    st.write("➡ Writing to:", os.path.abspath(path))
    with open(path, "a", encoding="utf-8") as f:
        f.write(item + "\n")


# ============================================================
# 🔥 POSTER FETCH (SAFE CACHE)
# ============================================================
@st.cache_data(ttl=3600)
def fetch_poster(title):
    try:
        r = requests.get(
            "https://api.jikan.moe/v4/anime",
            params={"q": title, "limit": 1},
            timeout=10,
        )
        if r.status_code != 200:
            return None
        d = r.json().get("data", [])
        if not d:
            return None
        return d[0]["images"]["jpg"]["large_image_url"]
    except:
        return None


# ============================================================
# 🔥 LOAD DATA
# ============================================================
def load_data():
    df = load_anime()
    df = merge_ratings_if_present(df)
    return df

df = load_data()


# ============================================================
# 🔥 STREAMLIT PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="🍥 MARS — Mood-Based Anime Recommender System 🪐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 🔥 TEST BUTTON (DO NOT DELETE UNTIL WE CONFIRM)
# ============================================================
st.markdown("### 🔬 Callback Test Button")

if st.button("CLICK ME TO TEST BUTTONS"):
    st.success("🔥 BUTTON CALLBACK IS WORKING!")
    st.write("If you see this, callbacks work. If Like/Dislike still fail → key issue.")


# ============================================================
# 🔥 SIDEBAR CONTROLS
# ============================================================
st.sidebar.title("🪐 MARS Controls")

mood = st.sidebar.selectbox("Choose your mood:", list(MOOD_MAP.keys()))
min_rating = st.sidebar.slider("Minimum rating", 0.0, 10.0, 6.0)
n_recs = st.sidebar.slider("How many?", 3, 12, 6)
refresh = st.sidebar.button("🔄 Refresh Recommendations")


# ============================================================
# 🔥 SESSION STATE INIT
# ============================================================
if "likes" not in st.session_state:
    st.session_state.likes = load_list(LIKES_FILE)

if "dislikes" not in st.session_state:
    st.session_state.dislikes = load_list(DISLIKES_FILE)

if f"seen_{mood}" not in st.session_state or refresh:
    st.session_state[f"seen_{mood}"] = set()

likes = st.session_state.likes
dislikes = st.session_state.dislikes
seen = st.session_state[f"seen_{mood}"]


# ============================================================
# 🔥 FILTER AND SCORE
# ============================================================
genres = MOOD_MAP[mood]
mask = genre_match_mask(df, genres)
filtered = df[mask].copy()

filtered["rating"] = pd.to_numeric(filtered["rating"], errors="coerce").fillna(0)
filtered = filtered[filtered["rating"] >= min_rating]

scored = score_anime(filtered, genres)
scored = scored[~scored["name"].isin(dislikes)]
scored = scored[~scored["name"].isin(seen)]

if scored.empty:
    st.warning("No anime found for this mood.")
    top = pd.DataFrame()
else:
    top = scored.sample(min(n_recs, len(scored)))
    seen.update(top["name"].tolist())


# ============================================================
# 🔥 HEADER
# ============================================================
st.markdown("""
# 🍥 MARS — Mood-Based Anime Recommender System 🪐
### _Find anime that matches how you feel._
---
""")


# ============================================================
# 🔥 CLEAN BUTTON KEYS (IMPORTANT)
# ============================================================
def clean_key(title):
    return "".join(c for c in title if c.isalnum())


# ============================================================
# 🔥 RENDER RECOMMENDATIONS
# ============================================================
cols = st.columns(3)

for i, row in top.reset_index(drop=True).iterrows():
    col = cols[i % 3]
    with col:
        with st.container(border=True):
            title = row["name"]
            poster = fetch_poster(title)
            safe_key = clean_key(title)

            if poster:
                st.image(poster, width=230)

            st.markdown(f"### 🎴 {title}")
            st.caption(f"Genres: {row.get('genre', '')}")
            st.write(f"⭐ Rating: {row.get('rating', 'N/A')}")
            st.write(f"📊 Score: {row.get('score', 0):.2f}")

            b1, b2 = st.columns(2)

            with b1:
                if st.button("👍 Like", key=f"like_{safe_key}"):
                    append_item(LIKES_FILE, title)
                    st.session_state.likes.add(title)
                    st.success(f"Added to Likes: {title}")

            with b2:
                if st.button("👎 Dislike", key=f"dislike_{safe_key}"):
                    append_item(DISLIKES_FILE, title)
                    st.session_state.dislikes.add(title)
                    st.warning(f"Added to Dislikes: {title}")


# ============================================================
# 🔧 DEBUG PANEL
# ============================================================
with st.expander("🔧 Debug info"):
    st.write("PROJECT_ROOT:", PROJECT_ROOT)
    st.write("Likes file:", LIKES_FILE)
    st.write("Dislikes file:", DISLIKES_FILE)
    st.write("Likes (session):", likes)
    st.write("Dislikes (session):", dislikes)
    st.write("Seen:", seen)
