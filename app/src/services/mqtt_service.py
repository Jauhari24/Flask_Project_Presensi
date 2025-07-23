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
    ("presensi/rfid", 1),
    ("kirim/pesan", 1)
]

client = None
app_context = None

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

# Callback default jika topik tidak punya handler khusus
def on_message(client, userdata, msg):
    print(f"📬 [Default Handler] Topik: {msg.topic} | Data: {msg.payload.decode().strip()}")

# Callback untuk topik presensi/rfid
def handle_rfid(client, userdata, msg):
    payload = msg.payload.decode().strip()
    topic = msg.topic
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"📨 Data RFID Masuk: {payload} pada {now}")

    try:
        hasil = proses_presensi_rfid(payload, now)
        print(hasil)
        socketio.emit("update_presensi", hasil)
    except Exception as e:
        print(f"❌ Error handle_rfid: {e}")
        socketio.emit("mqtt_error", {"error": str(e)})

# Callback untuk topik kirim/pesan
def handle_pesan(client, userdata, msg):
    payload = msg.payload.decode().strip()
    topic = msg.topic
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"📨 Pesan Diterima: {payload} pada {now}")

    try:
        # Kirim ke UI
        socketio.emit("pesan_masuk", {"waktu": now, "pesan": payload})
    except Exception as e:
        print(f"❌ Error handle_pesan: {e}")
        socketio.emit("mqtt_error", {"error": str(e)})

# Jalankan koneksi MQTT
def run_mqtt_service(app_instance):
    global client, app_context
    app_context = app_instance

    print(f"🚀 Menghubungkan ke MQTT Broker {BROKER}:{PORT}")
    print(f"🔐 USERNAME: {USERNAME}")
    print(f"🔐 PASSWORD: {PASSWORD}")

    client = paho.Client(client_id="presensi_karyawan", protocol=paho.MQTTv5)
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set(ca_certs=certifi.where(), tls_version=ssl.PROTOCOL_TLS_CLIENT)

    client.on_connect = on_connect
    client.on_message = on_message  # default handler
    client.message_callback_add("presensi/rfid", handle_rfid)
    client.message_callback_add("kirim/pesan", handle_pesan)

    try:
        client.connect(BROKER, PORT)
        client.loop_start()
    except Exception as e:
        print(f"❌ Gagal koneksi ke MQTT: {e}")
        socketio.emit("mqtt_error", {"error": str(e)})

# Fungsi dummy untuk proses_presensi_rfid (silakan ganti sesuai logika asli)
def proses_presensi_rfid(payload, waktu):
    print(f"[Simulasi] Proses presensi RFID untuk ID {payload} pada {waktu}")
    return {"tipe": "RFID", "waktu": waktu, "id_kartu": payload}
