import pandas as pd
import requests
import time

# 1. CONFIG
TMDB_API_KEY = "6e37410e9db29b31259ce3a04ae4fc22"  # <-- put your key here
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie/{}"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w185"  # keep small & fast

INPUT_CSV = "refined_df.csv"
OUTPUT_CSV = "refined_with_posters.csv"


def fetch_poster(tmdb_id, session):
    """Return (poster_path, full_url) for a given TMDb movie id, or (None, None)."""
    if pd.isna(tmdb_id):
        return None, None

    try:
        url = TMDB_BASE_URL.format(int(tmdb_id))
        params = {
            "api_key": TMDB_API_KEY,
            "language": "en-US",
        }
        resp = session.get(url, params=params, timeout=5)
        data = resp.json()

        poster_path = data.get("poster_path")
        if not poster_path:
            return None, None

        full_url = f"{TMDB_IMAGE_BASE}{poster_path}"
        return poster_path, full_url
    except Exception as e:
        print(f"Error for id {tmdb_id}: {e}")
        return None, None


def main():
    print(f"Loading {INPUT_CSV}...")
    df = pd.read_csv(INPUT_CSV)

    if "id" not in df.columns:
        raise ValueError("Expected an 'id' column in the CSV (TMDb movie id).")

    # Create columns if not present
    if "poster_path" not in df.columns:
        df["poster_path"] = None
    if "poster_url" not in df.columns:
        df["poster_url"] = None

    session = requests.Session()
    cache = {}  # tmdb_id -> (poster_path, poster_url)

    total = len(df)
    print(f"Found {total} rows. Fetching posters from TMDb...")

    for idx, row in df.iterrows():
        tmdb_id = row["id"]

        # Skip if already filled
        if pd.notna(row.get("poster_url")) and isinstance(row["poster_url"], str):
            continue

        if tmdb_id in cache:
            poster_path, poster_url = cache[tmdb_id]
        else:
            poster_path, poster_url = fetch_poster(tmdb_id, session)
            cache[tmdb_id] = (poster_path, poster_url)
            # small sleep to be gentle with TMDb API, adjust if needed
            time.sleep(0.25)

        df.at[idx, "poster_path"] = poster_path
        df.at[idx, "poster_url"] = poster_url

        if idx % 50 == 0:
            print(f"{idx}/{total} processed...")

    print(f"Saving to {OUTPUT_CSV}...")
    df.to_csv(OUTPUT_CSV, index=False)
    print("Done.")


if __name__ == "__main__":
    main()
