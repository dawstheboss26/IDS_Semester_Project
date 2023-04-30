import tensorflow_hub as hub
import pandas as pd 
import pprint
import json
from collections import defaultdict
import sys
import os
import re
import editdistance
import numpy as np
from numpy.linalg import norm

# load USE library and data from the Kaggle Movies dataset
os.environ['TFHUB_CACHE_DIR'] = '/data'
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
meta = pd.read_csv("data/movies_metadata.csv")
credit = pd.read_csv("data/credits.csv")

# fullVector holds every movie and its data
# fieldLengths holds the length of each field (i.e. genre, year, rating) and weights
fullVector = []
fieldLengths = []

# add movies to vector space
for movie in meta["original_title"]: 
    fullVector.append([movie])

# add ratings and normalize them -- highest is 10
for count, rating in enumerate(meta["vote_average"]):
    rating /= 10
    fullVector[count].append(rating)
# example: one column for ratings and we weight it at 15%
fieldLengths.append((1, 0.15))

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
fieldLengths.append((1, 0.1))

# add columns for 21 genres
# genres: Music, Family, Drama, Horror, War, Documentary, Adventure, TV Movie, Animation, Mystery, Action, Science Fiction
#         Foreign, Comedy, Crime, Romance, History, Aniplex, Western, Fantasy, Thriller
genre_dict = {}
genre_list = ["Music", "Family", "Drama", "Horror", "War", "Documentary", "Adventure", "Tv Movie", "Animation", "Mystery", "Action",
         "Science Fiction", "Foreign", "Comedy", "Crime", "Romance", "History", "Aniplex", "Western", "Fantasy", "Thriller"]
for count, genre in enumerate(genre_list):
    genre_dict[genre] = count
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

fieldLengths.append((21, 0.3))

# add columns for cast (crop top X actors/actresses)
castDict = {}
castNames = {}
creditIDs = credit['id']
for count, cast in enumerate(credit['cast']):
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

# get top x actors/actresses to put in the vector space
sortedKeys = list(sorted(castDict.keys(), key=lambda x: len(castDict[x]), reverse=True))
newCastDict = {}
sortedKeys = sortedKeys[:300]
for item in sortedKeys:
    newCastDict[item] = castDict[item]
castDict = {} 
castDict = dict(sorted(newCastDict.items()))

#package the names and indexes for saving
outCastDict = {}
# add to vector space -- 0 if actor is not in the movie, 1 if actor is in the movie
movieActorLookup = defaultdict(list)
for i, aid in enumerate(castDict.keys()):
    #package names and their indexes
    outCastDict[castNames[aid]] = i
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

fieldLengths.append((len(castDict), 0.15))

# add columns for description using the USE API and stick on vector space -- crop length
for i, d in enumerate(meta['overview']):
    try:
        e1 = embed([d]).numpy().tolist()[0]
        e = [(x+1)/2 for x in e1]
    except:
        e = [0]*512
    if (i % 1000 == 0):
        print(f'embedding description {i}/{len(meta["overview"])}')
    fullVector[i].extend(e)

fieldLengths.append((len(e), 0.23))

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
sortedKeys = sortedKeys[:300]

for item in sortedKeys:
    newDirDict[item] = dirDict[item]
dirDict = dict(sorted(newDirDict.items()))

dirDict = dict(sorted(dirDict.items()))
movieDirectorLookup = defaultdict(list)

outDirDict = {}
for i, did in enumerate(dirDict.keys()):
    #package directors
    outDirDict[directorNames[did]] = i

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

fieldLengths.append((len(dirVector), 0.07))

# get final outputs
outDict = {}
outDict['fullVector'] = fullVector
outDict['names'] = meta["original_title"].tolist()
outDict['fieldLengths'] = fieldLengths
outDict['genreDict'] = genre_dict
outDict['castDict'] = outCastDict
outDict['dirDict'] = outDirDict

fout = open('data/fullVectorData.json', 'w')
fout.write(json.dumps(outDict))