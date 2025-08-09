import paho.mqtt.client as paho
import os
import time
import requests
import certifi
import ssl
from datetime import datetime
from dotenv import load_dotenv
from app import socketio  # Untuk emit ke UI
from flask import current_app

# Load .env file
load_dotenv()

# Ambil variabel dari .env
BROKER = os.environ.get("MQTT_BROKER")
PORT = int(os.environ.get("MQTT_PORT", 8883))
USERNAME = os.environ.get("MQTT_USERNAME")
PASSWORD = os.environ.get("MQTT_PASSWORD")

# Topik yang digunakan
TOPICS = [
    ("alat/login_status", 1),
    ("alat/register_status",1),
    ("alat/message",1),
    ("data/rfid/login",1),
    ("data/rfid/register", 1),
]

client = None
app_context = None


latest_card_data = {
    "login": None,
    "register": None,
}

card_last_seen = {
    "login": None,
    "register": None,
}

card_last_value = {
    "login": None,
    "register": None,
}

card_last_change = {
    "login": None,
    "register": None,
}

card_alert_sent = {
    "login": None,
    "register": None,
}

check_times = [1, 2, 3, 4, 5, 10, 24]  # jam

SENSOR_RESET_SECONDS = 60  # Reset fingerprint setiap 120 detik

# Callback jika berhasil connect ke broker
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("✅ Terhubung ke MQTT Broker")
        for topic, qos in TOPICS:
            client.subscribe(topic, qos)
            print(f"📡 Berlangganan ke topik: {topic}")
    else:
        print("❌ Koneksi gagal")
        print(f"   USERNAME: {USERNAME}")
        print(f"   PASSWORD: {PASSWORD}")
        print(f"   BROKER: {BROKER}")
        print(f"   PORT: {PORT}")
        print(f"   Kode Reason: {reason_code}")


# Callback untuk topik presensi/rfid
def handle_rfid_data_factory(app_instance):
    def handle_rfid_data(client, userdata, message):
        topic = message.topic
        value = message.payload.decode('utf-8').strip()

        mapping = {
            "data/rfid/register": "register",
            "data/rfid/login": "login",
        }
        label = mapping.get(topic)
        if label == "register":
            # Normalisasi UID agar format sama antara alat & server
            # Contoh: "ab 3f 12 c9" -> "AB 3F 12 C9"
            uid_value = " ".join(value.split()).upper()

            now = datetime.now()
            last_val = card_last_value[label]

            if last_val != uid_value:
                card_last_change[label] = now
                card_last_value[label] = uid_value
                print(f"📡 Data register terkirim: {uid_value}")
            
            latest_card_data[label] = uid_value
            card_last_seen[label] = now
            print(f"📥 Data {label} diterima: {uid_value}")

            socketio.emit("rfid_update", latest_card_data)

        # ✅ Bungkus bagian yang mengakses Flask context
        if label == "login":
            with app_instance.app_context():
                
                print(f"📥 Data login diterima: {value}")
    
    return handle_rfid_data
        
        
def check_card_status():
    now = datetime.now()
    updated = False

    for label in latest_card_data:
        last_seen = card_last_seen.get(label)
        val = latest_card_data[label]

        # Reset jika tidak ada pembaruan selama 120 detik
        if last_seen and (now - last_seen).total_seconds() > SENSOR_RESET_SECONDS:
            if val is not None:
                latest_card_data[label] = None
                card_last_seen[label] = None
                card_last_value[label] = None
                print(f"⏳ rfid '{label}' direset setelah 60 detik tidak ada update.")
                updated = True

    if updated:
        socketio.emit("finger_update", latest_card_data)
    

# Jalankan koneksi MQTT
def run_mqtt_service(app_instance):
    global client

    print(f"🚀 Menghubungkan ke MQTT Broker {BROKER}:{PORT}")
    print(f"🔐 USERNAME: {USERNAME}")
    print(f"🔐 PASSWORD: {PASSWORD}")

    client = paho.Client(client_id="presensi_karyawan", protocol=paho.MQTTv5)
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set(ca_certs=certifi.where(), tls_version=ssl.PROTOCOL_TLS_CLIENT)

    client.on_connect = on_connect
    client.message_callback_add("data/rfid/login", handle_rfid_data_factory(app_instance))
    client.message_callback_add("data/rfid/register", handle_rfid_data_factory(app_instance))

    try:
        # ✅ Connect ke broker
        client.connect(BROKER, PORT, keepalive=60)

        # ✅ Jalankan loop MQTT di thread terpisah
        client.loop_start()
        while True:
            check_card_status()
            time.sleep(30)  # cek status fingerprint setiap 30 detik

    except KeyboardInterrupt:
        print("🛑 Memutuskan koneksi MQTT...")
        client.disconnect()
        client.loop_stop()
        
        
# 📤 Kirim perintah login ke ESP32
def send_login_command(msg="1"):
    if client:
        try:
            client.publish("alat/login_status", msg)
            print("📤 Kirim perintah 'login/status' ke ESP32")
        except Exception as e:
            print(f"❌ Gagal kirim perintah login: {e}")
    else:
        print("❌ Client MQTT belum tersedia")


# 📤 Kirim perintah register ke ESP32
def send_register_command(msg="0"):
    if client:
        try:
            client.publish("alat/register_status", msg)
            print("📤 Kirim perintah 'register/status' ke ESP32")
        except Exception as e:
            print(f"❌ Gagal kirim perintah register: {e}")
    else:
        print("❌ Client MQTT belum tersedia")


def send_message_command(msg):
    if client:
        try:
            client.publish("alat/message", msg)
            print(f"📤 Kirim pesan ke ESP32: {msg}")
        except Exception as e:
            print(f"❌ Gagal kirim pesan: {e}")
    else:
        print("❌ Client MQTT belum tersedia")