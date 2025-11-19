import streamlit as st
import plotly.express as px
import requests


# ---------- CSS FOR NETFLIX-STYLE CARDS ----------
def inject_css():
    st.markdown(
        """
        <style>
        /* Global */
        body {
            background-color: #05070b;
        }
        .main {
            background-color: #05070b;
        }
        /* Center the main container a bit */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }

        /* Section titles */
        h1, h2, h3, h4 {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        /* Anime card */
        .anime-card {
            background: #111827;
            border-radius: 18px;
            padding: 0.9rem;
            box-shadow: 0 14px 30px rgba(0,0,0,0.4);
            transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
            border: 1px solid rgba(148,163,184,0.3);
        }
        .anime-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.75);
            background: #020617;
        }

        .anime-title {
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.1rem;
        }

        .anime-meta {
            font-size: 0.85rem;
            color: #9ca3af;
        }

        .tag-pill {
            display: inline-block;
            padding: 0.15rem 0.5rem;
            margin-right: 0.25rem;
            margin-bottom: 0.25rem;
            border-radius: 999px;
            background: rgba(56,189,248,0.15);
            color: #e5f3ff;
            font-size: 0.75rem;
        }

        .score-badge {
            display: inline-block;
            padding: 0.2rem 0.45rem;
            border-radius: 999px;
            background: rgba(251,191,36,0.15);
            color: #fde68a;
            font-size: 0.8rem;
            margin-right: 0.4rem;
        }

        .rating-badge {
            display: inline-block;
            padding: 0.2rem 0.45rem;
            border-radius: 999px;
            background: rgba(52,211,153,0.17);
            color: #bbf7d0;
            font-size: 0.8rem;
        }

        .stButton > button {
            border-radius: 999px;
            border: 1px solid rgba(148,163,184,0.4);
            background: linear-gradient(135deg, #f97316, #ea580c);
            color: white;
            font-weight: 600;
            padding: 0.4rem 0.9rem;
        }
        .stButton > button:hover {
            border-color: #fed7aa;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------- POSTER FETCHING (Jikan API) ----------
@st.cache_data(show_spinner=False)
def fetch_poster(title: str):
    """
    Use Jikan API to get an anime poster URL for a given title.
    """
    try:
        resp = requests.get(
            "https://api.jikan.moe/v4/anime",
            params={"q": title, "limit": 1},
            timeout=10,
        )
        if resp.status_code != 200:
            return None
        data = resp.json().get("data", [])
        if not data:
            return None
        return data[0]["images"]["jpg"]["large_image_url"]
    except Exception:
        return None


# ---------- CARD COMPONENT ----------
def anime_card(row, key_prefix: str = "", show_button: bool = True):
    """
    Render a single anime card. Returns True if 'More like this' was clicked.
    """
    title = row["name"]
    genres = row.get("genre_list", [])
    rating = row.get("rating", 0.0)
    score = row.get("score", 0.0)

    col_img, col_info = st.columns([1, 1.6])

    with col_img:
        poster = fetch_poster(title)
        if poster:
            st.image(poster, use_container_width=True)
        else:
            st.image(
                "https://via.placeholder.com/400x600?text=No+Image",
                use_container_width=True,
            )

    with col_info:
        st.markdown(f"<div class='anime-title'>🎬 {title}</div>", unsafe_allow_html=True)

        if genres:
            st.markdown(
                " ".join(
                    f"<span class='tag-pill'>{g}</span>" for g in genres[:5]
                ),
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
            <div class="anime-meta">
                <span class="rating-badge">⭐ Rating: {rating:.2f}</span>
                <span class="score-badge">🧮 MARS Score: {score:.2f}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        clicked = False
        if show_button:
            if st.button("🛰 More like this", key=f"{key_prefix}_{title}"):
                clicked = True

        return clicked


# ---------- CHARTS ----------
def genre_donut(df):
    explode_df = df.explode("genre_list")
    explode_df = explode_df[explode_df["genre_list"] != ""]
    if explode_df.empty:
        st.info("No genre data available for chart.")
        return

    top = explode_df["genre_list"].value_counts().head(10).reset_index()
    top.columns = ["Genre", "Count"]

    fig = px.pie(
        top,
        names="Genre",
        values="Count",
        hole=0.55,
        title="Top Genres in Recommendations",
    )
    fig.update_layout(
        showlegend=True,
        paper_bgcolor="#020617",
        plot_bgcolor="#020617",
        font_color="#e5e7eb",
    )
    st.plotly_chart(fig, use_container_width=True)


def rating_scatter(df):
    if df.empty:
        st.info("No data for rating vs popularity chart.")
        return

    fig = px.scatter(
        df,
        x="members",
        y="rating",
        hover_name="name",
        title="Rating vs Popularity (members)",
    )
    fig.update_layout(
        paper_bgcolor="#020617",
        plot_bgcolor="#020617",
        font_color="#e5e7eb",
    )
    st.plotly_chart(fig, use_container_width=True)
