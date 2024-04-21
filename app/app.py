from flask import Flask, request, jsonify, render_template, session
import openai
from openai import OpenAI
import re
from pandas import DataFrame # type: ignore
from keybert import KeyBERT # type: ignore
import time
from fuzzywuzzy import fuzz # type: ignore
import csv
from embedded_recipes import SAMPLE_RECIPES

app = Flask(__name__)
app.secret_key = 'your_very_secret_key'



dietary_restrictions = {
    1: "None",
    2: "Keto",
    3: "Vegan",
    4: "Vegetarian",
    5: "Gluten-Free",
    6: "Lactose-Intolerant",
    7: "Paleo",
    8: "Halal",
    9: "Other"
}

goals = {
    1: "Weight Loss",
    2: "Weight Gain",
    3: "Muscle Gain",
    4: "Maintenance",
    5: "Other"
}


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def _convert_weight_to_kg(response):
        lbs_kg_pattern = re.compile(r"(\d+)\s*(kg|lb(s)?)?", re.IGNORECASE)
        match = lbs_kg_pattern.search(response)
        if match:
            value, unit = int(match.group(1)), match.group(2)
            if not unit or "kg" in unit.lower():
                return f"{value}kg"
            elif "lb" in unit.lower():
                return f"{value / 2.20462:.0f}kg"

        return response

def _convert_height_to_cm(response):
        cm_inches_pattern = re.compile(r"(\d+)\s*(cm|inch(es)?)?", re.IGNORECASE)
        match = cm_inches_pattern.search(response)
        if match:
            value, unit = int(match.group(1)), match.group(2)
            if not unit or "cm" in unit.lower():
                return f"{value}cm"
            elif "inch" in unit.lower():
                return f"{value * 2.54:.0f}cm"

        return response

def generate(prompt):
    try:
        client = get_openai_client()
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an intelligent health profile assistant. Your primary task is to gather information about the user (including weight, height, goal)"
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return str(e)


def generate_update(prompt):
    try:
        client = get_openai_client()
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI designed to assist with updating a user's health profile based on their input regarding changes. Identify and categorize changes mentioned by the user into fields such as weight, height, dietary restrictions, gender, and goal.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return str(e)

# Specializing Agents
def generate_calorie(prompt):
    try:
        client = get_openai_client()
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful calorie assistant to help users calculate an achievable daily caloric amount based on their profile and goals. Please give an estimation if there is not enough information."
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return str(e)

# Calculate daily maintanennce calories

def generate_recipe(prompt):
    try:
        client = get_openai_client()
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an intelligent meal planner. Your primary goal is to recommend recipes (including ingredients, steps, and nutrition information) based on the user's profile."
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return str(e)

