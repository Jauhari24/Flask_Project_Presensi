from app.src.repositories.riwayat_presensi_repositories import get_all_riwayat_karyawan_repository

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

