from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests

app = Flask(__name__)
CORS(app)

# Load datasets
movies = pd.read_csv('tmdb_5000_movies.csv')
credits = pd.read_csv('tmdb_5000_credits.csv')

# Merge datasets on title
movies = movies.merge(credits, on='title')

# Select relevant columns
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
movies.dropna(inplace=True)

# Helper functions to process data
def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L

def convert3(obj):
    L = []
    counter = 0
    for i in ast.literal_eval(obj):
        if counter != 3:
            L.append(i['name'])
            counter += 1
        else:
            break
    return L

def fetch_director(obj):
    L = []
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            L.append(i['name'])
            break
    return L

movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(convert3)
movies['crew'] = movies['crew'].apply(fetch_director)
movies['overview'] = movies['overview'].apply(lambda x: x.split())
movies['genres'] = movies['genres'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['keywords'] = movies['keywords'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['cast'] = movies['cast'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['crew'] = movies['crew'].apply(lambda x: [i.replace(" ", "") for i in x])

movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']
new_df = movies[['movie_id', 'title', 'tags']]

# Vectorization and similarity calculation
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(new_df['tags'].apply(lambda x: " ".join(x))).toarray()
similarity_matrix = cosine_similarity(vectors)

def get_recommendations(movie):
    try:
        movie_index = new_df[new_df['title'] == movie].index[0]
        distances = similarity_matrix[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        recommendations = [new_df.iloc[i[0]].title for i in movies_list]
        return recommendations
    except Exception as e:
        print(f"Error in getting recommendations: {e}")
        return []

@app.route('/recommend', methods=['POST'])
def recommend_movies():
    data = request.json
    movie = data.get('movie')
    recommendations = get_recommendations(movie)
    poster_urls = []
    api_key = "f40cffb4"

    for rec in recommendations:
        url = f"http://www.omdbapi.com/?t={rec}&apikey={api_key}"
        response = requests.get(url)
        data = response.json()
        if 'Poster' in data and data['Poster'] != 'N/A':
            poster_urls.append({'title': rec, 'poster_url': data['Poster']})
        else:
            poster_urls.append({'title': rec, 'poster_url': 'https://via.placeholder.com/150'})

    return jsonify({'recommendations': poster_urls})


@app.route('/movies', methods=['GET'])
def get_movies():
    movie_titles = new_df['title'].tolist()
    return jsonify({'movies': movie_titles})

@app.route('/posters', methods=['GET'])
def get_posters():
    movie_titles = new_df['title'].tolist()
    api_key = "f40cffb4"
    posters = []
    for title in movie_titles:
        url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}"
        response = requests.get(url)
        data = response.json()
        if 'Poster' in data and data['Poster'] != 'N/A':
            posters.append({'title': title, 'poster_url': data['Poster']})
        else:
            posters.append({'title': title, 'poster_url': 'https://via.placeholder.com/150'})
    return jsonify({'posters': posters})

if __name__ == '__main__':
    app.run(debug=True)
