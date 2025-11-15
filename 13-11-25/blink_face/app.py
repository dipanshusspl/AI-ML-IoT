from flask import Flask, render_template, request, jsonify
import cv2
import mediapipe as mp
import numpy as np
import base64

app = Flask(__name__)

mp_face_mesh = mp.solutions.face_mesh
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

def eye_aspect_ratio(landmarks, eye_points):
    # Use normalized coordinates (0–1) directly
    v1 = np.linalg.norm(np.array(landmarks[eye_points[1]]) - np.array(landmarks[eye_points[5]]))
    v2 = np.linalg.norm(np.array(landmarks[eye_points[2]]) - np.array(landmarks[4]))
    h  = np.linalg.norm(np.array(landmarks[eye_points[0]]) - np.array(landmarks[eye_points[3]]))
    ear = (v1 + v2) / (2.0 * h)
    return ear



def detect_blink(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, _ = frame.shape
    with mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5) as face_mesh:
        results = face_mesh.process(rgb)
        if not results.multi_face_landmarks:
            return None
        face_landmarks = results.multi_face_landmarks[0]
        landmarks = [(lm.x * w, lm.y * h) for lm in face_landmarks.landmark]
        left_ear = eye_aspect_ratio(landmarks, LEFT_EYE)
        right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE)
        ear = (left_ear + right_ear) / 2.0
        return ear

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    image_data = data['image']
    image_data = image_data.split(',')[1]
    image_bytes = base64.b64decode(image_data)
    np_arr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    ear = detect_blink(frame)
    print("EAR value:", ear)
    if ear is None:
        return jsonify({"status": "no_face"})

    if ear < 0.25:
        return jsonify({"status": "blink"})
    else:
        return jsonify({"status": "open"})

if __name__ == '__main__':
    app.run(debug=True)
