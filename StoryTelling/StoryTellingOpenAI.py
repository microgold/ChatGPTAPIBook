from io import BytesIO
import os
import tkinter as tk
from tkinter import ttk
from flask.cli import load_dotenv
import openai
import requests
from PIL import Image, ImageTk

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
openai.api_key = key


def generateImage(animal1, animal2, scenario):
    response = openai.Image.create(
        model="image-alpha-001",
        prompt=f"cartoon image of a {animal1} and a {animal2} discussing {scenario}",
        n=1,  # Number of images to generate
        size="256x256",  # Size of the generated image
        response_format="url"  # Format in which the image will be received
    )

    image_url = response.data[0]["url"]
    print(image_url)
    return image_url


def update_label_with_new_image(label, photo):
    # Assuming `label` is a global variable
    # photo = get_photo_from_url(new_image_url)
    label.config(image=photo)
    label.image = photo  # Keep a reference to avoid garbage collection


def display_image_from_url(image_holder, url):
    # Fetch the image from the URL
    response = requests.get(url)
    image_data = BytesIO(response.content)

    # Open and display the image using PIL and tkinter
    image = Image.open(image_data)
    photo = ImageTk.PhotoImage(image)

    update_label_with_new_image(image_holder, photo)


def submit():
    animal1 = combo1.get()
    animal2 = combo2.get()
    scenario = entry_box.get()

    prompt = f"Create a play between a {animal1} and a {animal2} with 10 lines of dialog with each animal taking turns to speak. Leave a vertical space between lines after each animal speaks. Here is the scenario in which they will engage: {scenario}\n"
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

    chatGPTAnswer = response["choices"][0]["message"]["content"]
    print(chatGPTAnswer)
    # make result_text scrollable

    result_text.config(state="normal")
    result_text.delete(1.0, tk.END)  # Clear any previous results
    result_text.insert(tk.END, chatGPTAnswer)
    result_text.config(state="disabled")

    image_url = generateImage(animal1, animal2, scenario)
    display_image_from_url(image_holder, image_url)


app = tk.Tk()
app.title("Animal Discussion Scenario")


# Label and ComboBox for the first animal
label1 = ttk.Label(app, text="Select Animal 1:")
label1.grid(column=0, row=0, padx=10, pady=5)
combo1 = ttk.Combobox(
    app, values=["Lion", "Elephant", "Giraffe", "Kangaroo", "Panda"])
combo1.grid(column=1, row=0, padx=10, pady=5)
combo1.set("Lion")

# Label and ComboBox for the second animal
label2 = ttk.Label(app, text="Select Animal 2:")
label2.grid(column=0, row=1, padx=10, pady=5)
combo2 = ttk.Combobox(
    app, values=["Lion", "Elephant", "Giraffe", "Kangaroo", "Panda"])
combo2.grid(column=1, row=1, padx=10, pady=5)
combo2.set("Elephant")

# Label and Entry for entering the discussion scenario
label3 = ttk.Label(app, text="Enter Discussion Scenario:")
label3.grid(column=0, row=2, padx=10, pady=5)
entry_box = ttk.Entry(app, width=30)
entry_box.grid(column=1, row=2, padx=10, pady=5)

# Button to submit the details
submit_btn = ttk.Button(app, text="Submit", command=submit)
submit_btn.grid(column=1, row=3, padx=10, pady=20)

# make it scrollable
# Create a Scrollbar widget
scrollbar = tk.Scrollbar(app)
scrollbar.grid(row=4, column=3, sticky='ns')

# Text widget to display results
result_text = tk.Text(app, width=50, height=10,
                      wrap=tk.WORD, yscrollcommand=scrollbar.set)
result_text.grid(column=0, row=4, columnspan=2, padx=10, pady=10)
result_text.config(state="disabled")
# result_text.pack(expand=True, fill=tk.BOTH)

image_holder = tk.Label(app)
image_holder.grid(column=0, row=5, columnspan=4, padx=10, pady=10)


scrollbar.config(command=result_text.yview)


# Link the scrollbar to the text widget (so the scrollbar knows how to scroll the text widget)


app.mainloop()
