from flask import Flask, render_template, request
import openai
import os
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

app = Flask(__name__)
# Fetch the API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate_recipe', methods=['POST'])
def generate_recipe():
    ingredients = request.form.getlist('ingredient')

    if len(ingredients) != 3:
        return "You must provide exactly 3 ingredients."

    prompt = f"Create a recipe in html using these ingredients: {', '.join(ingredients)}. \
        Ensure the ingredients of the recipe appear on the top, \
        and the instructions appear on the bottom."
    # prompt = 'Hi There'
    messages = [{'role': 'user', 'content': prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.8,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.6,
    )

    recipe = response["choices"][0]["message"]["content"]

    # render a new page containing the recipe
    return render_template('recipe.html', recipe=recipe)


if __name__ == '__main__':
    app.run(debug=True)
