from datetime import datetime
import time
import shutil
from tkinter import filedialog
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
from reportlab.lib.colors import black, white, gray
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
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
    create_book_btn.config(cursor="watch")
    app.update_idletasks()  # Force an immediate update of the window
    time.sleep(2)  # Simulate some long operation


def set_normal_cursor():
    create_book_btn.config(cursor="")


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
    # Create a new style based on 'Normal' but with centered text
    centered_italic_style = ParagraphStyle(
        'centered', parent=styles['Italic'], alignment=TA_CENTER)
    contents.append(Paragraph(dedictation_phrase, centered_italic_style))
    contents.append(PageBreak())


def create_title_page(contents, styles, title, subtitle, author, coverImagePath):
    print('calling create_title_page')
    # Dynamically determine or generate header_content and footer_content here
    # center dedication phrase in the center of the page
    contents.append(Spacer(left_margin, .5*72))
    contents.append(Paragraph(title, styles['Heading1']))
    contents.append(Spacer(left_margin, .125*72))
    contents.append(Paragraph(subtitle, styles['Heading2']))
    contents.append(Spacer(left_margin, .5*72))
    coverImage = ReportLabImage(
        coverImagePath, width=4.5*inch, height=4.5*inch)
    contents.append(coverImage)
    contents.append(Spacer(left_margin, .5*72))
    contents.append(Paragraph(author, styles['Heading3']))
    contents.append(PageBreak())


def create_publishing_page(contents, styles, title, subtitle, author, publisher, year, isbn, coverImagePath):
    print('calling create_publishing_page')
    # Dynamically determine or generate header_content and footer_content here
    # center dedication phrase in the center of the page
    contents.append(Spacer(left_margin, .5*72))
    contents.append(Paragraph(title, styles['Heading1']))
    contents.append(Spacer(left_margin, .125*72))
    contents.append(Paragraph(subtitle, styles['Heading2']))
    contents.append(Spacer(left_margin, .5*72))
    coverImage = ReportLabImage(
        coverImagePath, width=1.5*inch, height=1.5*inch)
    contents.append(coverImage)
    contents.append(Spacer(left_margin, .5*72))
    contents.append(Paragraph(author, styles['Heading3']))
    contents.append(Spacer(left_margin, .5*72))
    # temporarily center the style
    # Create a new style based on 'Normal' but with centered text
    centered_style = ParagraphStyle(
        'centered', parent=styles['Normal'], alignment=TA_CENTER)
    contents.append(Paragraph(f"ISBN {isbn}", centered_style))
    contents.append(Spacer(left_margin, .25*72))
    contents.append(Paragraph(publisher, centered_style))
    contents.append(Spacer(left_margin, .25*72))
    contents.append(Paragraph(f"© {year} {author}", centered_style))
    contents.append(PageBreak())


