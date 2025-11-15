import cv2
from deepface import DeepFace

# Open the webcam (0 = default webcam, or replace with video URL)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Analyze the frame for emotion
    try:
        result = DeepFace.analyze(frame, actions=['emotion','gender','age'], enforce_detection=False)

        # Extract the emotion
        emotion = result[0]['dominant_emotion']

        # Display on frame
        cv2.putText(frame, f"Emotion: {emotion}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    except Exception as e:
        print("Error:", e)

    # Show the frame
    cv2.imshow('Live Emotion Detection', frame)

    # Break loop with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()