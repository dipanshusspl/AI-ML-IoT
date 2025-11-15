import cv2
import numpy as np
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Start webcam
cap = cv2.VideoCapture(0)

# Initialize MediaPipe Face Mesh
with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as face_mesh:

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Flip and convert color
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(rgb_frame)

        if result.multi_face_landmarks:
            h, w, _ = frame.shape
            face_landmarks = result.multi_face_landmarks[0]

            # 3D model points of standard facial landmarks
            landmarks = face_landmarks.landmark

            # Key facial points for pose estimation (indices from MediaPipe docs)
            image_points = np.array([
                (landmarks[1].x * w, landmarks[1].y * h),     # Nose tip
                (landmarks[33].x * w, landmarks[33].y * h),   # Left eye inner corner
                (landmarks[263].x * w, landmarks[263].y * h), # Right eye inner corner
                (landmarks[61].x * w, landmarks[61].y * h),   # Left mouth corner
                (landmarks[291].x * w, landmarks[291].y * h), # Right mouth corner
                (landmarks[199].x * w, landmarks[199].y * h)  # Chin
            ], dtype="double")

            # 3D model points in real-world coordinates (approx.)
            model_points = np.array([
                (0.0, 0.0, 0.0),         # Nose tip
                (-30.0, -125.0, -30.0),  # Left eye
                (30.0, -125.0, -30.0),   # Right eye
                (-60.0, -225.0, -30.0),  # Left mouth
                (60.0, -225.0, -30.0),   # Right mouth
                (0.0, -330.0, -65.0)     # Chin
            ])

            # Camera matrix (approximate)
            focal_length = w
            center = (w / 2, h / 2)
            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]
            ], dtype="double")

            dist_coeffs = np.zeros((4, 1))  # Assume no lens distortion

            # SolvePnP gives rotation and translation vectors
            success, rotation_vector, translation_vector = cv2.solvePnP(
                model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
            )

            # Convert rotation vector to rotation matrix
            rmat, _ = cv2.Rodrigues(rotation_vector)

            # Extract Euler angles (yaw, pitch, roll)
            sy = np.sqrt(rmat[0, 0] ** 2 + rmat[1, 0] ** 2)
            singular = sy < 1e-6

            if not singular:
                pitch = np.arctan2(-rmat[2, 0], sy)
                yaw = np.arctan2(rmat[1, 0], rmat[0, 0])
                roll = np.arctan2(rmat[2, 1], rmat[2, 2])
            else:
                pitch = np.arctan2(-rmat[2, 0], sy)
                yaw = 0
                roll = np.arctan2(-rmat[1, 2], rmat[1, 1])

            # Convert to degrees
            pitch, yaw, roll = np.degrees([pitch, yaw, roll])

            # Interpretation
            direction = ""
            if yaw > 15:
                direction = "Looking Right"
            elif yaw < -15:
                direction = "Looking Left"
            elif pitch > 10:
                direction = "Looking Down"
            elif pitch < -10:
                direction = "Looking Up"
            else:
                direction = "Facing Center"

            # Display angles and direction
            cv2.putText(frame, f"Pitch: {pitch:.2f}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
            cv2.putText(frame, f"Yaw: {yaw:.2f}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
            cv2.putText(frame, f"Direction: {direction}", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

            # Draw landmarks
            mp_drawing.draw_landmarks(frame, face_landmarks, mp_face_mesh.FACEMESH_TESSELATION,
                                      mp_drawing.DrawingSpec(color=(0,255,255), thickness=1, circle_radius=1),
                                      mp_drawing.DrawingSpec(color=(255,0,0), thickness=1))

        cv2.imshow("Head Pose Estimation", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()