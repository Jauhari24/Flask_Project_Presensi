# config.py atau di file constants
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def validate_karyawan_form(form, files=None):
    errors = []
    data_karyawan = {
        'id': form.get('id'),          # ID karyawan (opsional, ada kalau edit)
        'id_kartu': form.get('id_kartu'),        # ID kartu
        'nama': form.get('nama'),      # Nama karyawan
        'gambar': []                   # List file image yang valid
    }

    # Validasi field wajib
    if not data_karyawan['id_kartu']:
        errors.append("ID Kartu wajib diisi.")
    if not data_karyawan['nama']:
        errors.append("Nama karyawan wajib diisi.")

    # Validasi gambar upload
    image_files = []
    if files:
        image_files = files.getlist('gambar')  # Sesuai name="gambar" di HTML

    # Kalau tambah baru, minimal 1 gambar wajib
    if not data_karyawan['id']:  
        if not image_files or all(f.filename.strip() == '' for f in image_files):
            errors.append('Minimal 1 foto karyawan wajib diunggah.')

    # Batas jumlah gambar
    if image_files and len(image_files) > 4:
        errors.append('Maksimal 4 gambar diperbolehkan.')

    # Validasi format file
    valid_images = []
    for img in image_files:
        if img.filename.strip() == '':
            continue
        ext = img.filename.rsplit('.', 1)[-1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            errors.append(
                f"Format file {img.filename} tidak valid. "
                "Jenis yang diizinkan: jpg, jpeg, png."
            )
        else:
            valid_images.append(img)

    if not errors:
        data_karyawan['gambar'] = valid_images  # Simpan hanya file yang lolos validasi
        return None, data_karyawan

    return errors, None
