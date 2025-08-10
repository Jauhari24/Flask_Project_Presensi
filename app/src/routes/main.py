from flask import Blueprint, app, render_template, redirect, url_for, flash,request
from app.src.routes.validation.login import login_required
from app.src.services.karyawan_service import get_all_riwayat_karyawan_service
from app.src.repositories.user_repositories import get_all_karyawan_repository
from app.src.repositories.cctv_repositories import get_cctv_link_repository, update_cctv_link_repository
main = Blueprint('main', __name__)

@main.route('/')
@login_required
def home():
    camera = get_cctv_link_repository()
    return render_template(
        'pages/dashboard-page/index.html',current_path=request.path,
        camera=camera
    )
    
@main.route('/data-karyawan', methods=['GET'])
@login_required
def data_karyawan():
    camera = get_cctv_link_repository()
    # Halaman tabel semua karyawan
    data_karyawan = get_all_karyawan_repository()
    return render_template(
        'pages/data-karyawan/index.html',current_path=request.path,
        data_karyawan=data_karyawan,
        camera=camera
    )

@main.route('/riwayat-presensi', methods=['GET'])
@login_required
def riwayat_presensi():
    camera = get_cctv_link_repository()
    # Halaman tabel semua riwayat presensi karyawan
    # data_presensi = get_all_presensi_service()
    data_riwayat_presensi = get_all_riwayat_karyawan_service()
    print(data_riwayat_presensi)
    return render_template(
        'pages/riwayat-presensi/index.html',current_path=request.path,
        data_riwayat_presensi=data_riwayat_presensi,
        camera=camera
    )

@main.route('/form/data-karyawan', methods=['GET'])
@login_required
def form_data_karyawan():
    camera = get_cctv_link_repository()
    # Halaman tabel semua riwayat presensi karyawan
    # data_presensi = get_all_presensi_service()
    return render_template(
        'pages/data-karyawan/form/index.html',current_path=request.path,camera=camera
    )

