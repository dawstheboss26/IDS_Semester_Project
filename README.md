# Welcome to the Movie Recommender 3000!
## Setting up your environment
```
pip install -r requirements.txt
```

## Download the online CSV data
Go to this [website](https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset?select=movies_metadata.csv)  
Download the **credits.csv** and **movies_metadata.csv**  
Place them in the **data** folder

## ChatGPT Key
When you pull, remove any apikey.txt file, then rename apikeyCMC.txt to apikey.txt. 

## Make the model
Run the below command to generate the model  
Check that a file called **fullVectorData.json** was added to the **data** folder
```
python3 prototype.py
```

## Boot up the system!
```
python3 movieRecommender.py
```
