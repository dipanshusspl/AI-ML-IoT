import cv2
import mediapipe as mp
import pyttsx3
import threading

# Initialize MediaPipe Hands and TTS
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
engine = pyttsx3.init()

# Set speaking rate and voice
engine.setProperty('rate', 170)  # speed
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # choose voice

# Speak in a background thread
def speak(text):
    def _speak():
        print(f"[VOICE]: {text}")
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=_speak, daemon=True).start()

# Gesture detection logic
def detect_gesture(landmarks):
    tips = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb (x-axis)
    if landmarks[tips[0]].x < landmarks[tips[0]-1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other 4 fingers (y-axis)
    for tip in tips[1:]:
        if landmarks[tip].y < landmarks[tip-2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    total = fingers.count(1)

    # 🏏 Cricket gesture rules
    if total == 1 and fingers[1] == 1:
        return "OUT"            # Index finger up
    elif total == 2 and fingers[1] == 1 and fingers[2] == 1:
        return "Two Bouncers"   # Index + middle
    elif total == 1 and fingers[0] == 1:
        return "Good Ball"      # Thumbs up
    elif total == 0:
        return "Dead Ball"      # Closed fist
    elif total == 5:
        return "Wide Ball"      # All fingers open
    else:
        return "Unknown"

# Open camera
cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
) as hands:
    last_gesture = ""

    while True:
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                gesture = detect_gesture(hand_landmarks.landmark)

                cv2.putText(frame, gesture, (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

                # Speak only when gesture changes
                if gesture != last_gesture and gesture != "Unknown":
                    speak(gesture)
                    last_gesture = gesture

        cv2.imshow("🏏 Cricket Gesture Umpire", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
