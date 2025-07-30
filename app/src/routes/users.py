from flask import Blueprint, render_template, redirect, url_for, flash,request
from app.src.routes.validation.login import login_required
# from app.src.services.presensi_service import get_all_presensi_service

users = Blueprint('users', __name__)


@login_required
@users.route('/tambah_karyawan', methods=['GET', 'POST'])
def tambah_karyawan():
    return render_template('pages/data-karyawan/form/index.html')

@login_required
@users.route('/edit_karyawan/<int:id>', methods=['GET', 'POST'])
def edit_karyawan(id):
    return render_template('pages/data-karyawan/form/index.html')