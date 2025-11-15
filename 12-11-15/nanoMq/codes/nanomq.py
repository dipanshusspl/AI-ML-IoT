import paho.mqtt.client as mqtt
import time

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "anjali/test"

def on_connect(client, userdata, flags, rc, properties=None):
    print("✅ Connected to HiveMQ Broker!")
    client.subscribe(TOPIC)
    # Publish after successful connection
    client.publish(TOPIC, "Hello again from Anjali 🚀")

def on_message(client, userdata, msg):
    print(f"📩 {msg.payload.decode()}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n👋 Disconnecting from broker...")
    client.loop_stop()
    client.disconnect()
    print("✅ Disconnected cleanly!")