from flask import Blueprint, render_template, redirect, url_for, flash
from app.src.utils import cards, table_rows
from app.src.routes.validation.login import login_required
from app.src.services.presensi_service import get_all_presensi_service

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    # Dashboard: Ringkasan & tabel presensi terbaru
    data_presensi = get_all_presensi_service()
    return render_template(
        'pages/index.html',
        cards=cards,  # Total Karyawan, Hadir Hari Ini, Terlambat, dsb
        table_rows=data_presensi
    )

@main.route('/riwayat-presensi', methods=['GET'])
@login_required
def riwayat_presensi():
    # Halaman tabel semua riwayat presensi karyawan
    data_presensi = get_all_presensi_service()
    return render_template(
        'pages/riwayat-presensi/riwayat_presensi.html',
        table_rows=data_presensi
    )

@main.route('/kontrol-alat', methods=['GET'])
@login_required
def control():
    # Contoh kontrol alat presensi (opsional)
    flash("Fitur kontrol alat belum tersedia.", "info")
    return redirect(url_for('main.index'))