def create_book(puzzle_words_list, theme_images_list, puzzle_images_list, puzzle_descriptions, puzzle_fun_facts, puzzle_topics_list):

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
    outputFilePath = data["outputFilePath"]
    coverImagePath = data["coverImagePath"]

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

        print(f"puzzle_words_list (length): {len(puzzle_words_list)}")
        print(f"theme_images_list (length): {len(theme_images_list)}")
        print(f"puzzle_images_list (length): {len(puzzle_images_list)}")
        print(f"puzzle_descriptions (length): {len(puzzle_descriptions)}")
        print(f"puzzle_topics_list (length): {len(puzzle_topics_list)}")
        print(f"puzzle_fun_facts (length): {len(puzzle_fun_facts)}")

        if not len(puzzle_words_list) == len(theme_images_list) == len(puzzle_images_list) == len(puzzle_descriptions):
            messagebox.showerror(
                "Error", "All input lists must be of the same length!")
            return

        gutter_width = 0.5 * inch
        right_gutter_width = gutter_width

        custom_page_size = (6*inch, 9*inch)
        custom_margins = 0.5*inch
        custom_vertical_margin = 0.25*inch
        doc = SimpleDocTemplate(outputFilePath,
                                pagesize=custom_page_size,
                                topMargin=custom_vertical_margin,
                                bottomMargin=custom_vertical_margin,
                                leftMargin=custom_margins,
                                rightMargin=custom_margins)
        styles = getSampleStyleSheet()
        styles['Normal'].fontName = 'Helvetica'
        styles['Heading1'].fontSize = 24
        styles['Heading2'].fontSize = 20
        styles['Heading3'].fontSize = 18
        styles['Heading1'].alignment = TA_CENTER
        styles['Heading2'].alignment = TA_CENTER
        styles['Heading3'].alignment = TA_CENTER
        styles['Heading1'].spaceAfter = 0
        styles['Heading2'].spaceBefore = 0
        contents = []

        print("creating title page")
        create_title_page(
            contents, styles, title, subtitle, author, coverImagePath)
        print("creating publishing page")
        create_publishing_page(contents, styles, title,
                               subtitle, author,
                               publisher, year, isbn, coverImagePath)
        print("creating dedication page")
        create_dedication_page(
            contents, styles, "This book is dedicated to my wife and son.")

        headline_style = styles['Heading1']
        normal_style = styles['Normal']
        print(f"creating puzzle pages ({len(puzzle_words_list)} pages.)")
        for i in range(len(puzzle_words_list)):
            header_data = [[Paragraph(f"{puzzle_topics_list[i]}", styles['Normal']),
                            Paragraph(f"{i + 1}", styles['Normal'])]]

            # Adjust colWidths as needed
            # Create a table for the header with spacer on the left, topic in the middle, and page number on the right
            margin_offset = 1*inch if (i % 2 == 0) else 1.25*inch
            puzzle_offset = 0*inch if (i % 2 == 0) else .25*inch

            header_data = None
            style_right = ParagraphStyle(
                name='RightAlign', parent=styles['Normal'], alignment=2)

            if (i % 2 == 1):
                header_data = [[Paragraph(f"{puzzle_topics_list[i]}", styles['Normal']), "",
                                Paragraph(f"Page {i + 1}", style_right)]]
                gutter_width = 0.5 * inch
                right_gutter_width = 0
            else:
                header_data = [[Paragraph(f"Page {i + 1}", styles['Normal']), "",
                                Paragraph(f"{puzzle_topics_list[i]}", style_right)]]
                gutter_width = 0
                right_gutter_width = 0.5 * inch

            # Adjust column widths for the 6" x 9" size

            # Define the column widths
            col_widths = [2 * inch, 2 * inch, 2 * inch]  # Adjust as needed

            # Create the header table
            header_table = Table(header_data, colWidths=col_widths)

            # Apply a style to the header table
            header_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                # ('GRID', (0, 0), (-1, -1), 1, black),
                ('LEFTPADDING', (0, 0), (0, 0), .35 * inch + gutter_width),
                ('RIGHTPADDING', (2, 0), (2, 0), .35 * inch + right_gutter_width),
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
            contents.append(Spacer(1, .4*72))

            img1 = ReportLabImage(
                theme_images_list[i], width=1.5*inch, height=1.5*inch)
          #  contents.append(img1)

            data = [['', img1, Paragraph(
                puzzle_fun_facts[i], styles['Normal'])]]

            image_table_style = TableStyle([
                # Adjusts vertical alignment of the second column
                ('VALIGN', (1, 0), (1, 0), 'TOP'),
                ('VALIGN', (2, 0), (2, 0), 'TOP'),
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
                                 puzzle_offset, 4*inch])
            puzzle_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (1, 0), 'LEFT'),
            ]))

            contents.append(puzzle_table)

            contents.append(Spacer(left_margin + .15*inch, .02*72))

            puzzle_word_text = '<br/>' + puzzle_words_list[i]
            puzzle_word_text = puzzle_word_text.replace('\n', '<br/><br/>')

            custom_style = ParagraphStyle(
                "CustomStyle",
                parent=styles["Normal"], fontsize=18,
                # Indent by 36 points (0.5 inch)
                leftIndent=inch*.55 if i % 2 == 0 else inch*.70,
                rightIndent=inch*.25,
            )

            # create a table that splits the list of puzzle_word_text into three columns
            # the first column has 4 words, the second column has 3 words, and the third column has 3 words

            # split the puzzle_word_text into a list of words
            words = puzzle_word_text.split(",")
            # split the list of words into three lists of words
            words1 = words[:3]
            words2 = words[3:6]
            words3 = words[6:-1]

            left_indent = inch*.55 if i % 2 == 0 else inch*.70
            custom_word_style = ParagraphStyle(
                "CustomStyle",
                parent=styles["Normal"],
                fontSize=12,
                # Indent by 36 points (0.5 inch)
                # leftIndent=left_indent,
                # rightIndent=inch*.25,
                wordWrap='LTR',
            )

            # create a paragraph for each list of words
            # do list comprehension to create a list of paragraphs from words1
            paragraphs1 = [Paragraph("")] + [Paragraph(word, custom_word_style)
                                             for word in words1]
            paragraphs2 = [Paragraph("")] + [Paragraph(word, custom_word_style)
                                             for word in words2]
            paragraphs3 = [Paragraph("")] + [Paragraph(word, custom_word_style)
                                             for word in words3]
            paragraph4 = [Paragraph("")] + [Paragraph(
                words[-1], custom_word_style), Paragraph(""), Paragraph(""), Paragraph("")]

            # create a table with three columns and 4 rows
            word_find_row = [paragraphs1, paragraphs2, paragraphs3, paragraph4]
            word_find_table = Table(word_find_row, colWidths=[inch * 1.65 + puzzle_offset,
                                                              1.45*inch, 1.45*inch, 1.45 * inch]
                                    )
            word_find_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, 0), 'LEFT'),

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
    try:
        response = openai.Image.create(
            prompt=f"a(n) {theme}",
            n=1,  # Number of images to generate
            size="512x512",  # Size of the generated image
            response_format="url"  # Format in which the image will be received
        )
    except Exception as e:
        messagebox.showerror("Error", f"Error generating image: {e}")
        return None

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
        #     word = word.upper().replace(" ", "")
        # remove any punctuation
        word = word.translate(str.maketrans('', '', string.punctuation))
        word = word.strip()
        if (len(word) <= 30):
            clean_words.append(word)

    # sort the words by size with largest first
    clean_words.sort(key=len, reverse=True)
    return clean_words


