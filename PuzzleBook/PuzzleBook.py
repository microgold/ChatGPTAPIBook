from io import BytesIO
import os
import random
import string
import time
import tkinter as tk
from tkinter import ttk
from dotenv import load_dotenv
import openai
import requests
from PIL import Image, ImageTk, ImageDraw, ImageFont
from PuzzleBoardCreator import PuzzleBoardCreator

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Image as ReportLabImage, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from tkinter import messagebox

pil_image_path = "c:\\temp\\temp__puzzlebook_image.png"

puzzle_board_creator = PuzzleBoardCreator()

generated_image = None

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
openai.api_key = key


def set_wait_cursor():
    submit_btn.config(cursor="watch")
    app.update_idletasks()  # Force an immediate update of the window
    time.sleep(2)  # Simulate some long operation


def set_normal_cursor():
    submit_btn.config(cursor="")


def create_pdf(dialog_text):
    if not dialog_text:
        messagebox.showerror("Error", "Please generate the dialog first!")
        return

    # 3. Create a PDF with both the extracted image and some text
    doc = SimpleDocTemplate("output.pdf", pagesize=letter)

    # Create the contents list for the PDF
    contents = []

    # Add the extracted image
    # Adjust width and height as needed
    img = ReportLabImage(pil_image_path, width=2.5*inch, height=2.5*inch)
    contents.append(img)

    # Add some text
    dialog_text = '<br/>' + dialog_text
    dialog_text = dialog_text.replace('\n', '<br/><br/>')
    styles = getSampleStyleSheet()
    paragraph = Paragraph(dialog_text, styles['Normal'])
    contents.append(paragraph)

    # Build the PDF
    doc.build(contents)

    # message box saying we finished generating the PDF
    messagebox.showinfo("PDF Created", "PDF created successfully!")


def generate_image(theme):
    response = openai.Image.create(
        model="image-alpha-001",
        prompt=f"cartoon image of {theme}",
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

    # Save the image as a PNG
    image.save(pil_image_path, "PNG")

    photo = ImageTk.PhotoImage(image)

    update_label_with_new_image(image_holder, photo)
    return image


def display_image_from_path(image_holder, path):
    # Fetch the image from the file

    # open image from path 'c:\\temp\\alphabet_grid.png'
    image = Image.open(path)

    photo = ImageTk.PhotoImage(image)

    update_label_with_new_image(image_holder, photo)
    return image


def create_grid_from_letters(letters):
    # Set image size, background color, and font size
    img_size = (650, 650)
    background_color = (255, 255, 255)  # white
    font_size = 30

    # Create a new image with white background
    img = Image.new('RGB', img_size, background_color)
    d = ImageDraw.Draw(img)

    # Load a truetype or OpenType font file, and set the font size
    try:
        fnt = ImageFont.truetype(
            'C:\\Windows\\Fonts\\Cour.ttf', font_size)
    except IOError:
        print('Font not found, using default font.')
        fnt = ImageFont.load_default()

    # Generate the 13 by 13 grid of letters

    for i in range(13):
        for j in range(13):
            letter = letters[i][j]  # Cycle through the alphabet
            # Adjust position for each letter
            position = (j * (font_size + 10) + 75, i * (font_size + 10) + 75)
            # Draw letter with black color
            d.text(position, letter, font=fnt, fill=(0, 0, 0))

    # Save the image
    img.save('c:\\temp\\alphabet_grid.png')


def clean_words(words):
    # choose only words that are 10 characters or less when punctuation is stripped
    # and spaces removed
    clean_words = []
    for word in words:
        word = word.upper().replace(" ", "")
        # remove any punctuation
        word = word.translate(str.maketrans('', '', string.punctuation))
        if (len(word) <= 10):
            clean_words.append(word)

    # narrow down words to only a list of 10
    if len(clean_words) > 10:
        clean_words = random.sample(clean_words, 10)

    # sort the words by size with largest first
    clean_words.sort(key=len, reverse=True)
    return clean_words


def submit():
    set_wait_cursor()
    theme = combo1.get()

    prompt = f"Create a comma delimited list of 20 words having to do with the theme {theme}. None of the words in the list should repeat\n"
    messages = [{'role': 'user', 'content': prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.8,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.6,
    )

    print(prompt)

    chatGPTAnswer = response["choices"][0]["message"]["content"]
    print(chatGPTAnswer)
    words = chatGPTAnswer.split(',')
    words = clean_words(words)  # pick out a list of 10 viable words
    print(words)
    # create word search puzzle array from words
    (board, words_to_remove) = puzzle_board_creator.create_word_search(words)
    # remove words that could not be placed
    words = [word for word in words if word not in words_to_remove]
    # show the board on the console
    puzzle_board_creator.display_board(board)
    label_puzzle_words.config(text=', '.join(words))
    # make result_text scrollable

    result_text.config(state="normal")
    result_text.delete(1.0, tk.END)  # Clear any previous results
    result_text.insert(tk.END, chatGPTAnswer)
    result_text.config(state="disabled")

    image_url = generate_image(theme)
    create_grid_from_letters(board)
    display_image_from_url(image_holder, image_url)
    display_image_from_path(puzzle_holder, 'c:\\temp\\alphabet_grid.png')
    puzzle_holder.config(width=600, height=600)
    set_normal_cursor()


app = tk.Tk()
app.title("Word Puzzle Book")


# Label and ComboBox for the first animal
label1 = ttk.Label(app, text="Select a Word Puzzle Theme:")
label1.grid(column=0, row=0, padx=10, pady=5)
combo1 = ttk.Combobox(
    app, values=["Holidays", "Science", "Travel", "AI", "Cars", "Food", "Entertainment", "Sports", "Space", "Work", "School", "Animals", "Nature", "Art", "Music", "Movies", "Books", "History", "Math", "Geography", "Weather", "Fashion", "Health", "Family", "Money", "Politics", "Religion", "Technology", "Games", "Business", "Crime", "Law", "Medicine", "Psychology", "Language", "Culture", "Relationships", "Social Media", "News", "Shopping", "Transportation", "Architecture", "Design", "Gardening", "Hobbies", "Humor", "Literature", "Philosophy", "Photography", "Writing", "Other"])
combo1.grid(column=1, row=0, padx=10, pady=5)
combo1.set("Holidays")


# Button to submit the details
submit_btn = ttk.Button(app, text="Submit", command=submit)
submit_btn.grid(column=1, row=3, padx=10, pady=20)

# Button to submit the details
create_pdf_btn = ttk.Button(
    app, text="Create Pdf", command=lambda: create_pdf(result_text.get(1.0, tk.END)))
create_pdf_btn.grid(column=2, row=3, padx=10, pady=20)

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

puzzle_holder = tk.Label(app)
puzzle_holder.grid(column=5, row=0, rowspan=6,  padx=2,
                   pady=2)

label_key_title = ttk.Label(app, text="Puzzle Words")
label_key_title.grid(column=5, row=6, padx=10, pady=5)

label_puzzle_words = ttk.Label(app, text="")
label_puzzle_words.grid(column=5, row=7, padx=10, pady=10)


scrollbar.config(command=result_text.yview)


# Link the scrollbar to the text widget (so the scrollbar knows how to scroll the text widget)


app.mainloop()
