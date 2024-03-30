#pip install openai
import openai
import getpass
import re
from openai import OpenAI

# Prompt the user for the API key
api_key = getpass.getpass("Enter your OpenAI API key: ")
# Assign the API key to the OpenAI client
openai.api_key = api_key

# Create and customize agent
client = OpenAI(
    api_key=api_key,
)

# Example usage: generate("example prompt")
def generate(prompt):
    try:
        openai.api_key = api_key
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an intelligent meal planner assistant. Your primary task is to gather information about the user (including weight, height, goal) and to understand user queries related to meal planning and provide helpful responses. This includes recognizing the user's intent (e.g., seeking a recipe, needing a shopping list, asking for nutritional advice) and identifying specific details (slots) such as dietary preferences, meal types, preferred cuisines, and ingredients. You should also consider users' dietary restrictions and nutritional goals when providing recommendations."
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


class MealPlannerAssistant:
    def __init__(self):
        self.user_profile = {
            "height": None,  # in cm
            "weight": None,  # in kg
            "gender": None,
            "dietary_restriction": None,  # Categorized by predefined list
            "goal": None  # e.g., weight loss, maintenance, muscle gain
        }
        self.questions = {
            "height": "Could you tell me your height? (e.g., 170cm or 5'7\")",
            "weight": "What's your weight? (e.g., 70kg or 155lbs)",
            "gender": "What's your gender?",
            "dietary_restriction": "Do you have any dietary restrictions? (e.g., vegan, keto)",
            "goal": "What's your goal? (e.g., weight loss, maintenance, muscle gain)"
        }

    def ask_questions(self):
        for key, question in self.questions.items():
            valid_response = False
            while not valid_response:
                if self.user_profile[key] is None:
                    print(question)
                    response = input().strip()
                    valid_response, processed_response = self.validate_and_process_response(key, response)
                    if valid_response:
                        self.user_profile[key] = processed_response
                    else:
                        print(f"Invalid response for {key}. Please try again.")

    def validate_and_process_response(self, topic, response):
        if topic == "dietary_restriction":
            prompt = f"From this response '{response}', can we categorize the user's dietary restriction into one of the following: None, Keto, Vegan, Vegetarian, Gluten-Free, Paleo, Halal, Other? Please select and list out the closest option."
        if topic in ["height", "weight"]:
            prompt = f"From this response '{response}', can we tell what the user's {topic} is and the unit? Please answer Yes or No, and if Yes, provide the user's {topic}."
        else:
            prompt = f"From this response '{response}', can we tell what the user's {topic} is? Please answer Yes or No, and if Yes, provide the user's {topic}."

        ai_response = generate(prompt) 
        print(ai_response) 

        if "no" in ai_response.lower() and topic != "dietary_restriction":
            return False, "Invalid response"
        else:
            processed_response = self.process_ai_response(topic, ai_response)
            return True, processed_response

    def process_ai_response(self, topic, response):
        if topic in ["height", "weight"]:
            prompt = f"Convert the user's {topic} '{response}' into standard units (write cm for height, kg for weight)."
        elif topic == "gender":
            prompt = f"Based on this response '{response}', how can we best classify the user's gender? Consider traditional categories like 'male' or 'female', but also note if the response suggests a non-binary or prefer-not-to-say option."
        elif topic == "goal":
            prompt = f"Given this response '{response}', what is the user's fitness or health goal? Classify it into one of the following categories and list it: weight loss, maintenance, muscle gain, or specify 'other' if none of these categories accurately capture the user's goal."
        else:
            return self.finalize_response(topic, response)
        ai_interpreted_response = generate(prompt)

        # Apply NLP techniques for final standardization
        return self.finalize_response(topic, ai_interpreted_response)
    
    def finalize_response(self, topic, response):
        #return self._interpret_goal(response)
        if topic == "height":
            return self._convert_height_to_cm(response)
        elif topic == "weight":
            return self._convert_weight_to_kg(response)
        elif topic == "gender":
            return self._interpret_gender(response)
        elif topic == "goal":
            return self._interpret_goal(response)
        else:
          return response

    def _interpret_gender(self, response):
        return next((value for word in response.lower().split() for key, value in {
            "female": "Female",
            "male": "Male",
            "non-binary": "Non-binary",
            "prefer not to say": "Prefer not to specify",
            # Add more mappings as necessary
        }.items() if key in word), "Prefer not to specify")


    def _interpret_goal(self, response):
        return next((value for word in response.split() for key, value in {
            "weight loss": "Weight Loss",
            "lose weight": "Weight Loss",  
            "maintenance": "Maintenance",
            "muscle gain": "Muscle Gain",
        }.items() if key in response.lower()), "Other")


    def _convert_height_to_cm(self, response):
        # Handling centimeters directly or inches, e.g., 170cm or 67 inches
        cm_inches_pattern = re.compile(r"(\d+)\s*(cm|inch(es)?)?", re.IGNORECASE)
        match = cm_inches_pattern.search(response)
        if match:
            value, unit = int(match.group(1)), match.group(2)
            if not unit or "cm" in unit.lower():
                return f"{value}cm"
            elif "inch" in unit.lower():
                return f"{value * 2.54:.0f}cm"

        return "Invalid height format"

    def _convert_weight_to_kg(self, response):
        # Handling pounds and kilograms
        lbs_kg_pattern = re.compile(r"(\d+)\s*(kg|lb(s)?)?", re.IGNORECASE)
        match = lbs_kg_pattern.search(response)
        if match:
            value, unit = int(match.group(1)), match.group(2)
            if not unit or "kg" in unit.lower():
                return f"{value}kg"
            elif "lb" in unit.lower():
                return f"{value / 2.20462:.0f}kg"

        return "Invalid weight format"


    def is_complete(self):
        return all(value is not None for value in self.user_profile.values())

    def run(self):
        print("Welcome to the Meal Planner Assistant. I'll ask you a few questions to understand your preferences and needs.")
        while not self.is_complete():
            self.ask_questions()
        print("Thank you for providing the information. Here's your profile:")
        for key, value in self.user_profile.items():
            print(f"{key.replace('_', ' ').title()}: {value}")

if __name__ == "__main__":
    assistant = MealPlannerAssistant()
    assistant.run()
