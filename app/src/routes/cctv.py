from flask import Blueprint, flash, redirect, request, url_for, Response
from app.src.repositories.cctv_repositories import get_cctv_link_repository, update_cctv_link_repository
from app.src.routes.validation.login import login_required
from app.src.utils.camera import frame_buffer,frame_lock,known_face_encodings,known_face_names, threading,streaming_active
from app.src.camera.snapshot import gen_frames, take_snapshot,start_capture_thread
cctv = Blueprint('cctv', __name__)
@cctv.route("/update-cctv/<id>", methods=["POST"])
def update_cctv(id):
    cctv_link = request.form.get("url")
    try:
        update_cctv_link_repository(cctv_link)  # Lakukan update CCTV link di database
        flash("CCTV link updated successfully!", "success")
    except Exception as e:
        print("Error updating CCTV link:", e)
        flash("Error updating CCTV link: " + str(e), "danger")
    return redirect(url_for("main.home"))

@cctv.route('/video_feed', methods=['GET', 'POST'])
@login_required
def video_feed():
    if frame_buffer is None:
        print("Kamera belum siap")
    data_cctv_access = get_cctv_link_repository()
    # Ambil RTSP dari database
    rtsp_url = data_cctv_access.url  # Ambil baris pertama, field rtsp
    if not data_cctv_access:
        return "Tidak ada data RTSP tersedia", 404  # Biar gak error kalau kosong
    start_capture_thread(rtsp_url)
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')