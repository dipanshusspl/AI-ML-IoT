import paho.mqtt.client as mqtt
from playsound import playsound

last_count = None

def on_message(client, userdata, msg):
    global last_count
    new_count = int(msg.payload.decode())

    print(f"📩 Received Count: {new_count}")

    if last_count is None:
        last_count = new_count
        return

    if new_count != last_count:
        print("🔔 Count changed! Playing sound...")
        playsound("alert.mp3")   # put any beep sound file in folder

    last_count = new_count

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("localhost", 1883, 60)
client.subscribe("topic/count")
client.on_message = on_message

print("🎧 Subscriber running...")
client.loop_forever()