def copy_image(base_file_path, src_path, prefix, puzzle_part):
    try:
        dst_path = f"{base_file_path}{prefix}_{puzzle_part}_src_path.png"
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
        count = 0
        length = len(words)
        for word in words:
            if count == length - 1:
                file.write(word)
            else:
                file.write(word + '|')  # Add a newline after each string
            count = count + 1


def add_word_to_wordlist(filename, word, backup_folder, is_first_word=False):
    # Open the file in write mode and write each string to the file
    # open file to append word

    with open(f"{backup_folder}\\{filename}.txt", 'a') as file:
        if (is_first_word):
            file.write(word)
        else:
            file.write('|' + word)


def read_description_file_from_backup(filename):
    # Open the file in read mode and read each string from the file
    with open(filename, 'r') as file:
        # read the entire file into a string
        file_contents = file.read()
        # split the string into an array of strings
        words = file_contents.split('|')
        return words


def reconstruct_book_from_backup(backup_folder):
    # read in each array of items from the back up folder
    puzzle_descriptions_list = read_description_file_from_backup(
        f"{backup_folder}\\puzzle_descriptions.txt")

    # read in each image from the back up folder into a list
    theme_images_list = []
    puzzle_images_list = []
    puzzle_words_list = []
    puzzle_facts_list = []

    # strip spaces from topics, by mapping strip function
    puzzle_topics_list = get_topics_from_file()
    topics = list(map(str.strip, puzzle_topics_list))
    # remove punctuation from all topics
    topics = [topic.translate(str.maketrans(
        '', '', string.punctuation)) for topic in topics]
    puzzle_descriptions_list = topics
    # for word in puzzle_descriptions_list:
    for word in topics:
        next_puzzle_words = read_puzzle_words(word, backup_folder)
        puzzle_words_list.append(next_puzzle_words)
        next_fact = read_fun_filled_fact(word, backup_folder)
        puzzle_facts_list.append(next_fact)

    if (reconstruct_puzzles_chk_var.get() == 1):
        print("reconstructing puzzles from text files...")
        for word in puzzle_descriptions_list:
            theme_images_list.append(
                f"{backup_folder}\\{word}_theme_src_path.png")
            board = []
            next_board = puzzle_board_creator.read_board_from_file(
                f"{backup_folder}/", word, board)
            # generate image from board
            create_grid_of_letters_image(next_board)
            dest_puzzle_image_path = copy_image(
                f"{backup_folder}\\", puzzle_image_path, word, "puzzle")
            puzzle_images_list.append(dest_puzzle_image_path)
    else:
        print("reconstructing puzzles from backup images...")
        # use each word list to form the filepath to the image (include backup_folder)
        for word in puzzle_descriptions_list:
            theme_images_list.append(
                f"{backup_folder}\\{word}_theme_src_path.png")
            puzzle_images_list.append(
                f"{backup_folder}\\{word}_puzzle_src_path.png")

    print(puzzle_words_list)
    print(theme_images_list)
    print(puzzle_images_list)
    print(puzzle_descriptions_list)
    print(puzzle_facts_list)

    print("reconstructing book...")
    create_book(puzzle_words_list, theme_images_list,
                puzzle_images_list, puzzle_descriptions_list, puzzle_facts_list, puzzle_topics_list)


