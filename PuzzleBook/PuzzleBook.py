from datetime import datetime
import shutil
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image as ReportLabImage, PageBreak, Spacer, Table, TableStyle
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
import json
import inflect

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image as ReportLabImage, PageBreak, Frame, PageTemplate
from reportlab.lib.colors import black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from tkinter import messagebox

p = inflect.engine()


def pluralize(topic):
    plural_topic = p.plural(topic)
    return plural_topic


pil_image_path = "c:\\temp\\temp__puzzlebook_image.png"
puzzle_image_path = 'c:\\temp\\alphabet_grid.png'

puzzle_board_creator = PuzzleBoardCreator()

generated_image = None

left_margin_left_side = .75*inch
left_margin_right_side = 1*inch
left_margin = left_margin_left_side

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
openai.api_key = key


def set_wait_cursor():
    submit_btn.config(cursor="watch")
    app.update_idletasks()  # Force an immediate update of the window
    time.sleep(2)  # Simulate some long operation


def set_normal_cursor():
    submit_btn.config(cursor="")


def header(canvas, doc, content):
    canvas.saveState()
    w, h = content.wrap(doc.width, doc.topMargin)
    content.drawOn(canvas, doc.leftMargin, doc.height +
                   doc.bottomMargin + doc.topMargin - h)
    canvas.restoreState()


def footer(canvas, doc, content):
    canvas.saveState()
    w, h = content.wrap(doc.width, doc.bottomMargin)
    content.drawOn(canvas, doc.leftMargin, h)
    canvas.restoreState()


def dynamic_header_and_footer(canvas, doc):
    print('calling dynamic header and footer')
    # Dynamically determine or generate header_content and footer_content here
    styles = getSampleStyleSheet()
    header_content = Paragraph(
        f"Dynamic Header for Page {doc.page}", styles['Normal'])
    footer_content = Paragraph(
        f"Dynamic Footer for Page {doc.page}", styles['Normal'])

    header(canvas, doc, header_content)
    footer(canvas, doc, footer_content)


def create_dedication_page(contents, styles, dedictation_phrase):
    print('calling create_dedication_page')
    # Dynamically determine or generate header_content and footer_content here
    # center dedication phrase in the center of the page
    contents.append(Spacer(left_margin, .5*72))
    contents.append(Paragraph(dedictation_phrase, styles['Italic']))
    contents.append(PageBreak())


def create_title_page(contents, styles, title, subtitle, author):
    print('calling create_title_page')
    # Dynamically determine or generate header_content and footer_content here
    # center dedication phrase in the center of the page
    contents.append(Spacer(left_margin, .5*72))
    contents.append(Paragraph(title, styles['Heading1']))
    contents.append(Spacer(left_margin, .25*72))
    contents.append(Paragraph(subtitle, styles['Heading2']))
    contents.append(Spacer(left_margin, .5*72))
    contents.append(Paragraph(author, styles['Heading3']))
    contents.append(PageBreak())


def create_publishing_page(contents, styles, title, subtitle, author, publisher, year, isbn):
    print('calling create_title_page')
    # Dynamically determine or generate header_content and footer_content here
    # center dedication phrase in the center of the page
    contents.append(Spacer(left_margin, .5*72))
    contents.append(Paragraph(title, styles['Heading1']))
    contents.append(Spacer(left_margin, .25*72))
    contents.append(Paragraph(subtitle, styles['Heading2']))
    contents.append(Spacer(left_margin, .5*72))
    contents.append(Paragraph(author, styles['Heading3']))
    contents.append(Spacer(left_margin, .5*72))
    contents.append(Paragraph(f"ISBN {isbn}", styles['Normal']))
    contents.append(Spacer(left_margin, .25*72))
    contents.append(Paragraph(publisher, styles['Normal']))
    contents.append(Spacer(left_margin, .25*72))
    contents.append(Paragraph(f"© {year} {author}", styles['Normal']))
    contents.append(PageBreak())


