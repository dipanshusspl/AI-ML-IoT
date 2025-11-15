import cv2
from ultralytics import YOLO
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_TOPIC = "people/count"

# Load YOLOv8 model
model = YOLO("yolov8n.pt")   # nano version, fast on CPU

client = mqtt.Client()
client.connect(MQTT_BROKER, 1883, 60)

prev_count = -1
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO detection
    results = model(frame, verbose=False)

    person_count = 0

    for obj in results[0].boxes:
        cls = int(obj.cls[0])     # class ID
        if cls == 0:              # 0 = "person"
            person_count += 1
            # Draw bounding boxes
            x1, y1, x2, y2 = map(int, obj.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

    # Publish only when number changes
    if person_count != prev_count:
        print(f"Publishing count: {person_count}")
        client.publish(MQTT_TOPIC, str(person_count))
        prev_count = person_count

    # Display on screen
    cv2.putText(frame, f"People: {person_count}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

    cv2.imshow("Full Body Multi-Person Counter", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
