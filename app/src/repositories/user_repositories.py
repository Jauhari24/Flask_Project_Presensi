from app import db
from app.src.model.schemas.data_karyawan import DataKaryawan
from datetime import datetime
from sqlalchemy.orm import joinedload
from app.src.model.schemas.data_karyawan import DataKaryawan

def get_all_karyawan_repository():
    return (
        DataKaryawan.query
        .options(joinedload(DataKaryawan.gambar))  # load relasi gambar
        .all()
    )

def get_karyawan_by_id_repository(karyawan_id):
    return (
        DataKaryawan.query
        .options(joinedload(DataKaryawan.gambar))  # load relasi gambar
        .get(karyawan_id)
    )


def create_riwayat_karyawan_repository(data):
    riwayat = RiwayatPresensi(
        status=data.get("status"),
        waktu_dibuat=datetime.now(),
        karyawan_id=data.get("karyawan_id"),
    )
    db.session.add(riwayat)
    db.session.commit()
    return riwayat

def delete_riwayat_karyawan_repository(karyawan_id):
    riwayat = RiwayatPresensi.query.get(karyawan_id)
    if riwayat:
        db.session.delete(riwayat)
        db.session.commit()
        return True
    return False