def create_book(puzzle_words_list, theme_images_list, puzzle_images_list, puzzle_descriptions, puzzle_fun_facts):

    # Open and read the JSON file
    with open('puzzlebook.config', 'r') as file:
        data = json.load(file)

    # Accessing each item
    title = data["title"]
    subtitle = data["subtitle"]
    author = data["author"]
    isbn = data["isbn"]
    year = data["year"]
    publisher = data["publisher"]

    # Printing the values
    print(f"Title: {title}")
    print(f"Subtitle: {subtitle}")
    print(f"Author: {author}")
    print(f"ISBN: {isbn}")
    print(f"Year: {year}")
    print(f"Publisher: {publisher}")

    try:
        print("creating book...")
        if not all([puzzle_words_list, theme_images_list, puzzle_images_list, puzzle_descriptions]):
            messagebox.showerror(
                "Error", "Please provide non-empty lists of puzzle words, theme images, puzzle images, and puzzle descriptions!")
            return

        if not len(puzzle_words_list) == len(theme_images_list) == len(puzzle_images_list) == len(puzzle_descriptions):
            messagebox.showerror(
                "Error", "All input lists must be of the same length!")
            return

        gutter_width = 0.5 * inch

        custom_page_size = (6*inch, 9*inch)
        custom_margins = 0.5*inch
        doc = SimpleDocTemplate("output.pdf",
                                pagesize=custom_page_size,
                                topMargin=custom_margins,
                                bottomMargin=custom_margins,
                                leftMargin=custom_margins,
                                rightMargin=custom_margins)
        styles = getSampleStyleSheet()
        contents = []

        print("creating title page")
        create_title_page(
            contents, styles, title, subtitle, author)
        print("creating publishing page")
        create_publishing_page(contents, styles, title,
                               subtitle, author,
                               publisher, year, isbn)
        print("creating dedication page")
        create_dedication_page(
            contents, styles, "This book is dedicated to my wife and son.")

        headline_style = styles['Heading1']
        normal_style = styles['Normal']
        print(f"creating puzzle pages ({len(puzzle_words_list)} pages.)")
        for i in range(len(puzzle_words_list)):
            header_data = [[Paragraph(f"{puzzle_descriptions[i]}", styles['Normal']),
                            Paragraph(f"{i + 1}", styles['Normal'])]]

            # Adjust colWidths as needed
            # Create a table for the header with spacer on the left, topic in the middle, and page number on the right
            margin_offset = 1*inch if (i % 2 == 0) else 1.25*inch
            puzzle_offset = 0*inch if (i % 2 == 0) else .25*inch

            header_data = None

            if (i % 2 == 1):
                header_data = [[Paragraph(f"{puzzle_descriptions[i]}", styles['Normal']),
                                Paragraph(f"Page {i + 1}", styles['Normal'])]]
                gutter_width = 0.5 * inch
            else:
                header_data = [[Paragraph(f"Page {i + 1}", styles['Normal']),
                                Paragraph(f"{puzzle_descriptions[i]}", styles['Normal'])]]
                gutter_width = 0

            # Adjust column widths for the 6" x 9" size
            header_table = Table(header_data, colWidths=[
                                 4.5*inch - gutter_width, 1*inch])
            header_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), white),
                # ('BOX', (0, 0), (-1, 0), 1, black),
                ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (0, 0), 14),
                ('FONTNAME', (1, 0), (1, 0), 'Helvetica'),
                ('FONTSIZE', (1, 0), (1, 0), 12),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (0, 0), 20),
                ('RIGHTPADDING', (1, 0), (1, 0), 20),
            ])

            header_table.setStyle(header_style)
            #   header_table = Table(header_data, colWidths=[
            #                        margin_offset, 4*72, 2*72])
            # header_table.setStyle(TableStyle([
            #     ('ALIGN', (1, 0), (2, 0), 'RIGHT'),
            #     # ... (other styling)
            # ]))

            contents.append(header_table)
            # Add some space between header and content
            contents.append(Spacer(1, .5*72))

            img1 = ReportLabImage(
                theme_images_list[i], width=1.5*inch, height=1.5*inch)
          #  contents.append(img1)

            data = [['', img1, Paragraph(
                puzzle_fun_facts[i], styles['Normal'])]]

            image_table_style = TableStyle([
                # Adjusts vertical alignment of the second column
                ('VALIGN', (1, 0), (1, 0), 'TOP'),
            ])

            image_table = Table(data, colWidths=[
                puzzle_offset, 2*inch, 2.5*inch])

            image_table.setStyle(image_table_style)

            contents.append(image_table)

            contents.append(Spacer(1, .25*72))

            puzzle_image = ReportLabImage(
                puzzle_images_list[i], width=4*inch, height=4*inch)

            puzzle_row = [['', puzzle_image]]

            puzzle_table = Table(puzzle_row, colWidths=[
                                 puzzle_offset, 4*72])
            puzzle_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (1, 0), 'LEFT'),
            ]))

            contents.append(puzzle_table)

            contents.append(Spacer(left_margin, .25*72))

            puzzle_word_text = '<br/>' + puzzle_words_list[i]
            puzzle_word_text = puzzle_word_text.replace('\n', '<br/><br/>')

            custom_style = ParagraphStyle(
                "CustomStyle",
                parent=styles["Normal"],
                leftIndent=inch*.5,  # Indent by 36 points (0.5 inch)
            )

            paragraph = Paragraph(puzzle_word_text, custom_style)
            word_find_row = [['', paragraph]]
            word_find_table = Table(word_find_row, colWidths=[
                puzzle_offset, 4*inch])
            word_find_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ]))
            contents.append(word_find_table)

            if i < len(puzzle_words_list) - 1:
                contents.append(PageBreak())

        doc.build(contents)
        messagebox.showinfo("PDF Created", "PDF created successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Error creating PDF: {e}")

