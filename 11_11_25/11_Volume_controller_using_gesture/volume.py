import cv2
import mediapipe as mp
import numpy as np
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# -----------------------------
# 🎚️ Initialize Audio Interface
# -----------------------------
devices = AudioUtilities.GetAllDevices()
speakers = None

# Try default speakers safely
for dev in devices:
    if "Speaker" in dev.FriendlyName or "Output" in dev.FriendlyName:
        speakers = dev
        break

# Fallback if not found
if speakers is None:
    speakers = AudioUtilities.GetSpeakers()

interface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Get min and max volume range (in dB)
min_vol, max_vol, _ = volume.GetVolumeRange()

# -----------------------------
# 🖐️ Initialize Mediapipe Hands
# -----------------------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# -----------------------------
# 🎥 Webcam Setup
# -----------------------------
cap = cv2.VideoCapture(0)

# ROI area (only works inside this box)
x1_roi, y1_roi, x2_roi, y2_roi = 100, 100, 500, 400

# -----------------------------
# 🧠 Main Loop
# -----------------------------
while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    # Draw control zone
    cv2.rectangle(frame, (x1_roi, y1_roi), (x2_roi, y2_roi), (0, 255, 0), 2)
    cv2.putText(frame, "Volume Control Zone", (x1_roi + 10, y1_roi - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Extract thumb and index tip
            x_thumb = int(hand_landmarks.landmark[4].x * w)
            y_thumb = int(hand_landmarks.landmark[4].y * h)
            x_index = int(hand_landmarks.landmark[8].x * w)
            y_index = int(hand_landmarks.landmark[8].y * h)

            # Check if within ROI
            if x1_roi < x_index < x2_roi and y1_roi < y_index < y2_roi:
                # Draw line and circles
                cv2.circle(frame, (x_thumb, y_thumb), 8, (255, 0, 0), -1)
                cv2.circle(frame, (x_index, y_index), 8, (255, 0, 0), -1)
                cv2.line(frame, (x_thumb, y_thumb), (x_index, y_index), (255, 255, 0), 3)

                # Distance between fingers
                length = math.hypot(x_index - x_thumb, y_index - y_thumb)

                # Map distance -> volume level
                vol = np.interp(length, [20, 200], [min_vol, max_vol])
                volume.SetMasterVolumeLevel(vol, None)

                # Draw volume bar
                vol_bar = np.interp(length, [20, 200], [400, 150])
                cv2.rectangle(frame, (50, 150), (85, 400), (0, 255, 0), 3)
                cv2.rectangle(frame, (50, int(vol_bar)), (85, 400), (0, 255, 0), -1)

                # Show percentage
                vol_perc = np.interp(length, [20, 200], [0, 100])
                cv2.putText(frame, f'Vol: {int(vol_perc)} %', (40, 450),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)

    cv2.imshow("🎛️ Hand Volume Controller", frame)

    # Exit on ESC key
    if cv2.waitKey(1) & 0xFF == 27:
        break

# -----------------------------
# 🔚 Cleanup
# -----------------------------
cap.release()
cv2.destroyAllWindows()
