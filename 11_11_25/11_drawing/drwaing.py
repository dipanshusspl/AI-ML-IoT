import cv2
import numpy as np
import mediapipe as mp

# Initialize MediaPipe Hand
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Create a blank canvas for drawing
canvas = None

# Default color: Blue
draw_color = (255, 0, 0)
brush_thickness = 8

# HSV color ranges for Red, Green, Blue markers (you can adjust these)
color_ranges = {
    'red':   ((0, 120, 70), (10, 255, 255)),
    'green': ((36, 50, 70), (89, 255, 255)),
    'blue':  ((94, 80, 2), (126, 255, 255))
}

# Webcam
cap = cv2.VideoCapture(0)

# Previous finger position
xp, yp = 0, 0

while True:
    success, frame = cap.read()
    if not success:
        break
    frame = cv2.flip(frame, 1)

    if canvas is None:
        canvas = np.zeros_like(frame)

    # Convert to RGB for MediaPipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    # --- Detect Color Object (to choose color) ---
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    for color_name, (lower, upper) in color_ranges.items():
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours and cv2.contourArea(max(contours, key=cv2.contourArea)) > 1500:
            draw_color = {
                'red': (0, 0, 255),
                'green': (0, 255, 0),
                'blue': (255, 0, 0)
            }[color_name]
            cv2.putText(frame, f'Color Selected: {color_name.upper()}', (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, draw_color, 3)

    # --- Hand tracking and drawing ---
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, _ = frame.shape
                lm_list.append((int(lm.x * w), int(lm.y * h)))

            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Index finger tip (landmark 8)
            x1, y1 = lm_list[8]

            # Clear canvas gesture – all fingers open
            fingers_up = [lm_list[8][1] < lm_list[6][1],
                          lm_list[12][1] < lm_list[10][1],
                          lm_list[16][1] < lm_list[14][1],
                          lm_list[20][1] < lm_list[18][1]]
            if all(fingers_up):
                canvas = np.zeros_like(frame)
                cv2.putText(frame, 'Canvas Cleared!', (100, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                xp, yp = 0, 0
            else:
                if xp == 0 and yp == 0:
                    xp, yp = x1, y1
                cv2.line(canvas, (xp, yp), (x1, y1), draw_color, brush_thickness)
                xp, yp = x1, y1
    else:
        xp, yp = 0, 0  # reset if hand not detected

    # Combine frame + canvas
    frame = cv2.addWeighted(frame, 0.7, canvas, 0.3, 0)
    cv2.imshow("🎨 Air Drawing", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
