from pathlib import Path
from openai import OpenAI
client = OpenAI()

speech_file_path = Path(__file__).parent / "speech.mp3"


def generate_speech(text):
    # Ensure the text is within the API's limit
    if len(text) > 4096:
        raise ValueError("Text exceeds 4096 characters limit")

    # Make the request to OpenAI's TTS API
    response = client.audio.speech.create(
      model="tts-1-hd",
      voice="nova",
      input=text
    )

    response.stream_to_file(speech_file_path)

    # Save the audio output to a file

#        audio_file.write(response["data"])

#    print("Audio saved as output_audio.wav")

# Example: A large block of text (under 4096 characters)
large_text = """
Chapter 1: The Shopping Trip Interrupted
I never thought I'd say this, but being dead has done wonders for my complexion.
"What do you think of this one?" Celeste held up a slinky black dress that probably cost more than my monthly rent. Pre-vampire me would have balked at the price tag, but apparently, when you're immortal, you develop expensive tastes. Who knew?
"I think it screams 'I vant to suck your blood,'" I quipped, affecting my best Dracula accent. "Perfect for our next Vampires Anonymous meeting."
Celeste rolled her eyes, a move she'd perfected over her centuries of undead existence. "Samantha, darling, we're vampires, not walking clichés. Besides, you need to update your wardrobe. You can't fight crime in last season's boots."
"Watch me," I retorted, but I was already eyeing a pair of stilettos that looked like they could double as weapons. Hey, a girl needs options when chasing down perps, supernatural or otherwise.
Just as I was about to cave and try on the shoes (for purely professional reasons, of course), my phone buzzed. The Imperial March ringtone told me it was work. Because nothing says “your boss is calling” like Darth Vader's theme song.
"Nightshade," I answered, trying to sound like I hadn't just been contemplating dropping a month's salary on footwear.
"Sam, we've got a situation." Mark's voice was tense, which immediately set off my detective spidey-senses. Or would that be vampire-senses now? Note to self: work on superhero branding later.
"What kind of situation? Did the coffee machine break down again? Because I told you, that's a job for S.W.A.T., not Homicide."
"Very funny," Mark deadpanned. "We've got a body. It's … It's bad, Sam. Really bad. Third one this month with the same M.O."
I felt my undead heart sink. So much for retail therapy. "Pick me up on your way to the crime scene at the corner of Sycamore and Main. I'll be there in ten."
Hanging up, I turned to Celeste, who was already holding out a bag with my new shoes. At my raised eyebrow, she shrugged. "What? Even crime-fighting vampires need to accessorize."
I couldn't argue with that logic. Grabbing the bag, I headed for the exit, my mind already shifting into detective mode. Another brutal murder, the third this month. Whatever was going on, I had a feeling it was going to be a long night.
But hey, at least I had new shoes. A girl has to look her best when diving into a bloody mystery, right? Who says you can't solve crimes and slay all day? This vampire detective was ready to sink her fangs into a new case.
Little did I know, this one was going to bite back. Hard.

"""

# Generate the speech
generate_speech(large_text)
