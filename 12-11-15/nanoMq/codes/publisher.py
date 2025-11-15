import time
import paho.mqtt.client as mqtt
import random

# Create client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("localhost", 1883, 60)

topic = "iot/sensor/data"

print("🚀 Publisher started. Sending sensor data every 2 seconds...")
try:
    while True:
        temperature = round(random.uniform(20, 35), 2)
        humidity = round(random.uniform(40, 80), 2)
        payload = f"Temperature: {temperature}°C, Humidity: {humidity}%"
        client.publish(topic, payload)
        print(f"📤 Sent → {topic}: {payload}")
        time.sleep(2)
except KeyboardInterrupt:
    print("\n🛑 Publisher stopped.")
    client.disconnect()
