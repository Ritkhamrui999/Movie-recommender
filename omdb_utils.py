# omdb_utils.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env into environment

OMDB_API_KEY = os.getenv("OMDB_API_KEY")

def fetch_movie_metadata(title):
    try:
        url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":
                return {
                    "poster": data.get("Poster", ""),
                    "rating": data.get("imdbRating", "N/A"),
                    "genre": data.get("Genre", "N/A"),
                    "plot": data.get("Plot", "No plot available"),
                    "year": data.get("Year", "N/A")
                }
    except:
        pass
    return {
        "poster": "",
        "rating": "N/A",
        "genre": "N/A",
        "plot": "No plot available",
        "year": "N/A"
    }
