


import ssl
import certifi
from flask import Flask, render_template
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt

# ==============================
# 🔧 HiveMQ Cloud Configuration
# ==============================
MQTT_BROKER = "mqtt-dashboard.com"  # from your HiveMQ Cloud cluster page
MQTT_PORT = 8883
MQTT_USERNAME = "dipanshu_30cr"
MQTT_PASSWORD = "1234"
MQTT_TOPIC = "dipans"

# ==============================
# ⚙️ Flask Setup
# ==============================
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# ==============================
# 🔌 MQTT Setup
# ==============================
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print("✅ Connected to HiveMQ Cloud")
        client.subscribe(MQTT_TOPIC)
        print(f"📡 Subscribed to topic: {MQTT_TOPIC}")
    else:
        print("❌ Connection failed:", reason_code)

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"📩 MQTT message received: {msg.topic} → {message}")
    # Broadcast message to all connected web clients
    socketio.emit("mqtt_message", {"topic": msg.topic, "message": message})

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
context = ssl.create_default_context(cafile=certifi.where())
mqtt_client.tls_set_context(context)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

mqtt_client.loop_start()

# ==============================
# 🌐 Flask Routes
# ==============================
@app.route('/')
def index():
    return render_template("index.html")

# ==============================
# 🚀 Run Flask App
# ==============================
if __name__ == "__main__":
    print("🌍 Starting Flask MQTT Dashboard on http://localhost:5000")
    socketio.run(app, host="0.0.0.0", port=5000)