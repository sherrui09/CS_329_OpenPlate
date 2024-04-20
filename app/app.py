from flask import Flask, request, jsonify, render_template, session
import openai
from openai import OpenAI
import re

app = Flask(__name__)

api_key = ''
client = OpenAI(
    api_key=api_key,
)


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
        openai.api_key = api_key
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
        openai.api_key = api_key
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
        openai.api_key = api_key
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful calorie assistant to help users calculate their daily intake based on their profile. Please give an estimation if there is not enough information."
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

# Calculate daily maintenance calories

def generate_recipe(prompt):
    try:
        openai.api_key = api_key
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

class HealthProfileAssistant:
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
        self.question_order = [
            "height", "weight", "gender", "dietary_restriction", "goal"
        ]
        self.question_keys = list(self.user_profile.keys())  # Maintain order of questions
        self.current_question_index = 0  # Track which question to ask next

    def is_complete(self):
        return all(value is not None for value in self.user_profile.values())
    
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
                prompt = f"From this response '{response}', can we tell what the user's {topic} is? Please answer Yes or No, and if Yes, provide the user's {topic}."

            ai_response = generate(prompt)

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

    

def specify_updates(updates, field_name):
        prompt = f"The user wants to make the following changes to their health profile '{updates}', write a conversational question asking them to give specifics about their changes to their {field_name}. Only reply with the question and only ask about their {field_name}."
        response = generate_update(prompt)
        return response


def summarize_updates(specified_update, user_input, field_name):
        prompt = f"The user responded {user_input} to the question {specified_update} about their new {field_name}, please summarize what changes there were to their {field_name}"
        return generate_update(prompt)

class UpdateAssistant:
    def __init__(self, user_profile):
            self.user_profile = user_profile
            self.field_names = list(self.user_profile.keys())

    def check_for_update_intent(self, user_input):
          prompt = (
              f"Based on the user's response {user_input} to if they'd like to update their profile or build a recipe. Classify it into: 1. Update profile, 2. Generate Recipe 3. Other. Please return just the number associated, return 1 if they want to update profile and generate recipe."
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
        return generate_calorie(prompt)

class RecipeAssistant:
    def __init__(self, user_profile, recipe_description):
        self.client = client
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

class GeneralAssistant:
    def __init__(self, user_profile):
        self.client = client
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


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["GET"])
def start():
    global assistant
    assistant = HealthProfileAssistant()
    message = "Welcome to the Meal Planner Assistant. I'll ask you a few questions to understand your preferences and needs."
    return jsonify(message=message, question=assistant.questions['height'])


@app.route("/message", methods=["POST"])
def message():
    user_input = request.json['message']
    current_key = assistant.question_keys[assistant.current_question_index]
    if assistant.user_profile[current_key] is None:
        valid_response, processed_response = assistant.validate_and_process_response(current_key, user_input)
        if valid_response:
            assistant.user_profile[current_key] = processed_response
            assistant.current_question_index += 1  # Move to the next question
            if assistant.current_question_index >= len(assistant.question_keys):
                summary = "Thank you for providing your information. Here's your profile:\n" + str(assistant.user_profile)
                return jsonify(message=summary)
            else:
                next_question = assistant.questions[assistant.question_keys[assistant.current_question_index]]
                return jsonify(message=next_question)
        else:
            return jsonify(message=f"Invalid response for {current_key}. Please try again.\n{assistant.questions[current_key]}")
    return jsonify(message="All questions answered. Thank you!")



if __name__ == "__main__":
    app.run(debug=True)