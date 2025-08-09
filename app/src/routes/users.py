from flask import Blueprint, render_template, redirect, url_for, flash,request
from app.src.routes.validation.login import login_required
from app.src.routes.validation.users import validate_karyawan_form

users = Blueprint('users', __name__)


@login_required
@users.route('/tambah_karyawan', methods=['GET', 'POST'])
def tambah_karyawan():
    if request.method == 'POST':
        errors, data = validate_karyawan_form(request.form, request.files)
        if errors:
            for err in errors:
                flash(err, 'danger')
        else:
            Data_add_user, status_code = add_karyawan_service(data)
            if status_code == 400:
                flash(Data_add_user['error'], 'danger')
            else:
                flash('Karyawan berhasil ditambahkan.', 'success')

        return redirect(url_for('main.data_karyawan'))

    # kalau GET, langsung render form tambah karyawan
    return render_template('tambah_karyawan.html')


@users.route('/edit-karyawan/<id>', methods=['GET', 'POST'])
def edit_karyawan(id):
    karyawan = Karyawan.get_by_id(id)
    if request.method == 'POST':
        errors, data = validate_karyawan_form(request.form, request.files)
        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('edit_karyawan.html', karyawan=karyawan)
        
        # Update data di database
        # contoh: karyawan.update(**data)
        
        flash('Karyawan berhasil diperbarui.', 'success')
        return redirect(url_for('users.daftar_karyawan'))
    
    return render_template('edit_karyawan.html', karyawan=karyawan)