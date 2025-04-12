# modules/tts_handler.py

import pyttsx3

# Initialize the speech engine only once
engine = pyttsx3.init()

def speak(text):
    """Speak the given text aloud"""
    engine.say(text)
    engine.runAndWait()