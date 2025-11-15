import paho.mqtt.client as mqtt

def on_message(client, userdata, message):
    print(f"[Subscriber 2] 📩 {message.payload.decode()}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("localhost", 1883, 60)
client.subscribe("iot/sensor/data")
client.on_message = on_message

print("🟢 Subscriber 2 listening...")
client.loop_forever()
