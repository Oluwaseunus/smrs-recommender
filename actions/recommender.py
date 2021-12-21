import re
import ssl
import nltk
import threading
import numpy as np
import pandas as pd

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('stopwords')
nltk.download('punkt')

data = pd.read_csv('./netflix_titles.csv')
data.head()

data.groupby('type').count()

data = data.dropna(subset=['cast', 'country', 'rating'])

movies = data[data['type'] == 'Movie'].reset_index()
movies = movies.drop(['index', 'show_id', 'type', 'date_added',
                     'release_year', 'duration', 'description'], axis=1)
movies.head()

actors = []

for i in movies['cast']:
    actor = re.split(r', \s*', i)
    actors.append(actor)

flat_list = []
for sublist in actors:
    for item in sublist:
        flat_list.append(item)

actors_list = sorted(set(flat_list))

binary_actors = [[0] * 0 for i in range(len(set(flat_list)))]

for i in movies['cast']:
    k = 0
    for j in actors_list:
        if j in i:
            binary_actors[k].append(1.0)
        else:
            binary_actors[k].append(0.0)
        k += 1

binary_actors = pd.DataFrame(binary_actors).transpose()

directors = []

for i in movies['director']:
    if pd.notna(i):
        director = re.split(r', \s*', i)
        directors.append(director)

flat_list2 = []

for sublist in directors:
    for item in sublist:
        flat_list2.append(item)

directors_list = sorted(set(flat_list2))

binary_directors = [[0] * 0 for i in range(len(set(flat_list2)))]

for i in movies['director']:
    k = 0
    for j in directors_list:
        if pd.isna(i):
            binary_directors[k].append(0.0)
        elif j in i:
            binary_directors[k].append(1.0)
        else:
            binary_directors[k].append(0.0)
        k += 1

binary_directors = pd.DataFrame(binary_directors).transpose()

countries = []

for i in movies['country']:
    country = re.split(r', \s*', i)
    countries.append(country)

flat_list3 = []

for sublist in countries:
    for item in sublist:
        flat_list3.append(item)

countries_list = sorted(set(flat_list3))

binary_countries = [[0] * 0 for i in range(len(set(flat_list3)))]

for i in movies['country']:
    k = 0
    for j in countries_list:
        if j in i:
            binary_countries[k].append(1.0)
        else:
            binary_countries[k].append(0.0)
        k += 1

binary_countries = pd.DataFrame(binary_countries).transpose()

genres = []

for i in movies['listed_in']:
    genre = re.split(r', \s*', i)
    genres.append(genre)

flat_list4 = []

for sublist in genres:
    for item in sublist:
        flat_list4.append(item)

genres_list = sorted(set(flat_list4))

binary_genres = [[0] * 0 for i in range(len(set(flat_list4)))]

for i in movies['listed_in']:
    k = 0
    for j in genres_list:
        if j in i:
            binary_genres[k].append(1.0)
        else:
            binary_genres[k].append(0.0)
        k += 1

binary_genres = pd.DataFrame(binary_genres).transpose()

ratings = []

for i in movies['rating']:
    ratings.append(i)

ratings_list = sorted(set(ratings))

binary_ratings = [[0] * 0 for i in range(len(set(ratings_list)))]

for i in movies['rating']:
    k = 0
    for j in ratings_list:
        if j in i:
            binary_ratings[k].append(1.0)
        else:
            binary_ratings[k].append(0.0)
        k += 1

binary_ratings = pd.DataFrame(binary_ratings).transpose()

binary = pd.concat([binary_actors, binary_directors,
                   binary_countries, binary_genres], axis=1, ignore_index=True)


def recommender(current_search):
    cs_list = []
    binary_list = []
    if current_search in movies['title'].values:
        idx = movies[movies['title'] == current_search].index.item()
        for i in binary.iloc[idx]:
            binary_list.append(i)
        point1 = np.array(binary_list).reshape(1, -1)
        point1 = [val for sublist in point1 for val in sublist]
        for j in range(len(movies)):
            binary_list2 = []
            for k in binary.iloc[j]:
                binary_list2.append(k)
            point2 = np.array(binary_list2).reshape(1, -1)
            point2 = [val for sublist in point2 for val in sublist]
            dot_product = np.dot(point1, point2)
            norm_1 = np.linalg.norm(point1)
            norm_2 = np.linalg.norm(point2)
            cos_sim = dot_product / (norm_1 * norm_2)
            cs_list.append(cos_sim)
        movies_copy = movies.copy()
        movies_copy['cos_sim'] = cs_list
        results = movies_copy.sort_values('cos_sim', ascending=False)
        results = results[results['title'] != current_search]
        top_results = results.head(5)
        return(top_results)
    else:
        return("Title not in dataset. Please check spelling.")


list_results = []


class threader(threading.Thread):
    def __init__(self, title):
        threading.Thread.__init__(self)
        self.title = title

    def run(self):
        print("Starting recommender for " + self.title + "\n")
        result = recommender(self.title)
        result = result.sort_values('cos_sim', ascending=False)
        result = result.head(10)
        list_results.append(result)


def top_movie_recommender(*args):
    results = pd.DataFrame([])
    list_threads = []

    for arg in args:
        print(arg)
        current_recommender = threader(arg)
        list_threads.append(current_recommender)
        current_recommender.start()

    for thread in list_threads:
        thread.join()

    for result in list_results:
        result
        print(result)
        result = pd.DataFrame(result)
        results = pd.concat([results, result])

    results = results.sort_values('cos_sim', ascending=False)
    results = results.head(10)
    list_titles = results["titles"].to_numpy()
    return(list_titles)


final_answer = top_movie_recommender(
    'The Conjuring', 'Wild Child', 'Creep', 'Desolation')
print(final_answer)
