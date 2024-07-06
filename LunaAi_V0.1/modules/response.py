import time

from groq import Groq
from openai import OpenAI
import speech_recognition as sr
import pyttsx3 as tts
import re
from faster_whisper import WhisperModel
import os

'''
This part of the Assistant is for listening & 
identifying the wanted task. After giving the task to the Controller & Operating it, 
the Assistant give's you the reply here. 
listening & response will be apart in V0.2
'''

# Wake word. Will be edited to Wake Words. So it can also be activated in a differnt context.
wake_word = "luna"

# You need groq API in this Version. In the Future Luna will be a AI Assistant running through an local API call with Ollama.
groq_api = open('Y:\\Tim NAS\\API keys\\groq.txt', 'r').read().strip()
groq_client = Groq(api_key= groq_api)

# initializing recognizer and microphone access from you're computer or laptop
r = sr.Recognizer()
source = sr.Microphone()

num_cores = os.cpu_count()
whisper_size = 'base'

speaker = tts.init()
speaker.setProperty('rate', 150)


"""
Activates the listening throw your Mic & waits until it recognizes the Wake Word
"""
def start_listening():
    with source as s:
        r.adjust_for_ambient_noise(s, duration=1)
    print("Listening..., say ", wake_word, "followed with prompt.\n")
    r.listen_in_background(source, callback)
    while True:
        time.sleep(0.1)

"""
Using the recognizer and a form of Regex to extract the prompt out of your Spoken sentence
:return prompt: gives the extracted prompt if identified
:return None: if the transcribed_text is not compatible with the pattern
"""
def extract_prompt(transcribed_text):
    pattern = rf'\b{re.escape(wake_word)}[\s,.?!]*([A-Za-z0-9].*)'
    match = re.search(pattern, transcribed_text, re.IGNORECASE)

    if match:
        prompt = match.group(1).strip()
        return prompt
    else:
        return None

def callback(recognizer, audio):
    try:
        prompt_text = recognizer.recognize_google(audio, language='de-De')
        clean_prompt = extract_prompt(prompt_text)
        print(prompt_text)
        if clean_prompt:
            print(f'USER: {clean_prompt}')
            call = function_call(clean_prompt)
            print(call)

            response = groq_prompt(prompt=clean_prompt)
            speaker.say(response)
            speaker.runAndWait()
            speaker.stop()
    except sr.UnknownValueError:
        print("I couldnt understand what you said!")

#
def groq_prompt(prompt):
    convo = [{'role':'user', 'content':prompt}]
    chat_completion = groq_client.chat.completions.create(messages = convo, model='llama3-70b-8192')
    response = chat_completion.choices[0].message.content

    return response

def function_call(prompt):
    sys_msg = (
        'You are an AI function calling model. You will determine whether to create a new Note,'
        'add a calendar event, add a task or calling no function is best for a voice assistant to respond'
        'to users prompt. You will respond with one selection for this list:'
        '["create note","add calendar","add task","None", "information", "skim notes", "smarthome interaction"] \n'
        'Do not respond with anything but the most logical selection from that list with no explanations. Format the'
        'function call name exactly as I listed.'
    )
    function_convo = [
        {'role':'system', 'content':sys_msg},
        {'role':'user', 'content':prompt}
    ]
    chat_completion = groq_client.chat.completions.create(messages=function_convo, model='llama3-8b-8192')
    response = chat_completion.choices[0].message.content

    return response


start_listening()