def construct_book_from_backup():
    # prompt user for the backup folder
    backup_folder = ''
    backup_folder = filedialog.askdirectory(
        initialdir="c:\\temp", title="Select backup folder of book")
    reconstruct_book_from_backup(backup_folder)


def backup_content(theme, header_images, puzzle_images, puzzle_words, puzzle_descriptions, puzzle_fun_facts, puzzle_text_images):
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

    # Copy the puzzle text images to the folder
    for text_image in puzzle_text_images:
        shutil.copy(text_image, backup_folder)

    # Copy the puzzle words, descriptions, and fun facts to the folder
    # Assuming these are text files, if not, adjust accordingly
    create_file_from_wordlist(
        "puzzle_words", puzzle_words, backup_folder)
    create_file_from_wordlist(
        "puzzle_descriptions", puzzle_descriptions, backup_folder)
    create_file_from_wordlist("puzzle_fun_facts",
                              puzzle_fun_facts, backup_folder)

    print("content backed up successfully!")


def check_if_topic_already_created(base_file_path, topic):
    # just see if the file exists in the base_file_path
    full_path = f"{base_file_path}{topic}_puzzle_src_path.png"
    if os.path.exists(full_path):
        return True
    return False


def batch_submit():
    puzzle_words_list = []
    theme_images_list = []
    puzzle_images_list = []
    puzzle_text_images_list = []
    puzzle_descriptions = []
    puzzle_fun_facts = []

    set_wait_cursor()
    theme = combo1.get()

    # GPT_Model = "gpt-4-0613"
    GPT_Model = "gpt-3.5-turbo"

    data = get_configuration()

    numberOfPuzzles = data["numberOfPuzzles"]
    base_file_path = data["tempFilePath"]
    dummy_puzzle_book_image = data["dummyImageUrl"]
    print("Number of puzzles: " + str(numberOfPuzzles))
    puzzle_clues_prompt = data["puzzleCluesPrompt"]
    fun_filled_fact_prompt = data["funFilledFactPrompt"]

    topics = []
    if (generate_topics_chk_var.get() == 1):
        topics = get_topics_from_file()
    else:
        topics = generate_topics(theme, GPT_Model, numberOfPuzzles)

    # sometimes chatgpt generates more topics than you asked for
    if len(topics) > numberOfPuzzles:
        topics = topics[:numberOfPuzzles]

    topics = clean_topics(topics)  # clean up the topics list.
    print(topics)

    # now create a list of words from each of those words
    count = 0
    for topic in topics:
        print(f"processing topic {count + 1} of {len(topics)}")
        count += 1
        if (check_if_topic_already_created(base_file_path, topic)):
            print(f"Skipping topic {topic} because it already exists.")
            continue

        time.sleep(1)
        print(topic)

        print(f"generating puzzle clues for {topic}...")

        prompt = puzzle_clues_prompt.format(theme=theme, topic=topic)
        messages = [{'role': 'user', 'content': prompt}]
        try:
            response = openai.ChatCompletion.create(
                model=GPT_Model,
                messages=messages,
                temperature=0.8,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.6,
            )

            print(prompt)
            time.sleep(1)

            # retrieve the list of words created by ChatGPT
            chatGPTAnswer = response["choices"][0]["message"]["content"]
            print(chatGPTAnswer)
        except Exception as e:
            messagebox.showerror(
                "Error", f"Error generating puzzle clues for {topic}, skipping topic: {e}")
            continue

        # save puzzle description
        puzzle_descriptions.append(topic)

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
        # write the board to a file
        text_board_path = puzzle_board_creator.write_board_to_file(
            base_file_path, topic, board)
        puzzle_text_images_list.append(text_board_path)
        print('text board path: ' + text_board_path)

        label_puzzle_words.config(text=', '.join(words))
        # make result_text scrollable

        result_text.config(state="normal")
        result_text.delete(1.0, tk.END)  # Clear any previous results
        result_text.insert(tk.END, chatGPTAnswer)
        result_text.config(state="disabled")

        # generates a cartoon image of the theme,
        # if it errors out keep trying
        # image_url = dummy_puzzle_book_image
        image_url = generate_image(topic)
        if image_url is None:
            image_url = dummy_puzzle_book_image

        # creates a grid of letters into an image for the puzzle
        create_grid_of_letters_image(board)
        display_image_from_url(image_holder, image_url)
        dest_theme_image_path = copy_image(
            base_file_path, pil_image_path,  topic, "theme")
        theme_images_list.append(dest_theme_image_path)

        display_image_from_path(puzzle_holder, puzzle_image_path)
        dest_puzzle_image_path = copy_image(
            base_file_path, puzzle_image_path, topic, "puzzle")
        puzzle_images_list.append(dest_puzzle_image_path)

        puzzle_holder.config(width=600, height=600)
        set_normal_cursor()

        # come up with a fun filled fact
        print(f"creating a fun filled fact about {topic}...")
        create_fun_filled_fact(puzzle_fun_facts, GPT_Model,
                               topic, fun_filled_fact_prompt)

        # sleep for 15 seconds to avoid hitting the API rate limit
        time.sleep(15)
        # Copy the puzzle words, descriptions, and fun facts to the folder
        # Assuming these are text files, if not, adjust accordingly
        backup_text_lists(topic, puzzle_words_list, puzzle_descriptions,
                          puzzle_fun_facts, base_file_path)

    backup_content(theme, theme_images_list, puzzle_images_list, puzzle_words_list,
                   puzzle_descriptions, puzzle_fun_facts, puzzle_text_images_list)

    create_book(puzzle_words_list, theme_images_list,
                puzzle_images_list, puzzle_descriptions, puzzle_fun_facts, topics)


