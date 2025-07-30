from flask import Blueprint, render_template, redirect, url_for, flash,request,jsonify
from app.src.routes.validation.login import login_required
# from app.src.services.presensi_service import get_all_presensi_service

card = Blueprint('card', __name__)

@card.route('/daftar-kartu', methods=['POST'])
@login_required
def daftar_kartu():
    try:
        data = request.get_json()
        daftar_value = data.get('daftar')

        if daftar_value == "1":
            print("Permintaan daftar kartu diterima.")
            # Bisa lanjutkan proses aktivasi WebSocket atau kirim sinyal, dsb.
            return jsonify({'success': True, 'message': 'Pendaftaran kartu dimulai'})
        else:
            return jsonify({'success': False, 'message': 'Nilai tidak valid'}), 400

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        return jsonify({'success': False, 'message': 'Permintaan tidak valid'}), 400
    