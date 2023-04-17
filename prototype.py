#import tensorflow as tf 
#from keras.preprocessing.text import Tokenizer
#from keras.preprocessing.text import tokenizer_from_json
#from keras.preprocessing.sequence import pad_sequences
#from tensorflow import keras

import pandas as pd 
import pprint
import json
from collections import defaultdict
import sys
import re

meta = pd.read_csv("data/movies_metadata.csv")
credit = pd.read_csv("data/credits.csv")

fullVector = []

#* add movies to vector space
for movie in meta["original_title"]: 
    fullVector.append([movie])

#* add ratings and normalize them -- highest is 10
for count, rating in enumerate(meta["vote_average"]):
    rating /= 10
    fullVector[count].append(rating)

#* add year and normalize -- highest is 2020
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

#* add columns for 21 genres
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
    
#* add columns for cast (crop top X actors/actresses)
'''
cast_dict = dict()
for count, cast in enumerate(credit["cast"]):
    movie_cast = []
    cast = cast.replace("'id':", "")
    cast = cast.replace("'cast_id':", "")
    cast = cast.replace("'character':", "")
    cast = cast.replace("'credit_id':", "")
    cast = cast.replace("'gender':", "")
    cast = cast.replace("'order':", "")
    cast = cast.replace("'profile_path':", "")
    num_cast = cast.count(":")
    cast = cast.split(":")

    for i in range(num_cast):
        c = cast[i + 1]
        try:
            c = c.split("'")[1]
            if c == ",  ":
                continue
            movie_cast.append(c)
        except:
            continue

    for actor in movie_cast:
        cast_dict[actor] = cast_dict.setdefault(actor, 0) + 1

sorted_cast_dict = dict(sorted(cast_dict.items(), key=lambda x:x[1], reverse=True))

top_100_cast = list(sorted_cast_dict.keys())[0:100]

for count, cast in enumerate(credit["cast"]):
    cast_vector = [0] * 100
    for num, actor in enumerate(top_100_cast):
        if actor in cast:
            cast_vector[num] = 1
    # for i in range(len(fullVector)):
    #     for actor in cast_vector:
    #         fullVector[i].append(actor)
    fullVector[count].extend(cast_vector)
'''
castDict = {}
castNames = {}
creditIDs = credit['id']
for count, cast in enumerate(credit['cast']):
    #print(cast)
    m = re.findall("'id': ([0-9A-Za-z\s]*), 'name': '([0-9A-Za-z\s]*)',", cast)
    if len(m) > 0:
        for match in m:
            aid = match[0]
            name = match[1]
            mid = creditIDs[count]
            if aid not in castDict:
                castDict[aid] = [mid]
            else:
                castDict[aid].append(mid)
            castNames[aid] = name      

#print(len(dirDict))
sortedKeys = list(sorted(castDict.keys(), key=lambda x: len(castDict[x]), reverse=True))
newCastDict = {}
sortedKeys = sortedKeys[:100]
for item in sortedKeys:
    newCastDict[item] = castDict[item]
castDict = {} 
castDict = dict(sorted(newCastDict.items()))
movieActorLookup = defaultdict(list)
for i, aid in enumerate(castDict.keys()):
    mids = castDict[aid]
    for mid in mids:
        movieActorLookup[mid].append(i)
castVector = []
for i, mid in enumerate(meta['id']):
    castVector = [0] * len(castDict)
    try:
        for index in movieActorLookup[int(mid)]:
            castVector[index] = 1
    except:   
        fullVector[i].extend(castVector)
        continue
    fullVector[i].extend(castVector)
#! error: credits has 10 more rows than metadata --> have to match up with ID
# print(fullVector[1])

# # add columns for description using the USE API and stick on vector space -- crop length

# # add columns for director using the USE API and stick on vector space -- crop length
dirDict = {}
directorNames = {}
creditIDs = credit['id']
for count, crew in enumerate(credit['crew']):
    m = re.findall("'id': ([0-9A-Za-z\s]*), 'job': 'Director', 'name': '([0-9A-Za-z\s]*)',", crew)
    if len(m) > 0:
        for match in m:
            did = match[0]
            name = match[1]
            mid = creditIDs[count]
            if did not in dirDict:
                dirDict[did] = [mid]
            else:
                dirDict[did].append(mid)
            directorNames[did] = name

# get top 100 directors
sortedKeys = list(sorted(dirDict.keys(), key=lambda x: len(dirDict[x]), reverse=True))
newDirDict = {}
sortedKeys = sortedKeys[:100]

for item in sortedKeys:
    newDirDict[item] = dirDict[item]
dirDict = dict(sorted(newDirDict.items()))

dirDict = dict(sorted(dirDict.items()))
movieDirectorLookup = defaultdict(list)
for i, did in enumerate(dirDict.keys()):
    mids = dirDict[did]
    for mid in mids:
        movieDirectorLookup[mid].append(i)

dirVector = []
for i, mid in enumerate(meta['id']):
    dirVector = [0] * len(dirDict)
    try:
        for index in movieDirectorLookup[int(mid)]:
            dirVector[index] = 1
    except:
        fullVector[i].extend(dirVector)
        continue
    fullVector[i].extend(dirVector)
print(fullVector[0])
# #* checkpoint 1
# # weight columns/column ranges with cosine similarities

# #* checkpoint 2 
# # ask the user for their favorite movie

# # calculate the cosine similarity for the favorite movie with the movies in the vector space

# # return the recommended movie