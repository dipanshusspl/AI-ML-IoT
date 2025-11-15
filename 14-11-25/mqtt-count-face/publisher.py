import paho.mqtt.client as mqtt
import time

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("localhost", 1883, 60)

count = 0

print("🚀 Publisher started...")

while True:
    count += 1
    client.publish("topic/count", str(count))
    print(f"📤 Published count: {count}")
    time.sleep(3)  # send every 3 seconds
