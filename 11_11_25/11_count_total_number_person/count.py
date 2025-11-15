import cv2
import mediapipe as mp

# Initialize mediapipe
mp_pose = mp.solutions.pose
mp_face = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Start camera
cap = cv2.VideoCapture(0)

# Detection models
pose = mp_pose.Pose(min_detection_confidence=0.5)
face = mp_face.FaceDetection(min_detection_confidence=0.5)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Convert to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Run both detectors
    face_results = face.process(rgb)
    pose_results = pose.process(rgb)

    # Count detected faces (you can count poses similarly)
    person_count = 0
    if face_results.detections:
        person_count = len(face_results.detections)

    # Draw detection and show count
    if face_results.detections:
        for detection in face_results.detections:
            mp_drawing.draw_detection(frame, detection)

    cv2.putText(frame, f'Persons: {person_count}', (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

    cv2.imshow('Person Counter', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
