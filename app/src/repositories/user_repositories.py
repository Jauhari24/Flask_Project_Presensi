from app import db
from app.src.model.schemas.data_karyawan import DataKaryawan
from datetime import datetime
def get_all_karyawan_repository():
    return DataKaryawan.query.all()
def get_karyawan_by_id_repository(karyawan_id):
    return DataKaryawan.query.get(karyawan_id)

def create_karyawan_repository(data):
    karyawan = DataKaryawan(
        nama=data.get("nama"),
        id_kartu=data.get("id_kartu"),
        foto=data.get("foto"),
        
    )
    db.session.add(karyawan)
    db.session.commit()
    return karyawan

def update_karyawan_repository(karyawan_id, data):
    karyawan = DataKaryawan.query.get(karyawan_id)
    if karyawan:
        karyawan.nama = data.get("nama")
        karyawan.id_kartu = data.get("id_kartu")
        karyawan.foto = data.get("foto")
        karyawan.waktu_diubah = datetime.now()
        db.session.commit()
        return karyawan
    return None 

def delete_karyawan_repository(karyawan_id):
    karyawan = DataKaryawan.query.get(karyawan_id)
    if karyawan:
        db.session.delete(karyawan)
        db.session.commit()
        return True
    return False