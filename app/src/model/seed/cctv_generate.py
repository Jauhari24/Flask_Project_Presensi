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
from app.src.model.schemas.cctv import CCTV  # Model CCTV kamu

# Inisialisasi Faker
fake = Faker("id_ID")

# Konfigurasi jumlah data dummy
JUMLAH_KARYAWAN = 5
PRESENSI_PER_KARYAWAN = 3
GAMBAR_PER_KARYAWAN = 2  # Bisa diubah, max 4 sesuai validasi form

# Buat app Flask
app = create_app()


def seed_cctv():
    with app.app_context():
        # Cek apakah sudah ada data CCTV, jika belum buat 1 data dummy
        if not CCTV.query.first():
            dummy_cctv = CCTV(
                url="http://192.168.0.100:8080/stream"
            )
            db.session.add(dummy_cctv)
            db.session.commit()
            print("✅ Dummy CCTV berhasil ditambahkan")
        else:
            print("ℹ️ Data CCTV sudah ada, tidak menambahkan lagi.")


if __name__ == "__main__":
    seed_cctv()
