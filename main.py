import pandas as pd

import os


# load the dataset

data = None 
# Step 1: Load dataset
try:
   route = os.path.join('data', 'anime.csv')
   data = pd.read_csv(route)
except FileNotFoundError:
    print("anime.csv not found in data/. Please add it to continue.")
    exit()