class HealthProfileAssistant(metaclass=Singleton):
    def __init__(self):
        self.user_profile = {
            "height": None,
            "weight": None,
            "gender": None,
            "dietary_restriction": None,
            "goal": None
        }
        self.questions = {
            "height": "Could you tell me your height? (e.g., 170cm or 5'7\")",
            "weight": "What's your weight? (e.g., 70kg or 155lbs)",
            "gender": "What's your gender?",
            "dietary_restriction": "Do you have any dietary restrictions? (e.g., vegan, keto)",
            "goal": "What's your goal? (e.g., weight loss, maintenance, muscle gain)"
        }

    def validate_and_process_response(self, topic, response):
        if topic == "dietary_restriction":
            prompt = f"""
            Given the user's response '{response}' regarding their dietary restrictions, categorize their diet using the embedded dictionary:
            {dietary_restrictions}
            Please only return the number(s) associated with the closest dietary restriction category. If other, please specify.
            """
            response = generate(prompt)
            numbers = re.findall(r'\d+', response)
            restriction_numbers = [int(num) for num in numbers]
            if len(restriction_numbers) == 0:
              return True, response
            else:
              restriction_names = [dietary_restrictions[number] for number in restriction_numbers if number in dietary_restrictions]
              unique_restriction_names = list(set(restriction_names))
              return True, ", ".join(unique_restriction_names)
        else:
            if topic in ["height", "weight"]:
                prompt = f"From this response '{response}' for {topic}, can we tell what the user's {topic} is and the unit? Please answer Yes or No, and if Yes, provide the user's {topic}. Say No for invalid/illogical answers or missing units."
            else:
                prompt = f"From this response '{response}', can we tell what the user's {topic} is? Please try to categorize and answer Yes or No, and if Yes, provide the user's {topic}."

            ai_response = generate(prompt)
            print(ai_response)

            if "no" in ai_response.lower().split() and topic != "dietary_restriction":
                prompt = (
                    f"The user has provided a response '{response}' to the topic '{topic}'. "
                    "It appears that the response may not have the detail or specificity required. "
                    "Please help the user with inputting a valid response and give any specific guidance on their invalid input"
                )
                return False, response
            else:
                processed_response = self.process_ai_response(topic, ai_response)
                return True, processed_response

    def process_ai_response(self, topic, response):
        if topic in ["height", "weight"]:
            prompt = f"Convert the user's {topic} '{response}' into standard units (write cm for height, kg for weight)."
            calculations = generate(prompt)
            prompt = f"Given the user's {topic} is {calculations}, please only return their final {topic} with standard units(write cm for height, kg for weight)."
        elif topic == "gender":
            prompt = f"Based on this response '{response}', how can we best classify the user's gender? Consider traditional categories like 'male' or 'female', or say other."
        elif topic == "goal":
            prompt = f"Given this response '{response}', what is the user's fitness or health goal? Classify it into one of the following categories {goals}. Simply return the number associated with the closest goal. Or summarize their goal if 'Other'"
            response = generate(prompt)
            numbers = re.findall(r'\d+', response)
            goal_numbers = [int(num) for num in numbers]
            unique_goal_numbers = list(set(goal_numbers))
            goal_names = [goals[number] for number in unique_goal_numbers if number in goals]
            return ", ".join(goal_names)
        else:
            return self.finalize_response(topic, response)
        ai_interpreted_response = generate(prompt)
        return self.finalize_response(topic, ai_interpreted_response)

    def finalize_response(self, topic, response):
        if topic == "height":
            return _convert_height_to_cm(response)
        elif topic == "weight":
            return _convert_weight_to_kg(response)
        elif topic == "gender":
            return self._interpret_gender(response)
        else:
          return response

    def _interpret_gender(self, response):
        return next((value for word in response.lower().split() for key, value in {
            "female": "Female",
            "male": "Male",
        }.items() if key in word), "Prefer not to specify")


    def is_complete(self):
        return all(value is not None for value in self.user_profile.values())

def specify_updates(updates, field_name):
        prompt = f"The user wants to make the following changes to their health profile '{updates}', write a conversational question asking them to give specifics about their changes to their {field_name}. Only reply with the question and only ask about their {field_name}."
        response = generate_update(prompt)
        return response


def summarize_updates(specified_update, user_input, field_name):
        prompt = f"The user responded {user_input} to the question {specified_update} about their new {field_name}, please summarize what changes there were to their {field_name}"
        return generate_update(prompt)

