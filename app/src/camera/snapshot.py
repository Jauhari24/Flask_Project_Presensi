import cv2
import face_recognition
import numpy as np
import datetime
import os
import time
from app.src.utils.camera import frame_buffer,frame_lock,known_face_encodings,known_face_names, threading,streaming_active
import pickle
import hashlib


def load_known_faces():
    global known_face_encodings, known_face_names

    known_face_encodings = []
    known_face_names = []

    base_path = "app/src/static/train model/snapshots"
    cache_path = "app/src/camera/face_cache.pkl"

    cache_data = {}

    # Load cache if exists
    if os.path.exists(cache_path):
        with open(cache_path, 'rb') as f:
            cache_data = pickle.load(f)

    updated_cache = {}

    try:
        for folder_name in os.listdir(base_path):
            folder_path = os.path.join(base_path, folder_name)
            if os.path.isdir(folder_path):
                user_name = folder_name
                for filename in os.listdir(folder_path):
                    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                        file_path = os.path.join(folder_path, filename)

                        # Buat hash berdasarkan isi file untuk mendeteksi perubahan
                        with open(file_path, 'rb') as img_file:
                            file_hash = hashlib.md5(img_file.read()).hexdigest()

                        cache_key = f"{user_name}/{filename}"

                        # Cek apakah sudah di-cache dan tidak berubah
                        if cache_key in cache_data and cache_data[cache_key]["hash"] == file_hash:
                            encoding = cache_data[cache_key]["encoding"]
                            print(f"♻️ Cache digunakan untuk: {cache_key}")
                        else:
                            image = face_recognition.load_image_file(file_path)
                            face_encodings = face_recognition.face_encodings(image)
                            if not face_encodings:
                                print(f"[!] Tidak ada wajah di file: {file_path}")
                                continue
                            encoding = face_encodings[0]
                            print(f"✅ Wajah dimuat ulang: {cache_key}")

                        # Simpan ke data runtime dan cache baru
                        known_face_encodings.append(encoding)
                        known_face_names.append(user_name)
                        updated_cache[cache_key] = {
                            "hash": file_hash,
                            "encoding": encoding
                        }
    except Exception as e:
        print(f"[!] Gagal memuat wajah: {e}")

    # Simpan cache
    with open(cache_path, 'wb') as f:
        pickle.dump(updated_cache, f)

    return known_face_encodings, known_face_names

#* Screenshoot Foto CCTV
def take_snapshot(ESP_URL):
    print("[INFO] Connecting to CCTV...")
    cap = cv2.VideoCapture(ESP_URL)

    if not cap.isOpened():
        print("[ERROR] Failed to connect to CCTV.")
        return None

    print("[INFO] Reading frame...")
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("[ERROR] Failed to capture frame.")
        return None

    # Buat folder jika belum ada
    output_dir = "app/src/static/snapshots/captured"
    os.makedirs(output_dir, exist_ok=True)

    # Simpan frame ke file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/snapshot_{timestamp}.jpg"
    cv2.imwrite(filename, frame)

    print(f"[INFO] Snapshot saved at {filename}")
    return filename

def start_capture_thread(RTSP_URL):
    global streaming_active
    
    cap = cv2.VideoCapture(RTSP_URL)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if streaming_active:
        return
    streaming_active = True
    # Jalankan thread capture
    threading.Thread(target=capture_thread, args=(RTSP_URL,), daemon=True).start()

def capture_thread(RTSP_URL):
    global frame_buffer
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)

    if not cap.isOpened():
        print("[ERROR] Failed to open RTSP stream.")
        return

    while True:
        success, frame = cap.read()

        if not success:
            print("[WARNING] Failed to read frame. Retrying...")
            time.sleep(0.5)  # kasih delay biar gak 100% CPU usage
            continue

        with frame_lock:
            frame_buffer = frame


#* ====== Video Frame Generator Stream======
def gen_frames():
    timeout = 10  # detik
    start_time = time.time()

    while True:
        if frame_buffer is None:
            if time.time() - start_time > timeout:
                print("[INFO] Timeout: Tidak ada frame yang diterima.")
                break
            time.sleep(1/40)
            continue

        start_time = time.time()

        try:
            with frame_lock:
                frame = frame_buffer.copy()

            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue

            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        except Exception as e:
            print(f"[ERROR] Streaming frame failed: {e}")
            continue
