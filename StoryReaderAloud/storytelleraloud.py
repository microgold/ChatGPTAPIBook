import os
from openai import OpenAI
import PyPDF2


def extract_text_from_pdf(pdf_path):
    """ Extracts text from a PDF file. """
    text = ''
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            page_text = page.extract_text() if page.extract_text() else ''
            # Optional: Add additional text cleaning here if necessary
            text += page_text
    return text


def text_to_speech(text, filename="output.mp3"):
    """ Converts text to speech using OpenAI's API and saves it to an MP3 file. """
    client = OpenAI()
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )
        response.stream_to_file(filename)
        print(f"Audio file created: {filename}")
    except Exception as e:
        print(f"Failed to create speech: {e}")


def main():
    pdf_path = "TaleOfTwoCitiesTruncated.pdf"  # Specify your PDF file path here
    output_audio = "output.mp3"      # Specify your output audio file name

    # Extract text from the PDF
    print("Extracting text from PDF...")
    extracted_text = extract_text_from_pdf(pdf_path)
    if not extracted_text:
        print("No text extracted from the PDF.")
        return

    # Truncate or split the text if it's too long for the API's limit
    max_length = 5000  # Set a reasonable character limit for the TTS
    if len(extracted_text) > max_length:
        # Trim the text if necessary
        extracted_text = extracted_text[:max_length]

    # Convert the extracted text to speech
    print("Converting text to speech...")
    text_to_speech(extracted_text, output_audio)


if __name__ == "__main__":
    main()