class UpdateAssistant(metaclass=Singleton):
    def __init__(self, user_profile):
            self.user_profile = user_profile
            self.field_names = list(self.user_profile.keys())

    def check_for_update_intent(self, user_input):
          prompt = (
              f"The user responded to if they'd like to update their profile or build a recipe with the following: {user_input}. Classify it into: 1. Update profile, 2. Generate Recipe 3. Other. Please return just the number associated, return 1 if they want to update profile and generate recipe."
          )
          response = generate(prompt)
          int_intent = lambda s: int(re.search(r'\d', s).group(0)) if re.search(r'\d', s) else None
          return int_intent(response)

    def identify_fields_to_update(self, updates):
        """Generate a prompt to identify which profile fields are mentioned in the updates."""
        fields_prompt = '\n'.join([f"{idx + 1}. {name.capitalize()}" for idx, name in enumerate(self.field_names)])
        prompt = f"""Given the user profile fields:
                {fields_prompt}
                And the user's updates: "{updates}", identify which profile fields are mentioned in the updates. Only list the fields by their numbers. Return 0 if no change needed."""
        response = generate_update(prompt)
        return response

    def extract_fields_to_update(self, response):
    # Use regex to find all numbers in the response
        return [int(num) for num in re.findall(r'\d+', response)]

    def process_updates(self, updates, field_name):
        if field_name in ["height", "weight"]:
            prompt = (
                f"Given the user's update that they '{updates}' which implies a change in their {field_name}, "
                f"and their current {field_name} is {self.user_profile[field_name]}, calculate the new {field_name}. "
                f"Convert all measurements to the unit of the current {field_name} before calculating. "
            )
            calculations = generate_update(prompt)
            prompt = f"Given the following calculations for {field_name}: {calculations}, what is the user's final {field_name}? Return only return the final {field_name} rounded to the nearest whole number and with the unit"
            response = generate_update(prompt)
            response = _convert_weight_to_kg(response) if field_name == "weight" else _convert_height_to_cm(response)
        elif field_name == "dietary_restriction":
            prompt = (
                f"Analyze the user's response '{updates}' and update the dietary restriction accordingly. "
                f"The current dietary restriction is {self.user_profile[field_name]}. Possible categories include: "
                "None, Keto, Vegan, Vegetarian, Gluten-Free, Lactose-Intolerant, Paleo, Halal. Or specify if other"
                "Please only return the updated category."
            )
            response = generate_update(prompt)
            response = _convert_weight_to_kg(response)
        elif field_name == "goal":
            prompt = (
                f"Analyze the user's response '{updates}' and update the goal accordingly. "
                f"The current goal is {self.user_profile[field_name]}. Possible goals include: "
                "Weight maintenance, Muscle Gain, Weight loss. "
                f"Please only return the updated goal. Return the original {field_name} if no updates can be made."
            )
            response = generate_update(prompt)
        else:
            prompt = f"Analyze the user's response '{updates}. update their {field_name}. The current {field_name} is {self.user_profile[field_name]}. Please only return the updated value. Return the original {field_name} if no updates can be made."
            response = generate_update(prompt)
        return response

    def extract_cal(self, s):
        numbers = re.findall(r'\d+', s)
        if numbers:
            number = int(numbers[0])
            if number < 1200:
                return 1200
            elif number > 3000:
                return 3000
            else:
                return number
        else:
            return 2000


    def calculate_calories(self):
        height = self.user_profile["height"]
        weight = self.user_profile["weight"]
        gender = self.user_profile["gender"]
        goal = self.user_profile["goal"]
        dietary_restriction = self.user_profile["dietary_restriction"]

        prompt = (
            f"Calculate the recommended daily goal calorie intake for the user with the following profile: "
            f"Height: {height}, Weight: {weight}, Gender: {gender}, "
            f"Dietary Restriction: {dietary_restriction}, Goal: {goal}. "
        )
        response = generate_calorie(prompt)
        prompt = (
            f"Based on the following analysis{response}, list the user's recommended daily intake as a whole number, do not include any units or extra text."
        )
        string_cal = generate_calorie(prompt)

        return self.extract_cal(string_cal)


class RecipeAssistant(metaclass=Singleton):
    def __init__(self, user_profile, recipe_description):
        self.client = get_openai_client()
        self.messages = [
            {
                "role": "system",
                "content": f"You are a helpful meal assistant and you will consider the users' profile {user_profile} when providing recommendations about the current recipe {recipe_description}. You will help with user queries related to meal planning and provide helpful responses."
            }
        ]

    def generate(self, user_prompt):
        self.messages.append({"role": "user", "content": user_prompt})

        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=self.messages
        )

        response_content = completion.choices[0].message.content

        self.messages.append({"role": "assistant", "content": response_content})

        return response_content

class GeneralAssistant(metaclass=Singleton):
    def __init__(self, user_profile):
        self.client = get_openai_client()
        self.messages = [
            {
                "role": "system",
                "content": f"You are a helpful meal assistant and you will consider the users' profile {user_profile} when providing recommendations and responding to user inquiries."
            }
        ]

    def generate(self, user_prompt):
        self.messages.append({"role": "user", "content": user_prompt})

        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=self.messages
        )

        response_content = completion.choices[0].message.content

        self.messages.append({"role": "assistant", "content": response_content})

        return response_content
        
def validate_recipe(recipe, dietary_restriction, taste):
    if check_recipe_fields:
        name = recipe[0]["name"]
        ingredients = recipe[0]["ingredients"]
        directions = recipe[0]["directions"]
        url = recipe[0]["url"]
        prep = recipe[0]["prep"]
        cook = recipe[0]["cook"]
        servings = recipe[0]["servings"]
        calories = recipe[0]["calories"]
        recipe_description = f"Recipe name: {name}, Ingredients: {ingredients}, Directions: {directions}, Calories: {calories}, Prep time: {prep}, Cook time: {cook}. URL: {url}"
        prompt = prompt = f"Given the user's dietary preference of {dietary_restriction} with a taste profile for {taste}, does the following recipe description fit their dietary preference and somewhat match their taste profile? Here's the recipe: {recipe_description}. Return 1 for Yes, 2 for No."
        recipe_check = generate(prompt)
        int_recipe_check = lambda s: int(re.search(r'\d', s).group(0)) if re.search(r'\d', s) else None
        print(int_recipe_check)
        print(int_recipe_check(recipe_check) == 1)
        return int_recipe_check(recipe_check) == 1, recipe_description
    return False, recipe


