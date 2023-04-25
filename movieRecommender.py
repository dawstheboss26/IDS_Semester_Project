import json
import editdistance
import numpy as np
from numpy.linalg import norm
from enum import Enum

class State(Enum):
    ANOTHER = 1
    SIMILAR_MOVIE = 2
    SPECIFY_GENRE = 3
    SPECIFY_DIRECTOR = 4
    SPECIFY_ACTOR = 5
    ACCEPT = 6

def findTargetMovie():
    # get user input and use edit distance to get the most similar movie to the one they provide
    uinput = input("Name a movie that you want the recommended movie to be similar to: ")
    bestED = float('inf')
    bestTitleIndex = None
    for i, name in enumerate(names):
        newED = editdistance.eval(uinput, name)
        if bestED > newED:
            bestED = newED
            bestTitleIndex = (name, i)

    print("Finding similar movies to " + bestTitleIndex[0])
    return bestTitleIndex

def calcCosineSim(bestTitleIndex):
    # based on the user input's movie as target, find the cosine similarity between that target and every other one
    target = fullVector[bestTitleIndex[1]]
    cosines = []
    # rating, year, genre, cast, desc, dir
    for i, potential in enumerate(fullVector):
        if i == bestTitleIndex[1]:
            cosines.append(0)
            continue
        acc = 0
        start = 1

        #subVecInfo is a tuple of (number of fields in category, category weight)
        for subVecInfo in fieldLengths:
            subTarget = target[start:subVecInfo[0]+start]
            subPotential = potential[start:subVecInfo[0]+start]
            start += subVecInfo[0]
            try:
                almost = subVecInfo[1] * (np.dot(subTarget,subPotential)/(norm(subTarget)*norm(subPotential)))
            except:
                almost = 0

            acc += almost
        
        cosines.append(acc)

        cosines 
    return cosines

def recommend(cosines, mIndex = 0): 
    # the recommended movie is the one with the highest cosine similarity
    movCos = zip(names, cosines)
    movCos = sorted(movCos, key=lambda x: x[1], reverse=True)
    rec = movCos[mIndex][0]

    print(f'I would suggest: {rec}')

def determineNextState():
    uinput = input()
    nextState = None

    # use ChatGPT API here for text classification -- send uinput to it
    textClass = State.ANOTHER

    if textClass == State.ANOTHER:
        return State.ANOTHER
    elif textClass == State.SIMILAR_MOVIE:
        return State.SIMILAR_MOVIE
    elif textClass == State.SPECIFY_GENRE:
        return State.SPECIFY_GENRE
    elif textClass == State.SPECIFY_DIRECTOR:
        return State.SPECIFY_DIRECTOR
    elif textClass == State.SPECIFY_ACTOR:
        return State.SPECIFY_ACTOR
    else:
        return State.ACCEPT

    # next states include: ANOTHER, SIMILAR_MOVIE, SPECIFY_GENRE, SPECIFY_DIRECTOR, SPECIFY_ACTOR, ACCEPT
    return nextState

# open the data from prototype.py (vector space, list of movies, and field lengths)
fin = open('data/fullVectorData.json', 'r')
inDictJson = fin.read()
inDict = json.loads(inDictJson)
fullVector = inDict['fullVector']
names = inDict['names']
fieldLengths = inDict['fieldLengths']
newVec = fullVector.copy()

# create vector space and replace 0s with 0.01
for i, x in enumerate(fullVector):
    for j, y in enumerate(x):
        if y == 0:
            newVec[i][j] = 0.01
        else:
            newVec[i][j] = y
fullVector = newVec

accept = 0
mIndex = 0

print("Hello! Welcome to the Movie Recommender 3000! What kind of movie are you looking for?")

bestTitleIndex = findTargetMovie()

cosines = calcCosineSim(bestTitleIndex)

recommend(cosines, mIndex)

while (not accept):
    nextState = determineNextState()

    if nextState == State.ANOTHER:
        mIndex += 1
        recommend(cosines, mIndex)
    elif textClass == State.SIMILAR_MOVIE:
        bestTitleIndex = findTargetMovie()
        cosines = calcCosineSim(bestTitleIndex)
        recommend(cosines, 0)
    elif textClass == State.SPECIFY_GENRE:
        continue
    elif textClass == State.SPECIFY_DIRECTOR:
        continue
    elif textClass == State.SPECIFY_ACTOR:
        continue
    else:
        accept = 1
        print("Happy watching!")