from gtts import gTTS
import uuid
import os

def text_to_audio(text):
    filename=f"audio_{uuid.uuid4()}.mp3"

    tts=gTTS(text=text, lang='en', slow=True)
    tts.save(filename)
    return filename

if __name__ == "__main__":
    text = input("Enter text to convert to audio: ")
    audio_file = text_to_audio(text)
    print(f"Audio file created: {audio_file}")