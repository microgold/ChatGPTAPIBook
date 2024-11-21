import re
import os
from openai import OpenAI
import PyPDF2
from pydub import AudioSegment


def extract_text_from_pdf(pdf_path):
    """ Extracts text from a PDF file. """
    text = ''
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            page_text = page.extract_text() if page.extract_text() else ''
            text += page_text
    return text


def text_to_speech(text, filename):
    """ Converts text to speech using OpenAI's API and saves it to an MP3 file. """
    client = OpenAI()
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    response.stream_to_file(filename)


def split_text(text, chunk_size=1000):
    """
    Yields chunks of text with the specified number of characters, ensuring words are not cut off.
    """
    words = re.split(r'(\s+)', text)  # Split by whitespace but keep the spaces
    current_chunk = ""
    current_length = 0

    for word in words:
        if current_length + len(word) > chunk_size:
            yield current_chunk.strip()
            current_chunk = word
            current_length = len(word)
        else:
            current_chunk += word
            current_length += len(word)

    if current_chunk:  # Yield any remaining text
        yield current_chunk.strip()


def merge_audio(files, output_filename):
    """ Merges multiple MP3 files into a single file. """
    combined = AudioSegment.empty()
    for file in files:
        print("Merging file: ", file)
        audio = AudioSegment.from_mp3(file)
        combined += audio
    combined.export(output_filename, format="mp3")
    print(f"Merged audio file created: {output_filename}")


def main():
    pdf_path = "2city12p.pdf"  # Specify your PDF file path here
    temp_audio_files = []

    # Extract text from the PDF
    print("Extracting text from PDF...")
    extracted_text = extract_text_from_pdf(pdf_path)
    if not extracted_text:
        print("No text extracted from the PDF.")
        return

    # Convert the extracted text to speech in chunks
    print("Converting text to speech in chunks...")
    for i, text_chunk in enumerate(split_text(extracted_text)):
        filename = f"part_{i+1}.mp3"
        print(f"Converting chunk {i+1} to speech...")
        temp_audio_files.append(filename)
        text_to_speech(text_chunk, filename)
        if i == 2:
            break

    # Merge all audio files into one
    if temp_audio_files:
        print("Merging audio files...")
        merge_audio(temp_audio_files, "final_output.mp3")

    # Clean up temporary files
    for file in temp_audio_files:
        os.remove(file)
        print(f"Removed temporary file: {file}")


if __name__ == "__main__":
    main()
