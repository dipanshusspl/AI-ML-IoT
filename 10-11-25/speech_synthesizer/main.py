from TTS.api import TTS
import os

# Load pretrained multilingual TTS model
tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=True, gpu=False)

# Folder with your recorded voice clips
voice_folder = "voices"
voice_files = [os.path.join(voice_folder, f) for f in os.listdir(voice_folder) if f.endswith(".wav")]

# Text to generate speech for
text = "Hello! This is a rough imitation of my recorded voice. It’s not exact, but sounds somewhat similar."

# Output audio file
output_path = "rough_clone_output.wav"

# Generate speech (voice adapted)
tts.tts_to_file(text=text, speaker_wav=voice_files, language="en", file_path=output_path)

print(f"✅ Done! Speech saved at {output_path}")
