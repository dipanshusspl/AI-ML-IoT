import cv2
import mediapipe as mp
import pyttsx3
import threading

# Initialize MediaPipe Hands and TTS
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
engine = pyttsx3.init()

# Speak function (runs in a thread)
def speak(text):
    def _speak():
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=_speak, daemon=True).start()

# Gesture detection logic
def detect_gesture(landmarks):
    tips = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb
    if landmarks[tips[0]].x < landmarks[tips[0]-1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    for tip in tips[1:]:
        if landmarks[tip].y < landmarks[tip-2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    total = fingers.count(1)

    if total == 0:
        return "Fist"
    elif total == 1 and fingers[1] == 1:
        return "Thumbs Up"
    elif total == 2 and fingers[1] == 1 and fingers[2] == 1:
        return "Victory"
    elif total == 5:
        return "Palm Open"
    elif total == 3:
        return "OK"
    elif total == 4:
        return "Loose"
    else:
        return "Unknown"

# Camera setup
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
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Speak only if gesture changes
                if gesture != last_gesture and gesture != "Unknown":
                    print(f"Detected gesture: {gesture}")
                    speak(gesture)
                    last_gesture = gesture

        cv2.imshow("Hand Gesture with Voice", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
