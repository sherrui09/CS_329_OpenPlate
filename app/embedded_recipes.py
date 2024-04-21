from keybert import KeyBERT # type: ignore
import pandas as pd # type: ignore
from pandas import DataFrame # type: ignore
import time
import csv

def select_recipes(recipes: DataFrame, n: int, random_selection: bool) -> DataFrame:
  if n > len(recipes): raise ValueError("Choose smaller n")

  if random_selection:
    selected_recipes = recipes.sample(n=n, random_state=42)  # Use a fixed random state for reproducibility
  else:
    selected_recipes = recipes.head(n)
  
  return selected_recipes

def make_recipe_keywords(sample_recipes: DataFrame) -> list:
  start = time.time()
  keybert_model = KeyBERT() # dont repeat instances
  recipe_keywords = []

  for _, recipe in SAMPLE_RECIPES.iterrows():
    summary           = recipe['summary']
    title             = recipe['name']
    title_and_summary = title + " " + summary
    recipe_keywords.append(keybert_model.extract_keywords(title_and_summary))
  
  end = time.time()
  print(f'Time to Embed {len(sample_recipes)} Recipes: {(end - start) / 60} minutes')

  return recipe_keywords

def convert_list_to_csv(data_list: list, file_path: str):
  with open(file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    # writer.writerow([str(i) for i in range(len(data_list[0]))])
    writer.writerows(data_list)
  

recipe_count = 35500
random_selection = False

ALL_RECIPES = pd.read_csv('C:/Users/cheem/Documents/GitHub/CS_329_OpenPlate/app/dat/all_recipes_scraped.csv') # make path name your own.
SAMPLE_RECIPES = select_recipes(ALL_RECIPES, recipe_count, random_selection)

def main():
  recipe_keywords = make_recipe_keywords(SAMPLE_RECIPES) # pre-calculate the keywords to make KeyBERT methods faster. GLOBAL
  convert_list_to_csv(recipe_keywords, 'embedded_recipes.csv')

  # df_recipe_keywords = pd.DataFrame(recipe_keywords)
  # df_recipe_keywords.to_csv('embedded_recipes.csv', index=False)

if __name__ == "__main__":
  main()