def write_puzzle_words(topic, puzzle_words, backup_folder):
    # Open the file in write mode and write each string to the file
    with open(f"{backup_folder}\\{topic}_puzzle_words.txt", 'w') as file:
        # join the list of words into a string
        file.write(puzzle_words)


def read_puzzle_words(topic, backup_folder):
    # Open the file in read mode and read each string from the file
    with open(f"{backup_folder}\\{topic}_puzzle_words.txt", 'r') as file:
        # read the entire file into a string
        file_contents = file.read()
        # split the string into an array of strings
        return file_contents


def write_fun_filled_fact(topic, puzzle_fun_fact, backup_folder):
    # Open the file in write mode and write each string to the file
    with open(f"{backup_folder}\\{topic}_puzzle_fact.txt", 'w') as file:
        # join the list of words into a string
        file.write(puzzle_fun_fact)


def read_fun_filled_fact(topic, backup_folder):
    # Open the file in read mode and read each string from the file
    with open(f"{backup_folder}\\{topic}_puzzle_fact.txt", 'r') as file:
        # read the entire file into a string
        file_contents = file.read()
        # split the string into an array of strings
        return file_contents


def backup_text_lists(topic, puzzle_words_list, puzzle_descriptions, puzzle_fun_facts, base_file_path):
    backup_folder = base_file_path
    # write the puzzle words to a file based on the topic
    write_puzzle_words(topic, puzzle_words_list[-1], backup_folder)
    # write the puzzle fun filled fact file based on the topic
    write_fun_filled_fact(topic, puzzle_fun_facts[-1], backup_folder)

    add_word_to_wordlist(
        "puzzle_words", puzzle_words_list[-1], backup_folder, len(puzzle_words_list) == 1)
    add_word_to_wordlist(
        "puzzle_descriptions", puzzle_descriptions[-1], backup_folder, len(puzzle_descriptions) == 1)
    add_word_to_wordlist("puzzle_fun_facts",
                         puzzle_fun_facts[-1], backup_folder, len(puzzle_fun_facts) == 1)


