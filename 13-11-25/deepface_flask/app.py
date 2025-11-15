from flask import Flask, render_template, request, jsonify
from deepface import DeepFace
import cv2
import numpy as np
import base64
import os

app = Flask(__name__)

# Path to your known image
KNOWN_FACE_PATH = "known_face.jpg"

# Preload known face representation
print("Encoding known face...")
known_embedding = DeepFace.represent(img_path=KNOWN_FACE_PATH, model_name='VGG-Face', enforce_detection=False)[0]['embedding']
print("Known face encoded successfully.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    image_data = data['image']

    # Decode base64 image from browser
    image_data = image_data.split(',')[1]
    image_bytes = base64.b64decode(image_data)
    np_arr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    try:
        # Get embedding for captured frame
        capture_embedding = DeepFace.represent(img_path=frame, model_name='VGG-Face', enforce_detection=False)[0]['embedding']

        # Compute similarity
        distance = DeepFace.verify(img1_path=KNOWN_FACE_PATH, img2_path=frame, model_name='VGG-Face', enforce_detection=False)['distance']

        # Threshold ~0.4–0.6 works depending on model
        if distance < 0.5:
            result = {"match": True, "distance": distance}
        else:
            result = {"match": False, "distance": distance}

    except Exception as e:
        result = {"error": str(e)}

    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)