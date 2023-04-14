#import tensorflow as tf 
#from keras.preprocessing.text import Tokenizer
#from keras.preprocessing.text import tokenizer_from_json
#from keras.preprocessing.sequence import pad_sequences
#from tensorflow import keras

import pandas as pd 

import sys

meta = pd.read_csv("data/movies_metadata.csv")

fullVector = []

# add movies to vector space
for movie in meta["original_title"]: 
    fullVector.append([movie])

# add ratings and normalize them -- highest is 10
for count, rating in enumerate(meta["vote_average"]):
    rating /= 10
    fullVector[count].append(rating)

# add year and normalize -- highest is 2020
for count, year in enumerate(meta["release_date"]):
    if pd.isna(year):
        year = 0
    else:
        year = year[0:4]
        year = int(year)
        if year < 1900:
            year = 1900
        year /= 2020

    fullVector[count].append(year)

# # add columns for 21 genres
# genres: Music, Family, Drama, Horror, War, Documentary, Adventure, TV Movie, Animation, Mystery, Action, Science Fiction
#         Foreign, Comedy, Crime, Romance, History, Aniplex, Western, Fantasy, Thriller

genre_list = ["Music", "Family", "Drama", "Horror", "War", "Documentary", "Adventure", "TV Movie", "Animation", "Mystery", "Action",
         "Science Fiction", "Foreign", "Comedy", "Crime", "Romance", "History", "Aniplex", "Western", "Fantasy", "Thriller"]
for count, genres in enumerate(meta["genres"]):
    genre_vector = [0] * 21

    movie_genres = []
    genres = genres.replace("'id':", "")
    num_genres = genres.count(":")
    genres = genres.split(":")
    
    for i in range(num_genres):
        g = genres[i + 1]
        g = g.split("'")[1]
        movie_genres.append(g)

    for category in movie_genres:
        for num, c in enumerate(genre_list):
            if category == c:
                genre_vector[num] = 1

    fullVector[count].extend(genre_vector)

print(fullVector[0])
    
# # add columns for cast (crop top X actors/actresses)

# # add columns for description using the USE API and stick on vector space -- crop length

# # add columns for director using the USE API and stick on vector space -- crop length

# #* checkpoint 1
# # weight columns/column ranges with cosine similarities

# #* checkpoint 2 
# # ask the user for their favorite movie

# # calculate the cosine similarity for the favorite movie with the movies in the vector space

# # return the recommended movie