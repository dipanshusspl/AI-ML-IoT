from pydub import AudioSegment
import os

input_folder = "voices"
output_folder = "voices_wav"

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.endswith(".m4a"):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename.replace(".m4a", ".wav"))
        sound = AudioSegment.from_file(input_path, format="m4a")
        sound = sound.set_frame_rate(16000).set_channels(1)
        sound.export(output_path, format="wav")
        print(f"✅ Converted: {filename} → {output_path}")

print("🎧 All files converted successfully!")
