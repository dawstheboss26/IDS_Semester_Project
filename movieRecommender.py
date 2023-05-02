import json
import editdistance
import numpy as np
import openai
from numpy.linalg import norm
from enum import Enum

openai.api_key_path = "apikey.txt"

# open the data from prototype.py (vector space, list of movies, and field lengths)
fin = open('data/fullVectorData.json', 'r')
inDictJson = fin.read()
inDict = json.loads(inDictJson)
fullVector = inDict['fullVector']
names = inDict['names']
fieldLengths = inDict['fieldLengths']
genreDict = inDict['genreDict']
castDict = inDict['castDict']
dirDict = inDict['dirDict']
newVec = fullVector.copy()

fin = open('data/descriptions.json', 'r')
inDictJson = fin.read()
descriptions = json.loads(inDictJson)

#open state category training data
tin = open('data/chatGPTprompt.txt')
prompt = tin.read().strip()
class State(Enum):
    ANOTHER = 1
    START_OVER = 2
    SPECIFY_GENRE = 3
    SPECIFY_DIRECTOR = 4
    SPECIFY_ACTOR = 5
    ACCEPT = 6
    DESCRIPTION = 7
    UNK = 8

genres = {"Music", "Family", "Drama", "Horror", "War", "Documentary", "Adventure", "TV Movie", "Animation", "Mystery", "Action",
         "Science Fiction", "Foreign", "Comedy", "Crime", "Romance", "History", "Aniplex", "Western", "Fantasy", "Thriller"}

def calcEditDistance(target, vector):
    bestED = float('inf')
    bestMatch = None
    for index, item in enumerate(vector):
        newED = editdistance.eval(target, item)
        if bestED > newED:
            bestED = newED
            bestMatch = (item, index)

    return bestMatch

def findTargetMovie():
    # get user input and use edit distance to get the most similar movie to the one they provide
    uinput = input("\nName a movie that you want the recommended movie to be similar to: ")
    bestED = float('inf')
    bestTitleIndex = None
    for i, name in enumerate(names):
        newED = editdistance.eval(uinput, name)
        if bestED > newED:
            bestED = newED
            bestTitleIndex = (name, i)

    print("\nFinding similar movies to " + bestTitleIndex[0])
    return bestTitleIndex

def calcCosineSim(bestTitleIndex, library = fullVector):
    # based on the user input's movie as target, find the cosine similarity between that target and every other one
    target = fullVector[bestTitleIndex[1]]
    cosines = []
    # rating, year, genre, cast, desc, dir
    for i, potential in enumerate(library):
        if potential[0] == target[0]:
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

def recommend(cosines, mIndex = 0, names = names): 
    # the recommended movie is the one with the highest cosine similarity
    movCos = zip(names, cosines)
    movCos = sorted(movCos, key=lambda x: x[1], reverse=True)
    rec = movCos[mIndex][0]

    print(f'\nI would suggest: {rec}')
    return rec

def determineNextState():
    uinput = input("\n> ")
    textClass = None

    # use ChatGPT API here for text classification -- send uinput to it
    #chatInput = [{"role": "user", "content": "you are a sentence classifier. Sentences I give you will be one of these 7 classes: Class 1 is asking for another reccommendation. Class 2 is starting over. Class 3 is specifying genres. Class 4 is specifying directors. Class 5 is specifying actors. Class 6 is confirming the recommendation. Classify a sentence as class 7 if it doesn't fit in classes 1, 2, 3, 4, 5, or 6. Respond with the format: <class number>. Here is the sentence:\n" + uinput}]
    chatInput = [{"role": "user", "content": prompt + '"' + uinput + '"'}]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=chatInput)
    reply = response['choices'][0]['message']['content']
    #print(reply)
    try:
        theClass = int(reply)
    except:
        print("\nCould not parse chatGPT classifier response. Try again")
        return (State.UNK, "")

    if reply == "1":
        textClass = State.ANOTHER
    if reply == "2":
        #! this state is never selected
        textClass = State.START_OVER
    if reply == "3":
        textClass = State.SPECIFY_GENRE
    if reply == "4":
        textClass = State.SPECIFY_DIRECTOR
    if reply == "5":
        textClass = State.SPECIFY_ACTOR
    if reply == "6":
        textClass = State.ACCEPT
    if reply == "7":
        textClass = State.DESCRIPTION
    if reply == "8": 
        textClass = State.UNK
        
    # print(textClass)
    return (textClass, uinput)
    

    # next states include: ANOTHER, SIMILAR_MOVIE, SPECIFY_GENRE, SPECIFY_DIRECTOR, SPECIFY_ACTOR, ACCEPT

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

recMovie = recommend(cosines, mIndex)

subNames = names
subCosines = cosines
subFullVector = fullVector

while (not accept):
    nextState, uinput = determineNextState()
    
    if nextState == State.ANOTHER:
        mIndex += 1
        recMovie = recommend(cosines, mIndex)
    elif nextState == State.START_OVER:
        mIndex = 0
        bestTitleIndex = findTargetMovie()
        cosines = calcCosineSim(bestTitleIndex)
        # update sub vectors
        subNames = names
        subCosines = cosines
        subFullVector = fullVector
        recMovie = recommend(cosines, mIndex)
    elif nextState == State.SPECIFY_GENRE:
        mIndex = 0
        # genres start at fullVector index 3
        uinput = input("Enter the genre you would like --> ")
        name, genre = calcEditDistance(uinput, genreDict.keys())
        print(f"\nLooking for a movie in the {name} genre")
        subFullVector = [movie for movie in subFullVector if movie[genre + 3] == 1]
        subNames = [movie[0] for movie in subFullVector]
        subCosines = calcCosineSim(bestTitleIndex, subFullVector)
        recMovie = recommend(subCosines, mIndex, subNames)
    elif nextState == State.SPECIFY_DIRECTOR:
        mIndex = 0
        # directors start at fullVector index 836 (check again)
        uinput = input("Enter the director you would like --> ")
        director = calcEditDistance(uinput, dirDict.keys())[0]
        print(f"\nLooking for a movie with {director} as the director")
        subFullVector = [movie for movie in subFullVector if movie[dirDict[director] + 836] == 1]
        subNames = [movie[0] for movie in subFullVector]
        subCosines = calcCosineSim(bestTitleIndex, subFullVector)
        recMovie = recommend(subCosines, mIndex, subNames)
    elif nextState == State.SPECIFY_ACTOR:
        mIndex = 0
        uinput = input("Enter the actor/actress you would like --> ")
        # cast start at fullVector index 24
        actor = calcEditDistance(uinput, castDict.keys())[0]
        print(f"\nLooking for a movie with {actor}")
        subFullVector = [movie for movie in subFullVector if movie[castDict[actor] + 24] == 1]
        subNames = [movie[0] for movie in subFullVector]
        subCosines = calcCosineSim(bestTitleIndex, subFullVector)
        recMovie = recommend(subCosines, mIndex, subNames)
    elif nextState == State.DESCRIPTION:
        print(f"\n{recMovie} Overview:")
        print(descriptions[recMovie])
    elif nextState == State.UNK:
        print("\nI'm sorry, I don't understand how that pertains to movies.")
        continue
    else:
        accept = 1
        print("\nHappy watching!")