def return_top_recipes(calories_per_meal: int, taste_profile: str, dietary_restriction: str, n_recipes: int, RECIPE_KEYWORDS):

    caloric_multiplier = 0.7 # alter value... (should be < 1)
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


def check_recipe_fields(recipe):
    # Check if recipe list is empty or not
    if not recipe:
        return False

    # Explicitly check each key
    required_keys = ["name", "ingredients", "directions", "url", "prep", "cook", "servings", "calories"]
    for key in required_keys:
        if key not in recipe[0]:
            return False

    return True

def get_recipe(calories_per_meal, taste_profile):
    RECIPE_KEYWORDS = []
    n_recipes = 1
    dietary_restriction = ''
    # return_top_recipes(calories_per_meal, taste_profile, dietary_restriction, n_recipes)
    file_path = 'C:/Users/sherry/open_plate/app/embedded_recipes.csv'

    with open(file_path, 'r', newline='', encoding='latin1') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            keywords = []
            for entry in row:
                word = entry.split(",")[0].strip("()\'")
                keywords.append(word)
            RECIPE_KEYWORDS.append(keywords)

    return return_top_recipes(calories_per_meal, taste_profile, dietary_restriction, n_recipes, RECIPE_KEYWORDS)

def jsonify_chat(message):
    """Generate a JSON response for chat messages."""
    return jsonify({
        "type": "chat",
        "message": message
    })

def jsonify_popup(chat_message, popup_message):
    """Generate a JSON response for both popup notifications and chat messages."""
    return jsonify({
        "type": "both",
        "chat_message": chat_message,
        "popup_message": popup_message
    })
assistant = HealthProfileAssistant()
update_agent = None
general_assistant = None
int_intent = None

def is_api_key_valid(api_key):
    try:
        client = openai.Client(api_key=api_key)
        #client.Engines.list()  # Attempt to list engines as a validation check
        return True
    except openai.error.AuthenticationError:
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def get_openai_client():
    api_key = session.get('api_key')
    if not api_key:
        raise ValueError("API key is not set.")
    if not is_api_key_valid(api_key):
        raise ValueError("Invalid API key.")
    return openai.Client(api_key=api_key)