# Example usage:
# create_book(
#     ["word1, word2", "word3, word4"],
#     ["path/to/theme_image1.png", "path/to/theme_image2.png"],
#     ["path/to/puzzle_image1.png", "path/to/puzzle_image2.png"],
#     ["Puzzle Description 1", "Puzzle Description 2"]
# )


def create_pdf(puzzle_word_text):
    if not puzzle_word_text:
        messagebox.showerror("Error", "Please generate the dialog first!")
        return

    theme = combo1.get()

    # 3. Create a PDF with both the extracted image and some text
    doc = SimpleDocTemplate("output.pdf", pagesize=letter)

    # Create the contents list for the PDF
    contents = []

    styles = getSampleStyleSheet()
    headline_style = styles['Heading1']
    headline = Paragraph(theme.capitalize(), headline_style)
    contents.append(headline)

    # Add the extracted image
    # Adjust width and height as needed
    img1 = ReportLabImage(pil_image_path, width=2.5*inch, height=2.5*inch)
    contents.append(img1)
    img2 = ReportLabImage(puzzle_image_path, width=5*inch, height=5*inch)
    contents.append(img2)

    # Add some text
    puzzle_word_text = '<br/>' + puzzle_word_text
    puzzle_word_text = puzzle_word_text.replace('\n', '<br/><br/>')
    styles = getSampleStyleSheet()
    paragraph = Paragraph(puzzle_word_text, styles['Normal'])
    contents.append(paragraph)

    # Build the PDF
    doc.build(contents)

    # message box saying we finished generating the PDF
    messagebox.showinfo("PDF Created", "PDF created successfully!")


