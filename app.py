# app.py
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import difflib
import ast
from omdb_utils import fetch_movie_metadata

# Load and merge datasets
movies = pd.read_csv("movies.csv")
credits = pd.read_csv("credits.csv")
data_set = movies.merge(credits, on='title')

# Helper functions
def get_director(crew):
    try:
        crew_list = ast.literal_eval(crew)
        for member in crew_list:
            if member.get('job') == 'Director':
                return member.get('name')
    except:
        return ''
    return ''

def get_top_cast(cast):
    try:
        cast_list = ast.literal_eval(cast)
        return ' '.join([member['name'] for member in cast_list[:3]])
    except:
        return ''

# Process features
data_set['director'] = data_set['crew'].apply(get_director)
data_set['cast'] = data_set['cast'].apply(get_top_cast)

selected_features = ['genres', 'keywords', 'tagline', 'overview', 'cast', 'director']
for feature in selected_features:
    data_set[feature] = data_set[feature].fillna('')
data_set['combined_features'] = data_set.apply(lambda row: ' '.join([row[feature] for feature in selected_features]), axis=1)

# TF-IDF + similarity
vectorizer = TfidfVectorizer()
feature_vectors = vectorizer.fit_transform(data_set['combined_features'])
similarity = cosine_similarity(feature_vectors)

# Recommendation logic
def recommend_movies(movie_name):
    movie_titles = data_set['title'].tolist()
    find_match = difflib.get_close_matches(movie_name, movie_titles)
    if not find_match:
        return None, None
    close_match = find_match[0]
    index_of_movie = data_set[data_set.title == close_match].index[0]
    similarity_scores = list(enumerate(similarity[index_of_movie]))
    sorted_similar_movies = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:11]

    recommendations = []
    for idx, score in sorted_similar_movies:
        title = data_set.iloc[idx]['title']
        metadata = fetch_movie_metadata(title)
        poster = metadata['poster'] if metadata['poster'] and metadata['poster'] != "N/A" else "https://via.placeholder.com/300x450?text=No+Image"
        recommendations.append({
            'title': title,
            'plot': metadata['plot'],
            'poster': poster,
            'rating': metadata['rating'],
            'genre': metadata['genre'],
            'year': metadata['year']
        })
    return close_match, recommendations

# Streamlit UI
st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")
st.title("🎬 Movie Recommendation System (OMDb Enhanced)")

movie_input = st.text_input("Enter your favorite movie:")

if movie_input:
    match, recs = recommend_movies(movie_input)
    if match and recs:
        st.subheader(f"Movies similar to **{match}**")
        for rec in recs:
            cols = st.columns([1, 2])
            with cols[0]:
                st.image(rec['poster'], width=200)
            with cols[1]:
                st.markdown(f"### {rec['title']} ({rec['year']})")
                st.markdown(f"**Genre:** {rec['genre']}")
                st.markdown(f"**IMDb Rating:** ⭐ {rec['rating']}")
                st.markdown(f"**Plot:** {rec['plot']}")
                st.markdown("---")
    else:
        st.error("Movie not found. Try another title.")