@app.route('/set_api_key', methods=['POST'])
def set_api_key():
    data = request.get_json()
    api_key = data.get('apiKey')
    if is_api_key_valid(api_key):
        session['api_key'] = api_key
        session['api_key_submit'] = True
        return jsonify({'message': 'API Key set successfully'}), 200
    return jsonify({'error': 'Invalid or No API Key provided'}), 400


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        session_keys = ['profile_updated', 'update_profile', 'calories_generated', 
                        'recipe_generated', 'ready_for_agent', 'api_key_submit']
        session.update({key: False for key in session_keys})
        session['calories'] = 1600
        welcome_message = "Welcome to the OpenPlate Agent. I'll ask you a few questions to understand your preferences and needs."
        # Start from the first question
        session['current_question_key'] = next(iter(assistant.questions)) if assistant.questions else None
        session['user_profile'] = {key: None for key in assistant.questions}  # Initialize user profile
        return render_template('index.html', bot_response=f"Assistant: {welcome_message}\n{assistant.questions[session['current_question_key']]}\n")

    if request.method == 'POST':
        data = request.get_json()  
        user_input = data['message'].strip()
        
        current_key = session['current_question_key']
        
        if current_key is not None:
            valid_response, processed_response = assistant.validate_and_process_response(current_key, user_input)
            if valid_response:
                session['user_profile'][current_key] = processed_response
                print(session['user_profile'][current_key])
                # Determine the next question
                remaining_keys = [k for k in assistant.questions if session['user_profile'][k] is None]
                print(remaining_keys)
                if remaining_keys:
                    session['current_question_key'] = remaining_keys[0]
                    print(session['current_question_key'])
                    return jsonify_chat(f"{assistant.questions[session['current_question_key']]}")
                else:
                    # All questions answered
                    session['current_question_key'] = None
                    chat_message = f"Your profile has been created!\nLet me know if you'd like to update your profile or jump into generating your recipe!"
                    popup_message = f"Your profile:\n{session['user_profile']}"
                    # TODO
                    return jsonify_popup(chat_message,popup_message )
            else:
                print(assistant.questions[current_key])
                return jsonify_chat(f"Invalid response for {current_key}. Please try again.")
        
        if not session['profile_updated']:
            update_agent = UpdateAssistant(session['user_profile'])
            int_intent = update_agent.check_for_update_intent(user_input) 
            print(int_intent)                 
            if int_intent == 1 and not session['update_profile']:
                session['update_profile'] = True
                return jsonify_chat("What are the changes to your health profile?")
            
            if session['update_profile'] and not session['calories_generated']:
                fields_to_update = update_agent.extract_fields_to_update(update_agent.identify_fields_to_update(user_input))
                for field_index in fields_to_update:
                    if field_index == 0:
                        continue
                    field_name = update_agent.field_names[field_index - 1]
                    prompt = f"From the user's response about their change in health profile '{user_input}', do we have specific information to update their {field_name}? Simply say yes if we do, otherwise just say No"
                    response = generate_update(prompt)
                    if "no" in response.lower():
                        return jsonify_chat(f"Please specify the updates for {field_name}")
                    else:
                        update_agent.user_profile[field_name] = update_agent.process_updates(user_input, field_name)
                session['user_profile'] = update_agent.user_profile
                session.pop('update_profile', None)
                session['profile_updated'] = True
                session["calories"] = update_agent.calculate_calories()
                if session["calories"] < 1200:
                    session["calories"] = 1200
                session['calories_generated'] = True
                chat_message = f"Your profile has been Updated!\nYour recommended daily calories is {session['calories']}.\nLet's find your perfect recipe! Please tell me about what you are looking for in a recipe such as any preferences in taste, cook time, budget, or health considerations. Include any other relevant details. This helps me pick the best recipes for you!"
                # TODO
                popup_message = f"Your updated profile:\n{update_agent.user_profile}"
                return jsonify_popup(chat_message,popup_message)
                
        if not session['calories_generated'] and (int_intent == 1 or int_intent == 2):
            # Calculate calories and get recipe
            session["calories"] = update_agent.calculate_calories()
            print(session["calories"])
            if session["calories"] < 1200: session["calories"] = 1200
            session['calories_generated'] = True
            return jsonify_chat(f"Your recommended daily calories is {session['calories']}.\nLet's find your perfect recipe! Please tell me about what you are looking for in a recipe such as any preferences in taste, cook time, budget, or health considerations. Include any other relevant details. This helps me pick the best recipes for you!")
        # Handle recipe preferences
        if not session['recipe_generated']:
            prompt = f"Given the user's preferences described as: {user_input}, summarize these preferences into a concise statement suitable for NLP processing."
            meal_calories = int(session["calories"] / 3)
            user_preference = generate_recipe(prompt)
            recipe = get_recipe(meal_calories, user_preference)
            dietary_restriction = session['user_profile']["dietary_restriction"]
            valid_recipe, session['recipe_description'] = validate_recipe(recipe, dietary_restriction, user_preference)
            if valid_recipe:
                session['recipe_generated'] = True
                # TODO
                return jsonify_chat(f"{session['recipe_description']}. Let me know if you have any questions!")
            else:
                prompt = f"Given the user profile {session['user_profile']}, and their preference for meals {user_preference}, generate a recipe for them that is around {session['calories']} calories"
                session['recipe_description'] = generate_recipe(prompt)
                session['recipe_generated'] = True
                # TODO
                # jsonify_popup(chat_Message, popup_message)
                return jsonify_chat(f"{session['recipe_description']}.\nLet me know if you have any questions!")

        if session['recipe_generated']:
            recipe_agent = RecipeAssistant(session['user_profile'], session['recipe_description'])
            if user_input.lower() in ['exit', 'quit']:
                return jsonify_chat("Goodbye!")
            response = recipe_agent.generate(user_input)
            return jsonify_chat(response)
        
        if not session['ready_for_agent']:
            session['ready_for_agent'] = True
            return jsonify_chat(f"Let me know if you have any questions!")
        # Handle general questions
        if not session['recipe_generated']:
            general_assistant = GeneralAssistant(session['user_profile'])
            if user_input.lower() in ['exit', 'quit']:
                return jsonify_chat("Goodbye!")
            response = general_assistant.generate(user_input)
            return jsonify_chat(response)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
