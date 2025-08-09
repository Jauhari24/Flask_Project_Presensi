import sys
import os
import random
from datetime import datetime, timedelta
from faker import Faker

# Tambahkan path root agar bisa import 'app'
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..'))
)

from app import create_app, db
from app.src.model.schemas.data_karyawan import DataKaryawan
from app.src.model.schemas.riwayat_presensi import RiwayatPresensi
from app.src.model.schemas.gambar import Gambar  # Model Gambar kamu

# Inisialisasi Faker
fake = Faker("id_ID")

# Konfigurasi jumlah data dummy
JUMLAH_KARYAWAN = 5
PRESENSI_PER_KARYAWAN = 3
GAMBAR_PER_KARYAWAN = 2  # Bisa diubah, max 4 sesuai validasi form

# Buat app Flask
app = create_app()


def seed_data():
    with app.app_context():
        # Reset database
        db.drop_all()
        db.create_all()

        for _ in range(JUMLAH_KARYAWAN):
            nama = fake.name()
            id_kartu = fake.unique.lexify("RFID-??????")

            # Buat data karyawan
            karyawan = DataKaryawan(
                nama=nama,
                id_kartu=id_kartu
            )
            db.session.add(karyawan)
            db.session.flush()  # Ambil ID karyawan

            # Tambahkan gambar karyawan (dummy nama file)
            for i in range(GAMBAR_PER_KARYAWAN):
                file_name = f"{nama.replace(' ', '_').lower()}_{i+1}.jpg"
                gambar = Gambar(
                    name=file_name,
                    data_karyawan_id=karyawan.id
                )
                db.session.add(gambar)

            # Tambahkan riwayat presensi
            for _ in range(PRESENSI_PER_KARYAWAN):
                waktu = datetime.now() - timedelta(days=random.randint(0, 5))
                status = random.choice([True, False])
                presensi = RiwayatPresensi(
                    status=status,
                    waktu_dibuat=waktu,
                    karyawan_id=karyawan.id,
                    gambar=file_name
                )
                db.session.add(presensi)

        db.session.commit()
        print("✅ Dummy data berhasil dimasukkan (karyawan, gambar, presensi).")


if __name__ == "__main__":
    seed_data()
