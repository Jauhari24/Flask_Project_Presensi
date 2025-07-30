from app.src.repositories.user_repositories import get_all_karyawan_repository
from app.src.repositories.riwayat_presensi_repositories import get_all_riwayat_karyawan_repository

def serialize_datetime(dt):
    return dt.isoformat() if dt else None

def serialize_model(instance, fields):
    return {field: serialize_datetime(getattr(instance, field)) if "waktu" in field else getattr(instance, field) for field in fields}

def get_all_karyawan_service():
    raw_data = get_all_karyawan_repository()
    return [
        serialize_model(item, ["id", "nama", "id_kartu", "foto", "waktu_dibuat", "waktu_diubah"])
        for item in raw_data
    ]

def get_all_riwayat_karyawan_service():
    raw_data = get_all_riwayat_karyawan_repository()
    return [
        {
            "id": item.id,
            "status": item.status,
            "waktu_dibuat": serialize_datetime(item.waktu_dibuat),
            "data_karyawan": serialize_model(item.data_karyawan, ["id", "nama", "id_kartu", "foto"])
        }
        for item in raw_data
    ]
