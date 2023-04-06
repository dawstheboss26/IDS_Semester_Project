#import tensorflow as tf 
#from keras.preprocessing.text import Tokenizer
#from keras.preprocessing.text import tokenizer_from_json
#from keras.preprocessing.sequence import pad_sequences
#from tensorflow import keras

import pandas as pd 

import sys

ratings = pd.read_csv("data/ratings.csv")
meta = pd.read_csv("data/movies_metadata.csv")
sum_rating = dict()
count_rating = dict()
avg_rating = dict()

for movie in ratings['movieId']:
    sum_rating[movie] = sum_rating.setdefault(movie, 0) + ratings['rating']
    count_rating[movie] = count_rating.setdefault(movie, 0) + 1

for movie in sum_rating:
    # get average movie rating and normalize from 0 to 1
    avg_rating[movie] = (sum_rating[movie] / count_rating[movie]) / 5 


'''
NEW STUFF below?
'''
movieVectors = dict()
for movie in meta:
    fullVector = []
    
    mid = movie['id']
    rating = float(movie['vote_average'])
    print(rating)

#! TO DO
# create vector space for movie ratings

# add year column: start at 1900 and go until 2023 (anything before 1900 is just normalized to be 1900)
    year = int(movie['release_date'][:4])
    if year < 1900:
        year = 1900
    
    #Normalizing first to zero
    year -= 1900
    # Movies span from 1900 to 2017? Maybe we can scan csv for the oldest
    year = float(year)/117.0
# add columns for genre (crop to top X genres)
    
# add columns for cast (crop top X actors/actresses)

# add columns for description using the USE API and stick on vector space -- crop length

# add columns for director using the USE API and stick on vector space -- crop length

#* checkpoint 1
# weight columns/column ranges with cosine similarities

#* checkpoint 2 
# ask the user for their favorite movie

# calculate the cosine similarity for the favorite movie with the movies in the vector space

# return the recommended movie