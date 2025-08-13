from app import db
from app.src.model.schemas.riwayat_presensi import RiwayatPresensi
from app.src.model.schemas.data_karyawan import DataKaryawan    
from sqlalchemy.orm import joinedload
from datetime import datetime
def get_all_riwayat_karyawan_repository():
    return RiwayatPresensi.query.options(joinedload(RiwayatPresensi.data_karyawan)).all()

def get_riwayat_karyawan_by_id(id):
    return RiwayatPresensi.query.get(id)

def create_riwayat_karyawan_repository(data):
    karyawan = RiwayatPresensi(
       status=data.get("status"),
       waktu_dibuat=datetime.now(),
       gambar=data.get("gambar"),
       karyawan_id=data.get("karyawan_id"),
    )
    db.session.add(karyawan)
    db.session.commit()
    return karyawan

def delete_riwayat_karyawan_repository(karyawan_id):
    karyawan = RiwayatPresensi.query.get(karyawan_id)
    if karyawan:
        db.session.delete(karyawan)
        db.session.commit()
        return True
    return False