import time

from groq import Groq
from openai import OpenAI
import speech_recognition as sr
import pyttsx3 as tts
import re
from faster_whisper import WhisperModel
import os

wake_word = "luna"
groq_client = Groq(api_key='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')
openai_client = OpenAI(api_key='sk-proj-dzy1wEAwtRVbQyQNlU4BT3BlbkFJJxth58Z4ZT8Nc6ODvxt2')

r = sr.Recognizer()
source = sr.Microphone()

num_cores = os.cpu_count()
whisper_size = 'base'

speaker = tts.init()
speaker.setProperty('rate', 150)


def start_listening():
    with source as s:
        r.adjust_for_ambient_noise(s, duration=2)
    print("Listening..., say ", wake_word, "followed with prompt.\n")
    try:
        r.listen_in_background(source, callback)
    except sr.UnknownValueError:
        print("I don't understand what you say.")

    while True:
        time.sleep(0.1)

def extract_prompt(transcribed_text, wake_word):
    pattern = rf'\b{re.escape(wake_word)}[\s,.?!]*([A-Za-z0-9].*)'
    match = re.search(pattern, transcribed_text, re.IGNORECASE)

    if match:
        prompt = match.group(1).strip()
        return prompt
    else:
        return None

def callback(recognizer, audio):
    prompt_text = recognizer.recognize_google(audio, language='de-De')
    clean_prompt = extract_prompt(prompt_text, wake_word)
    print(prompt_text)
    if clean_prompt:
        print(f'USER: {clean_prompt}')
        call = function_call(clean_prompt)
        print(call)

        response = groq_prompt(prompt=clean_prompt)
        speaker.say(response)
        speaker.runAndWait()
        speaker.stop()
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
    chat_completion = groq_client.chat.completions.create(messages=function_convo, model='llama3-70b-8192')
    response = chat_completion.choices[0].message.content

    return response


start_listening()