def generate_image(theme):
    response = openai.Image.create(
        model="image-alpha-001",
        prompt=f"cartoon image of {theme} that must fit in 512x512 dimensions",
        n=1,  # Number of images to generate
        size="512x512",  # Size of the generated image
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
    # image.resize((200, 200), Image.ANTIALIAS)

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


def create_grid_of_letters_image(letters):
    # Set image size, background color, and font size
    img_size = (1200, 1200)
    background_color = (255, 255, 255)  # white
    font_size = 72

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
            position = (j * (font_size + 20) + 20, i * (font_size + 20) + 20)
            # Draw letter with black color
            d.text(position, letter, font=fnt, fill=(0, 0, 0))

    # Save the image
    img.save(puzzle_image_path)


def remove_numbers(s):
    return ''.join([char for char in s if not char.isdigit()])


def clean_words(words):

    # remove any words that repeat
    words = list(dict.fromkeys(words))

    # choose only words that are 10 characters or less when punctuation is stripped
    # and spaces removed
    clean_words = []
    for word in words:
        word = word.upper().replace(" ", "")
        # remove any punctuation
        word = word.translate(str.maketrans('', '', string.punctuation))
        word = remove_numbers(word)  # remove any numbers as well
        if (len(word) <= 10):
            clean_words.append(word)

    # narrow down words to only a list of 10
    if len(clean_words) > 10:
        clean_words = random.sample(clean_words, 10)

    # sort the words by size with largest first
    clean_words.sort(key=len, reverse=True)
    return clean_words


def clean_topics(words):

    # remove any words that repeat
    words = list(dict.fromkeys(words))

    # choose only words that are 10 characters or less when punctuation is stripped
    # and spaces removed
    clean_words = []
    for word in words:
        word = word.upper().replace(" ", "")
        # remove any punctuation
        word = word.translate(str.maketrans('', '', string.punctuation))
        if (len(word) <= 10):
            clean_words.append(word)

    # sort the words by size with largest first
    clean_words.sort(key=len, reverse=True)
    return clean_words


def copy_image(src_path, prefix, puzzle_part):
    try:
        dst_path = f"{prefix}_{puzzle_part}_src_path.png"
        shutil.copy2(src_path, dst_path)
        print(f'Successfully copied {src_path} to {dst_path}')
        return dst_path
    except FileNotFoundError:
        print(f'The file at {src_path} was not found.')
    except PermissionError:
        print(f'Permission denied. Unable to write to {dst_path}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')

    # Backup the puzzle image
    # the header images
    # the puzzle words string array
    # to a new folder with timestamp under the temp directory
    # and the fun facts


def create_file_from_wordlist(filename, words, backup_folder):
    # Open the file in write mode and write each string to the file
    with open(f"{backup_folder}\\{filename}.txt", 'w') as file:
        for word in words:
            file.write(word + '\n\n')  # Add a newline after each string


def backupcontent(theme, header_images, puzzle_images, puzzle_words, puzzle_descriptions, puzzle_fun_facts):
    # create a new folder that has the theme and the timestamp
    print("backing up content...")
    # copy the header images to the folder

    # copy the puzzle image to the folder
    # copy the puzzle words to the folder
    # copy the puzzle descriptions to the folder
    # copy the puzzle fun facts to the folder
    # Create a new folder that has the theme and the timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    backup_folder = f"c:\\temp\\{theme}_{timestamp}"
    os.makedirs(backup_folder, exist_ok=True)

    # Copy the header images to the folder
    for image in header_images:
        shutil.copy(image, backup_folder)

    # Copy the puzzle image to the folder
    for image in puzzle_images:
        shutil.copy(image, backup_folder)

    # Copy the puzzle words, descriptions, and fun facts to the folder
    # Assuming these are text files, if not, adjust accordingly
    create_file_from_wordlist(
        "puzzle_words", puzzle_words, backup_folder)
    create_file_from_wordlist(
        "puzzle_descriptions", puzzle_descriptions, backup_folder)
    create_file_from_wordlist("puzzle_fun_facts",
                              puzzle_fun_facts, backup_folder)

    print("content backed up successfully!")


def batch_submit():
    puzzle_words_list = []
    theme_images_list = []
    puzzle_images_list = []
    puzzle_descriptions = []
    puzzle_fun_facts = []

    set_wait_cursor()
    theme = combo1.get()

    with open('puzzlebook.config', 'r') as file:
        data = json.load(file)

    numberOfPuzzles = data["numberOfPuzzles"]
    print("Number of puzzles: " + str(numberOfPuzzles))

   # prompt = f"Create a comma delimited list of 40 words having to do with the theme {theme}. None of the words in the list should repeat\n"
    prompt = f"Create a comma delimited list of {numberOfPuzzles} costumes people may dress up for on around the holiday of {theme}. None of the costumes in the list should repeat. Do not number the list, please separate each costume by a comma. Do not use any trademark characters.\n"
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

    # retrieve the list of words created by ChatGPT
    chatGPTAnswer = response["choices"][0]["message"]["content"]
    print(chatGPTAnswer)
    # split the comma delimited list of words into a list
    topics = chatGPTAnswer.split(',')

    # sometimes chatgpt generates more topics than you asked for
    if len(topics) > numberOfPuzzles:
        topics = topics[:numberOfPuzzles]

    topics = clean_topics(topics)  # clean up the topics list.
    print(topics)

    # now create a list of words from each of those words
    for topic in topics:
        print(topic)
        # save puzzle description
        puzzle_descriptions.append(topic)

        prompt = f"Create a comma delimited list of 40 words having to do with the theme {topic}. None of the words in the list should repeat. Do not use any trademark names.\n"
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

        # retrieve the list of words created by ChatGPT
        chatGPTAnswer = response["choices"][0]["message"]["content"]
        print(chatGPTAnswer)

        # split the comma delimited list of words into a list
        words = chatGPTAnswer.split(',')
        words = clean_words(words)  # pick out a list of 10 viable words
        print(words)

        # create word search puzzle array from words
        (board, words_to_remove) = puzzle_board_creator.create_word_search(words)
        # remove words that could not be placed
        words = [word for word in words if word not in words_to_remove]
        puzzle_words_list.append(', '.join(words))
        # show the board on the console
        puzzle_board_creator.display_board(board)
        label_puzzle_words.config(text=', '.join(words))
        # make result_text scrollable

        result_text.config(state="normal")
        result_text.delete(1.0, tk.END)  # Clear any previous results
        result_text.insert(tk.END, chatGPTAnswer)
        result_text.config(state="disabled")

        # generates a cartoon image of the theme
        image_url = generate_image(topic)
        # creates a grid of letters into an image for the puzzle
        create_grid_of_letters_image(board)
        display_image_from_url(image_holder, image_url)
        dest_theme_image_path = copy_image(pil_image_path,  topic, "theme")
        theme_images_list.append(dest_theme_image_path)

        display_image_from_path(puzzle_holder, puzzle_image_path)
        dest_puzzle_image_path = copy_image(puzzle_image_path, topic, "puzzle")
        puzzle_images_list.append(dest_puzzle_image_path)

        puzzle_holder.config(width=600, height=600)
        set_normal_cursor()

        # come up with a fun filled fact
        promptForFact = f"Come up with one fun filled fact about {pluralize(topic)}).\n"
        messages = [{'role': 'user', 'content': promptForFact}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.8,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.6,
        )

        print(promptForFact)

        # retrieve the list of words created by ChatGPT
        fact = response["choices"][0]["message"]["content"]
        print(fact)
        puzzle_fun_facts.append(fact)
    backupcontent(theme, theme_images_list, puzzle_images_list, puzzle_words_list,
                  puzzle_descriptions, puzzle_fun_facts)
    create_book(puzzle_words_list, theme_images_list,
                puzzle_images_list, puzzle_descriptions, puzzle_fun_facts)


def submit():
    set_wait_cursor()
    theme = combo1.get()

    prompt = f"Create a comma delimited list of 40 words having to do with the theme {theme}. None of the words in the list should repeat\n"
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

    # retrieve the list of words created by ChatGPT
    chatGPTAnswer = response["choices"][0]["message"]["content"]
    print(chatGPTAnswer)
    # split the comma delimited list of words into a list
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

    # generates a cartoon image of the theme
    image_url = generate_image(theme)
    # creates a grid of letters into an image for the puzzle
    create_grid_of_letters_image(board)
    display_image_from_url(image_holder, image_url)
    display_image_from_path(puzzle_holder, puzzle_image_path)
    puzzle_holder.config(width=600, height=600)
    set_normal_cursor()


app = tk.Tk()
app.title("Word Puzzle Book")


# Label and ComboBox for the first animal
label1 = ttk.Label(app, text="Select a Word Puzzle Theme:")
label1.grid(column=0, row=0, padx=10, pady=5)
combo1 = ttk.Combobox(
    app, values=["Halloween", "Holidays", "Science", "Travel", "AI", "Cars", "Food", "Entertainment", "Sports", "Space", "Work", "School", "Animals", "Nature", "Art", "Music", "Movies", "Books", "History", "Math", "Geography", "Weather", "Fashion", "Health", "Family", "Money", "Politics", "Religion", "Technology", "Games", "Business", "Crime", "Law", "Medicine", "Psychology", "Language", "Culture", "Relationships", "Social Media", "News", "Shopping", "Transportation", "Architecture", "Design", "Gardening", "Hobbies", "Humor", "Literature", "Philosophy", "Photography", "Writing", "Other"])
combo1.grid(column=1, row=0, padx=10, pady=5)
combo1.set("Halloween")


# Button to submit the details
submit_btn = ttk.Button(app, text="Submit", command=submit)
submit_btn.grid(column=0, row=3, padx=10, pady=20)

# Button to submit the details
create_book_btn = ttk.Button(app, text="Create Book", command=batch_submit)
create_book_btn.grid(column=2, row=3, padx=10, pady=20)

# make it scrollable
# Create a Scrollbar widget
scrollbar = tk.Scrollbar(app)
scrollbar.grid(row=4, column=3, sticky='ns')

# Text widget to display results
result_text = tk.Text(app, width=50, height=10,
                      wrap=tk.WORD, yscrollcommand=scrollbar.set)
result_text.grid(column=0, row=4, rowspan=1, columnspan=4, padx=10, pady=10)
result_text.config(state="disabled")
# result_text.pack(expand=True, fill=tk.BOTH)

image_holder = tk.Label(app)
image_holder.grid(column=0, row=5, columnspan=2, padx=10, pady=10)

puzzle_holder = tk.Label(app)
puzzle_holder.grid(column=5, row=0, rowspan=7,  padx=2,
                   pady=2)

label_key_title = ttk.Label(app, text="Puzzle Words")
label_key_title.grid(column=5, row=6, padx=10, pady=5)

label_puzzle_words = ttk.Label(app, text="")
label_puzzle_words.grid(column=5, row=7, padx=10, pady=10)

# Button to submit the details
create_pdf_btn = ttk.Button(
    app, text="Create Pdf", command=lambda: create_pdf(label_puzzle_words['text']))
create_pdf_btn.grid(column=1, row=3, padx=10, pady=20)

scrollbar.config(command=result_text.yview)


# Link the scrollbar to the text widget (so the scrollbar knows how to scroll the text widget)


app.mainloop()
