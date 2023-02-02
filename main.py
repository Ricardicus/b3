#%%
from pydub import AudioSegment
from pydub.playback import play
import speech_recognition as sr
import openai
import requests
import json
import os


r = sr.Recognizer()
r.pause_threshold = 1.0
r.energy_threshold = 1000


def play_mp3(path):
    sound = AudioSegment.from_mp3(path)
    play(sound)


def transcribe_audio(data):
    try:
        transcription = r.recognize_whisper(data, model="base", language="english", translate=False)
        return transcription
    except sr.UnknownValueError:
        print("Speech was unintelligible")
    except:
        print("Speech recognition failed")


def listen():
    while True:
        with sr.Microphone() as mic:
            data = r.listen(mic, phrase_time_limit=5)

            return data


def gpt(prompt):
    response = openai.Completion.create(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="text-davinci-003",
        prompt=prompt,
        temperature=1.0,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    return response.choices[0].text


def get_voice_id():
    response = requests.request(
        "GET", 
        "https://api.elevenlabs.io/v1/voices", 
        headers = {
            'xi-api-key': os.getenv("ELEVENLABS_API_KEY"),
        },
    )

    return response.json()["voices"][0]["voice_id"]



def text_to_speech(text, voice_id, save_path='response.mp3'):
    response = requests.request(
        "POST", 
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}", 
        headers={
            'accept': 'audio/mpeg',
            'xi-api-key': os.getenv("ELEVENLABS_API_KEY"),
        }, 
        data=json.dumps({ "text": text })
    )

    with open(save_path, 'wb') as f:
        f.write(response.content)



voice_id = get_voice_id()

prompt = f"""The following is a group chat conversation with 'AI', a rogue AI. The AI is benovelent, nihilistic, and funny.
If the AI doesn't know the answer to a question, it makes something up on the spot. 
The AI responds concisely. 

"""

while True:
    # capture microphone audio until silence
    print("Listening...")
    audio_data = listen()

    # use whisper to transcribe audio data
    print("Transcribing audio...")
    transcription = transcribe_audio(audio_data)
    print(f"Heard: {transcription}")

    # add the spoken text to the prompt
    prompt += f"Person: {transcription}\nAI:"

    # get response text from openai api
    response = gpt(prompt)
    print(f"Response: {response}")

    # add ai response to prompt, so we can have a continuous conversation
    prompt += f"{response}\n"

    # let evelenlabs api speak
    print("Waiting for speech synthesis...")
    text_to_speech(response, voice_id, save_path="response.mp3")

    # play response audio
    play_mp3("response.mp3")
