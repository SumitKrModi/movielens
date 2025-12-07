import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset with posters pre-fetched
# Expected columns now: id, title, tags, poster_url (and maybe poster_path)
movies = pd.read_csv("refined_with_posters.csv")

def get_poster(id):
    return movies.loc[movies.id == id, "poster_url"].values[0]

# Precompute title -> tags map for fast lookup
title_to_tags = dict(
    zip(movies["title"].str.lower(), movies["tags"].str.lower())
)

# Basic cleanup
movies["tags"] = movies["tags"].fillna("")
if "poster_url" not in movies.columns:
    movies["poster_url"] = None

# Vectorize tags
cv = CountVectorizer(max_features=5000, stop_words="english")
vectors = cv.fit_transform(movies["tags"]).toarray()

# Cosine similarity matrix
similarity = cosine_similarity(vectors)


def recommend_with_posters(movie_title, top_n=10):
    """
    Given a movie title, return a list of similar movies with:
    - title
    - poster URL (from CSV, no API call)
    - similarity score
    """
    movie_title = (movie_title or "").strip().lower()
    if not movie_title:
        return []

    # Exact case insensitive match
    matches = movies[movies["title"].str.lower() == movie_title]

    # Fallback: contains
    if matches.empty:
        matches = movies[movies["title"].str.lower().str.contains(movie_title)]

    if matches.empty:
        return []

    idx = matches.index[0]

    distances = list(enumerate(similarity[idx]))
    distances = sorted(distances, key=lambda x: x[1], reverse=True)

    # Skip the first one (same movie)
    distances = distances[1 : top_n + 1]

    recommendations = []
    for i, score in distances:
        row = movies.iloc[i]

        recommendations.append(
            {
                "title": row["title"],
                "poster": row.get("poster_url", None),
                "score": float(score),
            }
        )

    return recommendations

def filter_by_genre(recommendations, genre):
    """
    Filter a list of recommendation dicts using the tags column.
    Genre is matched as a lowercase word inside tags.
    """
    genre = (genre or "").strip().lower()
    if not genre:
        return recommendations

    filtered = []
    for rec in recommendations:
        tags = title_to_tags.get(rec["title"].lower(), "")
        if genre in tags:
            filtered.append(rec)

    return filtered


def get_all_titles(limit=None):
    """
    Return a sorted list of unique movie titles for the search datalist.
    """
    titles = movies["title"].dropna().unique()
    titles = sorted(titles)
    if limit:
        titles = titles[:limit]
    return titles
