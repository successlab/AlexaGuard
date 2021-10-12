import speech_recognition as sr
import requests
from pydub import AudioSegment

url = 'https://tinytts.amazon.com/3/2d9d4a47-f525-11eb-a3c5-6d3b35577df3-1e14ca/17/1628168959273/fc3aa003dec71b81cd950a04244885beb7019ef168a8f1790a5d43c088455429/resource.mp3'
req = requests.get(url, allow_redirects=True)

open('audio.mp3', 'wb').write(req.content)

sound = AudioSegment.from_mp3("audio.mp3")
sound.export("audio.wav", format="wav")

with sr.AudioFile('audio.wav') as source:
    r = sr.Recognizer()
    audio_data = r.record(source)
    # recognize (convert from speech to text)
    text = r.recognize_google(audio_data)
    print(text)