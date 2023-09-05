from flask import Flask, render_template, request
import openai
import os
from dotenv import load_dotenv

# Initialize environment variables
load_dotenv()

app = Flask(__name__)

# Securely fetch the API key using the dotenv library
openai.api_key = os.getenv('OPENAI_API_KEY')


@app.route('/')
def index():
    # Display the main ingredient input page
    return render_template('index.html')


@app.route('/generate_recipe', methods=['POST'])
def generate_recipe():
    # Extract the three ingredients from the user's input
    ingredients = request.form.getlist('ingredient')

    if len(ingredients) != 3:
        return "Kindly provide exactly 3 ingredients."

    # Craft a conversational prompt for ChatGPT, specifying our needs
    prompt = f"Craft a recipe in HTML using \
        {', '.join(ingredients)}. \
        Ensure the recipe ingredients appear at the top, \
        followed by the step-by-step instructions."
    messages = [{'role': 'user', 'content': prompt}]

    # Engage ChatGPT to receive the desired recipe
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.8,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.6,
    )

    # Extract the recipe from ChatGPT's response
    recipe = response["choices"][0]["message"]["content"]

    # Showcase the recipe on a new page
    return render_template('recipe.html', recipe=recipe)


if __name__ == '__main__':
    app.run(debug=True)
