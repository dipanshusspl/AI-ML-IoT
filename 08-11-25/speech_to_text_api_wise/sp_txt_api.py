
import speech_recognition as sr
import requests
import re
from gtts import gTTS
import os
import playsound

API_URL = "http://192.168.1.21/handleChatbotDuesReq/"

def speak(text):
    """Convert text to speech and play it"""
    print("💬 BOT:", text)
    tts = gTTS(text=text, lang='hi')  # 'hi' for Hindi voice, use 'en' for English
    filename = "response.mp3"
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)

def clean_pin(text):
    return re.sub(r'\D', '', text)

def listen_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n🎤 Speak your property PIN now...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print("🗣️ You said:", text)
        return text.strip()
    except sr.UnknownValueError:
        speak("Sorry, I could not understand your voice.")
        return None
    except sr.RequestError:
        speak("Speech recognition service is unavailable.")
        return None

def check_dues(pin):
    try:
        response = requests.post(API_URL, json={"pin": pin}, timeout=5)
        return response.json()
    except Exception as e:
        print("⚠️ Error:", e)
        return {"status": "failed", "msg": "Connection error"}

def main():
    speak("Please say your property PIN.")
    heard = listen_audio()
    if not heard:
        return

    pin = clean_pin(heard)
    if not pin:
        speak("I could not find any numbers in your speech.")
        return

    speak(f"Checking dues for PIN {pin}. Please wait.")
    result = check_dues(pin)

    if result.get("status") == "success":
        msg = f"Property found. Owner name is {result.get('owner_name')}. You can pay using the link sent."
    else:
        msg = f"{result.get('msg')}"

    speak(msg)

if __name__ == "__main__":
    main()
