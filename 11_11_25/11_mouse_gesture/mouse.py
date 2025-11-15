import cv2
import mediapipe as mp
import pyautogui

# Initialize hand detector
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1)

# Get screen size
screen_w, screen_h = pyautogui.size()

# Start webcam
cap = cv2.VideoCapture(0)

# Track previous click state
clicking = False

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)  # mirror the frame
    h, w, _ = frame.shape

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Get index fingertip & thumb tip
            index_finger = hand_landmarks.landmark[8]  # index tip
            thumb = hand_landmarks.landmark[4]         # thumb tip

            # Convert to screen coordinates
            x = int(index_finger.x * w)
            y = int(index_finger.y * h)
            screen_x = screen_w / w * x
            screen_y = screen_h / h * y

            # Move mouse
            pyautogui.moveTo(screen_x, screen_y, duration=0.01)

            # Draw hand landmarks
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Calculate distance between thumb & index tip (for click gesture)
            thumb_x, thumb_y = int(thumb.x * w), int(thumb.y * h)
            distance = ((thumb_x - x)**2 + (thumb_y - y)**2) ** 0.5

            # Visual feedback circle
            cv2.circle(frame, (x, y), 10, (255, 0, 0), -1)

            # Click when fingers come close
            if distance < 30 and not clicking:
                clicking = True
                pyautogui.click()
                cv2.putText(frame, 'Click!', (x, y - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
            elif distance >= 40:
                clicking = False

    cv2.imshow("🖐️ Virtual Mouse", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key to quit
        break

cap.release()
cv2.destroyAllWindows()
