import cv2
import datetime

# Initialize webcam (0 = default camera)
cam = cv2.VideoCapture(0)

# Set video frame width and height (optional)
cam.set(3, 1280)  # width
cam.set(4, 720)   # height

# Define video codec and create VideoWriter object (initialized later)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = None
recording = False

print("Press 'r' to start/stop recording, 'q' to quit.")

while True:
    ret, frame = cam.read()
    if not ret:
        print("Failed to grab frame!")
        break

    # Show current time on frame
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, timestamp, (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # If recording, save frame to video file
    if recording and out is not None:
        out.write(frame)
        cv2.putText(frame, "REC", (20, 100),
                    cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 255), 3)

    # Show the live camera window
    cv2.imshow("Camera Feed", frame)

    # Keyboard controls
    key = cv2.waitKey(1) & 0xFF
    if key == ord('r'):
        if not recording:
            filename = datetime.datetime.now().strftime("record_%Y%m%d_%H%M%S.avi")
            out = cv2.VideoWriter(filename, fourcc, 20.0, (1280, 720))
            recording = True
            print(f"🎥 Recording started: {filename}")
        else:
            recording = False
            out.release()
            out = None
            print("🛑 Recording stopped.")
    elif key == ord('q'):
        print("Exiting...")
        break

# Cleanup
cam.release()
if out is not None:
    out.release()
cv2.destroyAllWindows()
