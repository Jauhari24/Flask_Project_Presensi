import face_recognition
import os
import time
import numpy as np
import face_recognition

# Repos & util imports
from app.src.repositories.cctv_repositories import get_cctv_link_repository
from app.src.repositories.riwayat_presensi_repositories import create_riwayat_karyawan_repository
from app.src.repositories.user_repositories import get_karyawan_by_rfid_id

# Import modul utility camera (variabel shared: known_face_encodings, known_face_names, face_data_lock, faces_loaded)
from app.src.utils import camera as camera_utils

# Import take_snapshot dan load_known_faces (coba kedua kemungkinan lokasi)
try:
    from app.src.camera.snapshot import load_known_faces, take_snapshot
except Exception:
    # fallback ke snapshot modul jika ada
    from app.src.camera.snapshot import load_known_faces, take_snapshot


def _take_snapshot_with_retries(camera_url, retries=3, delay=0.6):
    """
    Wrapper take_snapshot dengan retry: mengurangi kasus snapshot kosong.
    Return: full path file snapshot atau None.
    """
    for attempt in range(1, retries + 1):
        try:
            path = take_snapshot(camera_url)
        except Exception as e:
            print(f"[WARN] take_snapshot error attempt {attempt}: {e}")
            path = None

        if path and os.path.exists(path):
            return path

        print(f"[WARN] Snapshot gagal atau tidak ada file. Attempt {attempt}/{retries}")
        time.sleep(delay)

    return None

def rfid_auth(value_parsed, app):
    from datetime import datetime
    # import layanan mqtt dinamis agar modul tidak circular
    from app.src.services.mqtt_service import send_message_command
    import os

    # Ambil link kamera (bisa http atau rtsp tergantung config)
    camera_access = get_cctv_link_repository()
    if not camera_access:
        print("❌ Tidak ada data CCTV tersedia")
        return
    camera_url = camera_access.url

    # Kirim perintah/feedback ke device/UI
    send_message_command("Scan Wajah")
    time.sleep(1.5)  # kasih sedikit jeda sebelum ambil gambar

    # Ambil snapshot dengan retry
    snapshot_full_path = _take_snapshot_with_retries(camera_url, retries=4, delay=0.6)
    if not snapshot_full_path or not os.path.exists(snapshot_full_path):
        print("[ERROR] Gagal ambil gambar dari CCTV")
        send_message_command("Gagal ambil gambar")
        return
    print(f"📸 Gambar diambil: {snapshot_full_path}")

    # Normalisasi path yang disimpan di DB (relatif ke static/)
    if 'static/' in snapshot_full_path.replace("\\", "/"):
        idx = snapshot_full_path.replace("\\", "/").index('static/')
        snapshot_path_for_db = snapshot_full_path.replace("\\", "/")[idx:]
    else:
        snapshot_path_for_db = snapshot_full_path

    # Ambil user berdasarkan RFID
    rfid_user = get_karyawan_by_rfid_id(value_parsed)
    if not rfid_user:
        print("❌ RFID tidak dikenali")
        send_message_command("User tidak ditemukan")
        create_riwayat_karyawan_repository(
            data={
                'status': "Tidak Diketahui",
                'gambar': snapshot_path_for_db,
                'karyawan_id': 0
            }
        )
        return

    # Pastikan data wajah dikenal sudah dimuat (gunakan modul camera_utils supaya update faces_loaded berhasil)
    with camera_utils.face_data_lock:
        # Jika belum ter-load, panggil load_known_faces()
        if not getattr(camera_utils, "faces_loaded", False) or not getattr(camera_utils, "known_face_encodings", None):
            print("[INFO] Memuat data wajah dikenal...")
            try:
                # load_known_faces dapat mengembalikan tuple (encodings, names) atau mengisi global di modul kameranya
                load_result = load_known_faces()
                # Jika fungsi mengembalikan data, sinkronkan ke modul camera_utils
                if isinstance(load_result, tuple) and len(load_result) >= 2:
                    encs, names = load_result[0], load_result[1]
                    camera_utils.known_face_encodings = encs
                    camera_utils.known_face_names = names
                # set flag agar tidak reload berkali-kali
                camera_utils.faces_loaded = True
                print(f"[INFO] Jumlah wajah dikenal: {len(getattr(camera_utils, 'known_face_encodings', []))}")
            except Exception as e:
                print(f"[ERROR] Gagal load_known_faces(): {e}")

    # Baca snapshot dan lakukan encoding wajah
    try:
        image = face_recognition.load_image_file(snapshot_full_path)
    except FileNotFoundError:
        send_message_command("Gambar tidak ada")
        return
    except Exception as e:
        print(f"[ERROR] Tidak dapat memuat file gambar: {e}")
        send_message_command("Gagal baca gambar")
        return

    face_encodings = face_recognition.face_encodings(image, model='hog')
    if not face_encodings:
        send_message_command("Wajah tidak terdeteksi")
        # Simpan riwayat "tidak terdeteksi" jika perlu
        create_riwayat_karyawan_repository({
            'status': 0,
            'gambar': snapshot_path_for_db,
            'karyawan_id': rfid_user.id if rfid_user else 0
        })
        return

    # Pastikan known_face_encodings tidak kosong
    with camera_utils.face_data_lock:
        known_encs = getattr(camera_utils, "known_face_encodings", [])
        known_names = getattr(camera_utils, "known_face_names", [])

        if not known_encs:
            send_message_command("Data wajah kosong")
            create_riwayat_karyawan_repository({
                'status': 0,
                'gambar': snapshot_path_for_db,
                'karyawan_id': rfid_user.id
            })
            return

        # Hitung jarak wajah dan cari best match
        try:
            face_distances = face_recognition.face_distance(known_encs, face_encodings[0])
            best_match_index = np.argmin(face_distances)
            best_distance = float(face_distances[best_match_index])
        except Exception as e:
            print(f"[ERROR] Perhitungan jarak wajah gagal: {e}")
            send_message_command("Gagal proses wajah")
            return

        threshold = 0.45  # sesuaikan threshold sesuai quality dataset
        matched_name = None
        if best_distance < threshold:
            matched_name = known_names[best_match_index]

    # Verifikasi nama yang cocok dengan user RFID
    expected_name = rfid_user.nama.lower().replace(" ", "_")
    if matched_name and matched_name.lower() == expected_name:
        send_message_command("Login Berhasil")
        create_riwayat_karyawan_repository({
            'status': 1,
            'gambar': snapshot_path_for_db,
            'karyawan_id': rfid_user.id
        })
    elif matched_name:
        send_message_command("Wajah tidak cocok")
        create_riwayat_karyawan_repository({
            'status': 0,
            'gambar': snapshot_path_for_db,
            'karyawan_id': rfid_user.id
        })
    else:
        send_message_command("Wajah tidak dikenali")
        create_riwayat_karyawan_repository({
            'status': 0,
            'gambar': snapshot_path_for_db,
            'karyawan_id': rfid_user.id
        })