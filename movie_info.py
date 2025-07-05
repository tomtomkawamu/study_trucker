import requests

TMDB_API_KEY = "YOUR_TMDB_API_KEY"

def get_movie_info(title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    response = requests.get(url).json()
    if response["results"]:
        movie = response["results"][0]
        movie_id = movie["id"]
        details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
        details = requests.get(details_url).json()
        director = "Unknown"
        for crew in details.get("credits", {}).get("crew", []):
            if crew["job"] == "Director":
                director = crew["name"]
                break
        return {"公開年": movie["release_date"][:4], "監督": director}
    return None