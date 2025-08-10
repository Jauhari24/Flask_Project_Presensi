from flask import Blueprint, render_template, redirect, url_for, flash,request
from app.src.routes.validation.login import login_required
from app.src.routes.validation.users import validate_karyawan_form
from app.src.services.karyawan_service import add_karyawan_service,delete_karyawan_service

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

@login_required
@users.route('/delete-karyawan/<int:id>', methods=['DELETE'])
def delete_karyawan(id):
    try:
        # Hapus karyawan berdasarkan ID
        success = delete_karyawan_service(id)
        if not success:
            return {"error": "User not found"}, 404
        
        return {"message": "User deleted successfully"}, 200
    except Exception as e:
        print(f"❌ Error saat menghapus user: {e}")
        return {"error": "Terjadi kesalahan saat menghapus data."}, 500

