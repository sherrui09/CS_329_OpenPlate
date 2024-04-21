import pandas as pd # type: ignore
from pandas import DataFrame # type: ignore
from keybert import KeyBERT # type: ignore
import numpy as np # type: ignore
import time
from fuzzywuzzy import fuzz # type: ignore
import csv

from embedded_recipes import SAMPLE_RECIPES

# encode RECIPES with BERT it takes hella long, can I like
def return_top_recipes(calories_per_meal: int, taste_profile: str, dietary_restriction: str, n_recipes: int):
    
    caloric_multiplier = 1 # alter value... (should be > 1)
    caloric_deviation = calories_per_meal * caloric_multiplier
    min_calories_per_meal, max_calories_per_meal = calories_per_meal - caloric_deviation, calories_per_meal + caloric_deviation
    # null_calories_count = RECIPES['calories'].isnull().sum()

    selected_recipes_df = SAMPLE_RECIPES[(SAMPLE_RECIPES['calories'] >= min_calories_per_meal) & (SAMPLE_RECIPES['calories'] <= max_calories_per_meal)]
    selected_recipes_df.reset_index(drop=True, inplace=True)

    if dietary_restriction != "":
        for index, recipe in selected_recipes_df.iterrows():
            recipe_info = recipe['summary'] + ' ' + recipe['name']
            if dietary_restriction in recipe_info:
              print(recipe_info) # implement l8r

    if len(selected_recipes_df) < n_recipes:
        raise ValueError(f'There are not n_recipes in selected_recipes_df. Choose value lower than {len(selected_recipes_df)}')

    print(f'# of Selected Recipes: {len(selected_recipes_df)}')
    similarity_scores = []
    taste_keywords = KeyBERT().extract_keywords(taste_profile)
    key_words  = [word for word, _ in taste_keywords]
    
    start = time.time()
    for index in range(len(RECIPE_KEYWORDS)):
      recipe_words = RECIPE_KEYWORDS[index]
      denom = len(key_words)
      if denom != 0: # avoid div by 0
        score = 0
        for key_word in key_words:
          score += fuzz.partial_ratio(key_word, recipe_words) / denom
        similarity_scores.append((index, score))
    end = time.time()
    print(f'Fuzzy Algorithm Time: {round(end - start, 3)} seconds')
    
    similarity_scores.sort(key=lambda x: x[1], reverse=True) # sort by highest mean
    top_indices = [index for index, _ in similarity_scores]
    top_n_indices = top_indices[:n_recipes]
    
    top_recipes = [SAMPLE_RECIPES.iloc[index] for index in top_n_indices]
    top_recipes_name = [SAMPLE_RECIPES['name'][index] for index in top_n_indices]
    print(top_recipes_name)
    
    return top_recipes

RECIPE_KEYWORDS = []

def main():
    calories_per_meal = 800
    taste_profile = "spaghetti and turkey meatballs with garlic bread"
    dietary_restriction = ""
    n_recipes = 5
    # return_top_recipes(calories_per_meal, taste_profile, dietary_restriction, n_recipes)
    file_path = '/Users/dylanethan/Desktop/CS_329_OpenPlate/app/dat/embedded_recipes.csv'

    start = time.time()
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            keywords = []
            for entry in row:
                word = entry.split(",")[0].strip("()\'")
                keywords.append(word)
            RECIPE_KEYWORDS.append(keywords)
    end = time.time()
    print(f'Time to make RECIPE_KEYWORDS: {round(end - start, 3)} seconds')
    top_n_recipes = return_top_recipes(calories_per_meal, taste_profile, dietary_restriction, n_recipes)
    # print(top_n_recipes)

# This block checks if the script is being run directly, not imported as a module
if __name__ == "__main__":
    main()