def create_fun_filled_fact(puzzle_fun_facts, GPT_Model, topic, fun_filled_fact_prompt):
    try:
        # f"Come up with one fun filled fact about {pluralize(topic)}).\n"
        promptForFact = fun_filled_fact_prompt.format(topic=pluralize(topic))
        messages = [{'role': 'user', 'content': promptForFact}]
        response = openai.ChatCompletion.create(
            model=GPT_Model,
            messages=messages,
            temperature=0.8,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.6,
        )

        print(promptForFact)
        time.sleep(1)

        # retrieve the list of words created by ChatGPT
        fact = response["choices"][0]["message"]["content"]
    except Exception as e:
        fact = f"No fun fact was generated for the {topic} puzzle."
    print(fact)
    puzzle_fun_facts.append(fact)


def get_configuration():
    with open('puzzlebook.config', 'r') as file:
        data = json.load(file)
    return data


def generate_topics(theme, GPT_Model, numberOfPuzzles):
    prompt = f"Create a comma delimited list of {numberOfPuzzles} costumes people may dress up for on around the holiday of {theme}. None of the costumes in the list should repeat. Do not number the list, please separate each costume by a comma. Do not use any trademark characters.Remember Comma delimited, NOT a numbered list."
    print(prompt)

    messages = [{'role': 'user', 'content': prompt}]
    response = openai.ChatCompletion.create(
        model=GPT_Model,
        messages=messages,
        temperature=0.8,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.6,
    )

    # retrieve the list of words created by ChatGPT
    chatGPTAnswer = response["choices"][0]["message"]["content"]
    print(chatGPTAnswer)
    # split the comma delimited list of words into a list
    topics = chatGPTAnswer.split(',')
    return topics


def get_topics_from_file():
    # use pathToTopicsFile to read in the topics
    config = get_configuration()
    pathToTopics = config["pathToTopics"]
    # return the list of topics
    topics = []
    with open(pathToTopics, 'r') as file:
        # read the entire file into a string
        file_contents = file.read()
        # split the string into an array of strings
        topics = file_contents.split(',')
        return topics


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

data = get_configuration()

preferred_theme = data["preferredTheme"]


# Label and ComboBox for the first animal
label1 = ttk.Label(app, text="Select a Word Puzzle Theme:")
label1.grid(column=0, row=0, padx=10, pady=5)
combo1 = ttk.Combobox(
    app, values=["Halloween", "Christmas", "Science", "Travel", "AI", "Cars", "Food", "Entertainment", "Sports", "Space", "Work", "School", "Animals", "Nature", "Art", "Music", "Movies", "Books", "History", "Math", "Geography", "Weather", "Fashion", "Health", "Family", "Money", "Politics", "Religion", "Technology", "Games", "Business", "Crime", "Law", "Medicine", "Psychology", "Language", "Culture", "Relationships", "Social Media", "News", "Shopping", "Transportation", "Architecture", "Design", "Gardening", "Hobbies", "Humor", "Literature", "Philosophy", "Photography", "Writing", "Other"])
combo1.grid(column=1, row=0, padx=10, pady=5)
combo1.set(preferred_theme)


# # Button to submit the details
# submit_btn = ttk.Button(app, text="Submit", command=submit)
# submit_btn.grid(column=0, row=3, padx=10, pady=20)

# Button to submit the details
create_book_btn = ttk.Button(app, text="Create Book", command=batch_submit)
create_book_btn.grid(column=0, row=3, padx=10, pady=20)

# generate topics from file checkbox
generate_topics_chk_var = tk.IntVar(value=1)
generate_topics_chk = ttk.Checkbutton(
    app, text="read topics from file", variable=generate_topics_chk_var)
generate_topics_chk.grid(column=1, row=1, padx=10, pady=20)

# reconstruct puzzles from text file checkbox
reconstruct_puzzles_chk_var = tk.IntVar(value=0)
reconstruct_puzzles_chk = ttk.Checkbutton(
    app, text="reconstruct puzzles from backup", variable=reconstruct_puzzles_chk_var)
reconstruct_puzzles_chk.grid(column=1, row=2, padx=10, pady=2)

# reconstruct book button
reconstruct_book_btn = ttk.Button(
    app, text="Reconstruct Book", command=construct_book_from_backup)
reconstruct_book_btn.grid(column=1, row=3, padx=10, pady=20)


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
# create_pdf_btn = ttk.Button(
#     app, text="Create Pdf", command=lambda: create_pdf(label_puzzle_words['text']))
# create_pdf_btn.grid(column=1, row=3, padx=10, pady=20)

scrollbar.config(command=result_text.yview)


# Link the scrollbar to the text widget (so the scrollbar knows how to scroll the text widget)


app.mainloop()
