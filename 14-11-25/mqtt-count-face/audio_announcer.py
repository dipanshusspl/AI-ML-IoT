import paho.mqtt.client as mqtt
import pyttsx3

MQTT_BROKER = "localhost"
MQTT_TOPIC = "people/count"

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def on_message(client, userdata, msg):
    count = msg.payload.decode()
    announcement = f"{count} people"
    print("Received count →", announcement)
    speak(announcement)

def on_connect(client, userdata, flags, rc):
    print("Connected to broker")
    client.subscribe(MQTT_TOPIC)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, 1883, 60)
client.loop_forever()
