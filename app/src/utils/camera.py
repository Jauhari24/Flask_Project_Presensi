import threading
import os
import time
#* Definisi

# Lock untuk melindungi frame_buffer
known_face_encodings = []
known_face_names = []
start_time = time.time()
timeout = 10  # detik
known_face_encodings = []
known_face_names = []
capture_thread_started = False
streaming_active = False  # global
face_data_lock = threading.Lock()
frame_buffer = None
frame_lock = threading.Lock()
faces_loaded = False  # Variabel global untuk melacak apakah faces sudah dimua