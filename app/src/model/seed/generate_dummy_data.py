import sys
import os

# Tambahkan path root agar bisa import 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..')))

import random
from datetime import datetime, timedelta
from faker import Faker

from app import create_app, db
from app.src.model.schemas.data_karyawan import DataKaryawan
from app.src.model.schemas.riwayat_presensi import RiwayatPresensi

# Inisialisasi Faker
fake = Faker("id_ID")

# Buat app Flask
app = create_app()

def seed_data():
    with app.app_context():
        # Hapus semua tabel & buat ulang
        db.drop_all()
        db.create_all()

        for _ in range(5):  # Jumlah karyawan
            nama = fake.name()
            id_kartu = fake.unique.lexify("RFID-??????")
            foto = f"{nama.replace(' ', '_').lower()}.jpg"

            # Buat data karyawan
            karyawan = DataKaryawan(nama=nama, id_kartu=id_kartu, foto=foto)
            db.session.add(karyawan)
            db.session.flush()  # Dapatkan karyawan.id sebelum commit

            for _ in range(3):  # Setiap karyawan punya 3 presensi
                waktu = datetime.now() - timedelta(days=random.randint(0, 5))
                status = random.choice([True, False])
                presensi = RiwayatPresensi(
                    status=status,
                    waktu_dibuat=waktu,
                    karyawan_id=karyawan.id  # Pastikan ada kolom ini
                )
                db.session.add(presensi)

        db.session.commit()
        print("✅ Dummy data berhasil dimasukkan.")

if __name__ == "__main__":
    seed_data()
