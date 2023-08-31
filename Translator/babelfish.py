# pip install sounddevice numpy pydub pygame gtts wavio

from io import BytesIO
import json
import os
import time
import tkinter as tk
from tkinter import ttk
from dotenv import load_dotenv
import openai
import requests
from tkinter import messagebox
import sounddevice as sd
import numpy as np
from pydub import AudioSegment
from pygame import mixer
from gtts import gTTS
import pygame
import wavio

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
openai.api_key = key


def set_wait_cursor():
    submit_btn.config(cursor="watch")
    app.update_idletasks()  # Force an immediate update of the window
    time.sleep(2)  # Simulate some long operation


def set_normal_cursor():
    submit_btn.config(cursor="")
    
def translate(language1, language2, text):
    prompt = f"Translate the following from {language1} to {language2}: {text}"
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
    
    chatGPTTranslation = response["choices"][0]["message"]["content"]
    
    # Parse JSON string to a Python dictionary
    parsed_json = json.loads(chatGPTTranslation)

    # Extract value associated with the key "text"
    chatGPTTranslation = parsed_json["text"]
    print(chatGPTTranslation)
    return chatGPTTranslation

def text_to_speech(translated_text, language):
    tts = gTTS(translated_text, lang= languages[language], slow=False)
    tts.save('C:\\temp\\hello.mp3')
    # 5. Convert Translated Text to Speech
    # Placeholder for a TTS service (like Google Cloud TTS).
   

    # Initialize pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load('C:\\temp\\hello.mp3')
    pygame.mixer.music.play()
    

# If you want to keep the program running until the audio is done playing:
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)  # This will wait and let the music play.
        
    # close the mp3 file
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    os.remove('C:\\temp\\hello.mp3')
    
def submit():
  # 1. Capture Audio
    set_wait_cursor()
    # Indicate start of recording
    label_recording.config(text="Recording...", bg="red")
    app.update()
    duration = 10  # seconds
    samplerate = 44100
    audio = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=2, dtype='int16')
    sd.wait()
    
    label_recording.config(text="Finished Recording", bg="green")
    app.update()


    set_normal_cursor()

    # Save the numpy array to a WAV file using wavio
    wav_path = "c:\\temp\\myrecording.wav"
    wavio.write(wav_path, audio, samplerate, sampwidth=2)

    # Load the WAV file into an AudioSegment
    audio_segment = AudioSegment.from_wav(wav_path)

    # Save the audio segment as MP3
    # audio_segment.export("c:\\temp\\myrecording.wav", format="mp3")
    set_normal_cursor()
    

    # 3. Transcribe the Audio
    # This is just a placeholder, you'll have to replace with the actual API call to OpenAI or other transcription services.
    audio_file= open("c:\\temp\\myrecording.wav", "rb")
    transcription = openai.Audio.transcribe(model = 'whisper-1', file = audio_file)
    audio_file.close()
    
    print(f'{transcription}\n\n')
    resulting_translation = translate(combo1.get(), combo2.get(), transcription)
    text_to_speech(resulting_translation, combo2.get())
    
# create a dictionary to store the languages and their corresponding codes
languages = {'English': 'en', 'Spanish': 'es', 'French': 'fr', 'German': 'de', 'Russian': 'ru'}




app = tk.Tk()
app.title("Babel Fish")

# Label and ComboBox for the first animal
label1 = ttk.Label(app, text="Select Known Language")
label1.grid(column=0, row=0, padx=10, pady=5)
combo1 = ttk.Combobox(app, values=["English", "Spanish", "French", "German", "Russian"])
combo1.grid(column=1, row=0, padx=10, pady=5)
combo1.set("English")

# Label and ComboBox for the second animal
label2 = ttk.Label(app, text="Select Translated Language:")
label2.grid(column=0, row=1, padx=10, pady=5)
combo2 = ttk.Combobox(
    app, values=["English", "Spanish", "French", "German", "Russian"])
combo2.grid(column=1, row=1, padx=10, pady=5)
combo2.set("Spanish")

# Button to submit the text to translate
submit_btn = ttk.Button(app, text="Record", command=submit)
submit_btn.grid(column=1, row=3, padx=10, pady=20)
label_recording = tk.Label(app, text="Click the button to start recording", bg="lightgray", fg="white", width=60, height=2)
label_recording.grid(column=1, row=8, padx=10, pady=20)

app.mainloop()