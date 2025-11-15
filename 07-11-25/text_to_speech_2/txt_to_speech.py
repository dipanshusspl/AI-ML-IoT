import pyttsx3

# Initialize synthesizer
engine = pyttsx3.init()

# Choose a voice (optional)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # 0=male, 1=female (depends on system)

# Set speaking rate
engine.setProperty('rate', 150)

# Input text
text = "Hello, this is a simple text to speech synthesizer built in Python."

# Speak the text
engine.say(text)
engine.runAndWait()

# Save to audio file
engine.save_to_file(text, 'output_audio.mp3')
engine.runAndWait()
