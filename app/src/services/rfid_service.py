import face_recognition
from app.src.camera.snapshot import take_snapshot

# 🔄 Fungsi untuk mengirim perintah fingerprint
def fingerprint_auth(value_parsed,app):
    from datetime import datetime
    from app.src.services.mqtt_service import send_message_command
    import os
    import time


    # Ambil data RTSP
    data_door_access = get_all_cctv()
    if not data_door_access:
        print("❌ Tidak ada data RTSP tersedia")
        return
    rtsp_url = data_door_access.rtsp

    send_message_command(f"Scan Wajah")
    time.sleep(3)
    # Ambil snapshot
    snapshot_full_path = take_snapshot(rtsp_url)  # Full path dari fungsi
    if not snapshot_full_path or not os.path.exists(snapshot_full_path):
        send_message_command("Gagal ambil gambar")
        return

    # Dapatkan path yang disimpan ke database
    if 'static/' in snapshot_full_path:
        idx = snapshot_full_path.index('static/')
        snapshot_path_for_db = snapshot_full_path[idx:]  # Misal: static/snapshots/...
    else:
        snapshot_path_for_db = snapshot_full_path  # fallback aman

    # Dapatkan user dari fingerprint
    user = get_user_by_fingerprint_id(value_parsed)
    if not user:
        print("❌ Fingerprint tidak dikenali")
        send_message_command("User tidak ditemukan")
        send_door_status_command("1")
        create_door_access(
            data={
                'name': "Tidak diketahui",
                'finger': 0,
                'img': snapshot_path_for_db,
                'door_access': "false",
                'access_time': datetime.now()
            }
        )
        return

    # Tidak ada akses pintu
    if user.door_access == 'false':
        send_message_command("Akses pintu ditutup")
        send_door_status_command("1")
        create_door_access(
            data={
                'name': user.name,
                'finger': str(user.finger_id),
                'img': snapshot_path_for_db,
                'door_access': str(user.door_access),
                'access_time': datetime.now()
            }
        )
        return
    
    # Face recognition
    # load_known_faces()

    try:
        image = face_recognition.load_image_file(snapshot_full_path)
    except FileNotFoundError:
        send_message_command("Gambar tidak ada")
        send_door_status_command("1")
        return

    face_encodings = face_recognition.face_encodings(image)
    if not face_encodings:
        send_message_command("Wajah tidak terdeteksi")
        send_door_status_command("1")
        return
    
    # Load data wajah dikenal
    # known_face_encodings, known_face_names = load_known_faces()
    # if not known_face_encodings:
    #     send_message_command("Data wajah kosong")
    #     send_door_status_command("1")
    #     return
    # matches = face_recognition.compare_faces(known_face_encodings, face_encodings[0], tolerance=0.65)
    # if True in matches:
    #     matched_index = matches.index(True)
    #     matched_name = known_face_names[matched_index]
    #     if user.name.lower().replace(" ", "_") in matched_name.lower():
    #         send_message_command(f"Pintu Terbuka")
    #         send_door_status_command("0")
          
    #         create_door_access(
    #             data={
    #                 'name': user.name,
    #                 'finger': str(user.finger_id),
    #                 'img': snapshot_path_for_db,
    #                 'door_access': str(user.door_access),
    #                 'access_time': datetime.now()
    #             }
    #         )
    #     else:
    #         send_message_command("Wajah tidak cocok")
    #         create_door_access(data={
    #             'name': 'Wajah Tidak cocok',
    #             'finger': str(user.finger_id),
    #             'img': snapshot_path_for_db,
    #             'door_access': 'false',
    #             'access_time': datetime.now()
    #         })
    #         send_door_status_command("1")
    # else:
    #     send_message_command("Wajah tidak dikenali")
    #     send_door_status_command("1")
 
    matched_name = None
    with face_data_lock:
        if not known_face_encodings:
            send_message_command("Data wajah kosong")
            send_door_status_command("1")
            return

        face_distances = face_recognition.face_distance(known_face_encodings, face_encodings[0])
        best_match_index = np.argmin(face_distances)
        best_distance = face_distances[best_match_index]
        threshold = 0.45  # Sesuaikan threshold

        if best_distance < threshold:
            matched_name = known_face_names[best_match_index]

    # Verifikasi hasil
    expected_name = user.name.lower().replace(" ", "_")

    if matched_name and matched_name.lower() == expected_name:
        send_message_command("Pintu Terbuka")
        send_door_status_command("0")
        create_door_access({
            'name': user.name,
            'finger': str(user.finger_id),
            'img': snapshot_path_for_db,
            'door_access': str(user.door_access),
            'access_time': datetime.now()
        })
    elif matched_name:
        send_message_command("Wajah tidak cocok")
        send_door_status_command("1")
        create_door_access({
            'name': 'Wajah Tidak cocok',
            'finger': str(user.finger_id),
            'img': snapshot_path_for_db,
            'door_access': 'false',
            'access_time': datetime.now()
        })
    else:
        send_message_command("Wajah tidak dikenali")
        send_door_status_command("1")