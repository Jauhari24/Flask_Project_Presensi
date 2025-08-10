import os
from app.src.repositories.riwayat_presensi_repositories import get_all_riwayat_karyawan_repository
from app.src.repositories.user_repositories import  create_karyawan_repository, get_karyawan_by_rfid_id,get_karyawan_by_id_with_images, delete_karyawan_by_id
from werkzeug.utils import secure_filename
import shutil
UPLOAD_FOLDER = 'app/static/train model/snapshots'

def serialize_datetime(dt):
    return dt.isoformat() if dt else None

def get_all_riwayat_karyawan_service():
    raw_data = get_all_riwayat_karyawan_repository()
    return [
        {
            "id": item.id,
            "status": item.status,
            "waktu_dibuat": serialize_datetime(item.waktu_dibuat),
            "data_karyawan": {
                "id": item.data_karyawan.id,
                "nama": item.data_karyawan.nama,
                "id_kartu": item.data_karyawan.id_kartu,
                "gambar": [
                    {
                        "id": g.id,
                        "name": g.name,
                        "createdAt": serialize_datetime(g.createdAt),
                        "updatedAt": serialize_datetime(g.updatedAt)
                    }
                    for g in item.data_karyawan.gambar
                ]
            }
        }
        for item in raw_data
    ]
def add_karyawan_service(data):
    try:
        # Cek Finger ID
        if get_karyawan_by_rfid_id(data['id_kartu']):
            return {"error": "rfid ID already exists"}, 400

        # Buat folder tujuan
        folder_name = f"{data['nama'].replace(' ', '_')}_{data['id_kartu']}"
        save_path = os.path.join(UPLOAD_FOLDER, folder_name)
        os.makedirs(save_path, exist_ok=True)

        image_paths = []

        # Simpan semua gambar
        for idx, img_file in enumerate(data['gambar']):
            ext = img_file.filename.rsplit('.', 1)[-1].lower()
            filename = secure_filename(f"{data['nama'].replace(' ', '_')}_{data['id_kartu']}_{idx + 1}.{ext}")
            image_full_path = os.path.join(save_path, filename)
            img_file.save(image_full_path)

            relative_path = image_full_path.split('app/', 1)[-1].replace('\\', '/')
            image_paths.append(relative_path)

        # Simpan user ke database
        user_data = data.copy()
        del user_data['gambar']
        user_data['gambar'] = image_paths  # simpan list path relatif
        create_karyawan_repository(user_data)

        print('✅ Gambar berhasil disimpan:', image_paths)
        return {"message": "User created successfully"}, 201

    except Exception as e:
        print(f"❌ Error add_user: {e}")
        return {"error": str(e)}, 500


def delete_karyawan_service(karyawan_id):
    try:
        # Ambil data karyawan dan gambar terkait
        karyawan, images = get_karyawan_by_id_with_images(karyawan_id)

        if not karyawan:
            return False
        
        # Hapus file gambar dari sistem file
        if images:  # Pastikan ada gambar terkait
            # Ambil folder dari path gambar pertama
            first_image_path = os.path.join('app', images[0].name)
            folder_path = os.path.dirname(first_image_path)  # Dapatkan path folder
            
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)  # Hapus folder beserta isinya
                print(f"✅ Folder {folder_path} berhasil dihapus.")
            else:
                print(f"⚠️ Folder {folder_path} tidak ditemukan.")

        # Hapus user dari database
        delete_karyawan_by_id(karyawan_id)
        return True
    except Exception as e:
        print(f"❌ Error saat menghapus user: {e}")
        return False