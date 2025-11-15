import paho.mqtt.client as mqtt
import pyttsx3
import threading

MQTT_BROKER = "localhost"
MQTT_TOPIC = "people/count"

last_spoken = None

def speak_dynamic(count):
    engine = pyttsx3.init()
    engine.say(f"{count} people")
    engine.runAndWait()
    engine.stop()

def on_message(client, userdata, msg):
    global last_spoken
    count = msg.payload.decode()

    print("Received →", count, "people")

    # speak only when value changes
    if count != last_spoken:
        last_spoken = count
        threading.Thread(target=speak_dynamic, args=(count,), daemon=True).start()

def on_connect(client, userdata, flags, rc):
    print("Subscriber connected.")
    client.subscribe(MQTT_TOPIC)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, 1883, 60)
client.loop_forever()
