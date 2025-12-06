# 🪐 MARS - Mood-Based Anime Recommender System

MARS (Mood-Based Anime Recommender System) is a **Streamlit web application** that recommends anime based on your **mood**, **favorite genres**, **search queries**, or a **random surprise pick**.

Stop scrolling endlessly — MARS generates instant, clean, and high-quality recommendations using a curated anime dataset, mood-matching logic, and a premium UI with genre badges, match scores, and insights.

---

## ✨ Features

### 🎭 Mood-Based Recommendations  
Choose between:
- 😊 Happy  
- 😢 Sad  
- 🍃 Chill  
- 🔥 Energetic  
- 👻 Scared  
- 💘 Romantic  

Recommendations are based on mood-genre alignment, rating, popularity, and a weighted scoring system.

---

### 🎚️ Smart Priority System  
Only one mode is active at a time:

1. 🎲 **Surprise Me**  
2. 🔍 **Search**  
3. 🎭 **Genre Filter**  
4. ✨ **Mood Recommendations**

This ensures clean, predictable results with no overlap.

---

### 🔍 Search Bar  
Instant fuzzy search for anime titles.

---

### 🧩 Genre Filters  
Multi-select genres to filter anime by tags such as `Comedy`, `Drama`, `Action`, etc.

---

### ⭐ Premium Anime Cards  
Each card includes:

- High-resolution poster  
- Title  
- Type & Episode Count  
- Genre Badges  
- Star Rating (⭐ based on score /10)  
- Numeric Score  
- Match Score (%)  
- Mood Explanation  
- Crunchyroll Link  
- ❤️ Add to Favorites  
- “More Info” hover expander  

---

### ❤️ Favorites System  
- Saves anime into `data/favorites.json`  
- Persistent locally  
- Remove anytime from Favorites section  

---

### 📊 Insights Dashboard  
- 🍩 **Primary Genre Distribution (Donut Chart)**  
- 📈 **Top 25 Highest Rated Anime (Bar Chart)**  

---

### 🔍 More Like This  
Select an anime and get similar titles using genre similarity and rating.

---

## 🧱 Tech Stack

- Python 3.10+  
- Streamlit  
- pandas  
- plotly.express  
- Jikan/MAL-style image URLs  

---

## 📁 Folder Structure

```
mood-anime-recommeder-system/
│
├─ app.py
├─ prepare_data.py
├─ requirements.txt
├─ README.md
│
├─ data/
│   ├─ anime.csv
│   ├─ cleaned_anime.csv
│   └─ favorites.json
│
├─ scripts/
│   ├─ data_cleaning.py
├─  └─ recommender.py
```

---

## 🔧 Installation

### 1. Clone Repository  
```bash
git clone <your-repo-url>
cd mood-anime-recommender-system
```

### 2. Create Virtual Environment (Optional)
```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate       # Windows
```

### 3. Install Dependencies  
```bash
pip install -r requirements.txt
```

### 4. Prepare Data  
```bash
python prepare_data.py
```

### 5. Run the App  
```bash
streamlit run app.py
```

---

## 🧼 Data Pipeline

### 1. Raw Dataset (`anime.csv`)  
Includes:  
`anime_id`, `name`, `genre`, `type`, `episodes`, `rating`, `members`.

### 2. Cleaning (`data_cleaning.py`)  
- Converts `genre` → `genre_list`  
- Extracts `primary_genre`  
- Fills NaNs  
- Ensures numeric types  
- Drops invalid rows  

### 3. Enrichment (`prepare_data.py`)  
- Adds poster URLs  
- Saves `cleaned_anime.csv`

### 4. App Use (Streamlit)  
- Loads dataset  
- Applies filters, search, mood scoring  
- Renders UI  

---

## 🧠 Recommendation Logic

### Mood Matching  
Weights include:
- Genre match  
- Rating score  
- Popularity (`members`)  
- Mood → Genre mapping  
- Explanation text  

### More Like This  
Uses:
- Primary genre  
- Sub-genre overlap  
- Rating and popularity  
- Simple similarity heuristic  

---

## 🚀 Future Enhancements

- TF-IDF synopsis embedding similarity  
- Genre-weighted cosine similarity  
- Collaborative filtering  
- Real Crunchyroll availability  
- Studio/year filters  
- Deploy to Streamlit Cloud  

---

## 🙌 Credits

- Dataset inspired by MAL community datasets  
- Poster images from MAL/Jikan URLs  
- Built using **Streamlit**, **pandas**, **plotly**  
- Developed by **Nitin Yadav - 69199A**

---

## 🪐 Final Note  
_“Stop scrolling. Start watching.”_  
**MARS – Mood-Based Anime Recommender System**
