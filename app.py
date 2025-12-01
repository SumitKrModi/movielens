from flask import Flask, render_template, request
from recommender import (
    recommend_with_posters,
    filter_by_genre,
    get_all_titles,
)

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    query = ""
    genre = ""
    movies = []

    if request.method == "POST":
        query = request.form.get("movie_name", "").strip()
        genre = request.form.get("genre", "").strip()

        if query:
            # Take a bigger pool so genre filter has choices
            movies = recommend_with_posters(query, top_n=30)
            movies = filter_by_genre(movies, genre)

    titles = get_all_titles(limit=5906)

    return render_template(
        "index.html",
        query=query,
        genre=genre,
        movies=movies,
        titles=titles,
    )


if __name__ == "__main__":
    app.run()
