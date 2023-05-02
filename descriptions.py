import pandas as pd 
import json

meta = pd.read_csv("data/movies_metadata.csv")

descriptions = dict()

for i, movie in enumerate(meta["original_title"]):
    descriptions[movie] = meta["overview"][i]

fout = open('data/descriptions.json', 'w')
fout.write(json.dumps(descriptions))