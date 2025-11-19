import streamlit as st
import pandas as pd
import os
import sys

from pathlib import Path

# ---------- PATHS & IMPORTS ----------
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
CSV_PATH = DATA_DIR / "anime.csv"

# Make scripts importable
sys.path.append(str(PROJECT_ROOT / "scripts"))

from data_cleaning import load_anime
from recommend import MOOD_GENRE_MAP, get_mood_recommendations, get_similar_by_genre
import components  # same folder


# ---------- STREAMLIT CONFIG ----------
st.set_page_config(
    page_title="🍥 MARS — Mood-Based Anime Recommender System 🪐",
    layout="wide",
)

components.inject_css()

st.markdown(
    """
    <h1>🍥 MARS — Mood-Based Anime Recommender System <span>🪐</span></h1>
    <p style="color:#9ca3af; font-size:0.95rem;">
      Choose your mood, explore anime, then dive deeper into similar shows – MARS-style.
    </p>
    """,
    unsafe_allow_html=True,
)

# ---------- LOAD DATA ----------
df = load_anime(str(CSV_PATH))

# ---------- SESSION STATE ----------
if "selected_title" not in st.session_state:
    st.session_state.selected_title = None

# ---------- MOOD SELECTION ----------
col_mood, col_info = st.columns([1.2, 2])

with col_mood:
    mood = st.selectbox("Your mood today:", list(MOOD_GENRE_MAP.keys()))
with col_info:
    st.write(
        f"🎭 **Mapped genres:** {', '.join(MOOD_GENRE_MAP[mood])}"
    )

# Get mood based recommendations (no exclusions)
recs = get_mood_recommendations(df, mood, n=9)

st.markdown("## ✨ Your Recommendations")

if recs.empty:
    st.info("No recommendations for this mood. Try another one.")
else:
    # Show cards in rows of 3
    rows = [recs.iloc[i : i + 3] for i in range(0, len(recs), 3)]

    for r_i, chunk in enumerate(rows):
        cols = st.columns(3)
        for c_i, (_, row) in enumerate(chunk.iterrows()):
            with cols[c_i]:
                clicked = components.anime_card(
                    row,
                    key_prefix=f"{mood}_{r_i}_{c_i}",
                    show_button=True,
                )
                if clicked:
                    st.session_state.selected_title = row["name"]

# ---------- SIMILAR ANIME SECTION ----------
st.markdown("---")
st.markdown("## 🛰 More Like This")

if st.session_state.selected_title is None:
    st.info("Click **🛰 More like this** on any anime card above to explore similar shows.")
else:
    base_title = st.session_state.selected_title
    st.markdown(
        f"### Because you liked: **{base_title}**"
    )

    similar = get_similar_by_genre(df, base_title, n=9)
    if similar.empty:
        st.info("Couldn't find similar anime – maybe this one has unique genres.")
    else:
        rows = [similar.iloc[i : i + 3] for i in range(0, len(similar), 3)]
        for r_i, chunk in enumerate(rows):
            cols = st.columns(3)
            for c_i, (_, row) in enumerate(chunk.iterrows()):
                with cols[c_i]:
                    components.anime_card(
                        row,
                        key_prefix=f"similar_{r_i}_{c_i}",
                        show_button=False,  # no infinite nesting
                    )

# ---------- VISUALS (CHARTS) ----------
st.markdown("---")
st.markdown("## 📊 Mood Snapshot")

vis_cols = st.columns(2)

with vis_cols[0]:
    st.markdown("#### 🎭 Genre Distribution")
    components.genre_donut(recs)

with vis_cols[1]:
    st.markdown("#### ⭐ Rating vs Popularity")
    components.rating_scatter(recs)
