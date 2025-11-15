import cv2
import mediapipe as mp
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"   # NanoMQ broker
MQTT_TOPIC = "people/count"

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

client = mqtt.Client()
client.connect(MQTT_BROKER, 1883, 60)

prev_count = -1
cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    count = 1 if results.pose_landmarks else 0   # simple 1-person example

    if count != prev_count:
        print("Publishing count:", count)
        client.publish(MQTT_TOPIC, str(count))
        prev_count = count

    cv2.imshow("Camera - Person Counter", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
