from flask import Blueprint, app, render_template, redirect, url_for, flash,request, send_file
from app.src.routes.validation.login import login_required
from app.src.services.karyawan_service import get_all_riwayat_karyawan_service
from app.src.repositories.user_repositories import get_all_karyawan_repository
from app.src.repositories.cctv_repositories import get_cctv_link_repository, update_cctv_link_repository
from datetime import datetime, date, time
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io
main = Blueprint('main', __name__)

@main.route('/')
@login_required
def home():
    camera = get_cctv_link_repository()

    today = date.today()
    start_day = datetime.combine(today, time.min)  # 00:00
    end_day = datetime.combine(today, time.max)    # 23:59:59

    # Ambil semua data presensi dari service (hasil dict)
    data_riwayat_presensi = get_all_riwayat_karyawan_service()

    # Filter hanya data hari ini
    data_hari_ini = []
    for d in data_riwayat_presensi:
        # Pastikan waktu_dibuat diubah ke datetime
        waktu = d.get("waktu_dibuat")
        if isinstance(waktu, str):
            waktu = datetime.fromisoformat(waktu)  # misalnya format "2025-09-13T08:15:00"
        if start_day <= waktu <= end_day:
            d["waktu_dibuat"] = waktu
            data_hari_ini.append(d)

    # Hitung jumlah hadir & telat berdasarkan kolom status
    jumlah_hadir = sum(1 for d in data_hari_ini if d.get("status") == True)
    jumlah_telat = sum(1 for d in data_hari_ini if d.get("status") == False)

    print("Data presensi hari ini:", data_hari_ini)
    print("Jumlah hadir:", jumlah_hadir)
    print("Jumlah telat:", jumlah_telat)
    print("data karyawan", data_riwayat_presensi)

    return render_template(
        'pages/dashboard-page/index.html',
        current_path=request.path,
        camera=camera,
        data_riwayat_presensi=data_hari_ini,
        jumlah_hadir=jumlah_hadir,
        jumlah_telat=jumlah_telat,
        tanggal=today.strftime("%A, %d %B %Y")
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

    data_riwayat_presensi = get_all_riwayat_karyawan_service()
    
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

@main.route('/riwayat-presensi/export-pdf')
@login_required
def export_pdf_presensi():
    bulan = request.args.get("bulan")  # format: YYYY-MM
    if not bulan:
        bulan = datetime.today().strftime("%Y-%m")

    # ambil data riwayat presensi
    data_riwayat_presensi = get_all_riwayat_karyawan_service()

    # filter data berdasarkan bulan
    data_filtered = []
    for d in data_riwayat_presensi:
        waktu = d.get("waktu_dibuat")
        if isinstance(waktu, str):
            waktu = datetime.fromisoformat(waktu)
        if waktu.strftime("%Y-%m") == bulan:
            d["waktu_dibuat"] = waktu
            data_filtered.append(d)

    # buat PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Judul
    elements.append(Paragraph(f"Laporan Riwayat Presensi Bulan {bulan}", styles['Title']))
    elements.append(Spacer(1, 12))

    # Header tabel
    table_data = [["ID Kartu", "Nama", "Tanggal", "Jam Masuk", "Status"]]

    # Isi tabel
    for d in data_filtered:
        table_data.append([
            d.get("data_karyawan", {}).get("id_kartu", "-"),
            d.get("data_karyawan", {}).get("nama", "-"),
            d["waktu_dibuat"].strftime("%d-%m-%Y"),
            d["waktu_dibuat"].strftime("%H:%M"),
            "Hadir" if d.get("status") else "Tidak Hadir"
        ])

    # Tabel
    table = Table(table_data, colWidths=[70, 120, 80, 80, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"riwayat_presensi_{bulan}.pdf",
        mimetype='application/pdf'
    )