import json
import editdistance
import numpy as np
from numpy.linalg import norm

fin = open('data/fullVectorData.json', 'r')
inDictJson = fin.read()
inDict = json.loads(inDictJson)
names = inDict['names']
fullVector = inDict['fullVector']
newVec = fullVector.copy()
for i, x in enumerate(fullVector):
    for j, y in enumerate(x):
        if y == 0:
            newVec[i][j] = 0.01
        else:
            newVec[i][j] = y
fullVector = newVec


fieldLengths = inDict['fieldLengths']

uinput = input("Enter your favorite movie -->  ")
bestED = float('inf')
bestTitleIndex = None
for i, name in enumerate(names):
    newED = editdistance.eval(uinput, name)
    if bestED > newED:
        bestED = newED
        bestTitleIndex = (name, i)

print("Finding similar movies to "+bestTitleIndex[0])

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
        #print(f'{subTarget} compared to {subPotential}')
        try:
            almost = subVecInfo[1] * (np.dot(subTarget,subPotential)/(norm(subTarget)*norm(subPotential)))
        #print(acc)
        except:
            almost = 0

        acc += almost
    
    #print(acc)
    #exit()
    cosines.append(acc)

    cosines 
#res = np.argmax(cosines, axis=0)
#print(cosines)
res = max(cosines)
index = cosines.index(res)

print(f'I would suggest: {names[index]}')