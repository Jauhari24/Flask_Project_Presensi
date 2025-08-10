from app import db
from datetime import datetime
from sqlalchemy.orm import joinedload
from app.src.model.schemas.data_karyawan import DataKaryawan
from app.src.model.schemas.gambar import Gambar
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

def get_karyawan_by_rfid_id(rfid_id):
    return (
        DataKaryawan.query
        .options(joinedload(DataKaryawan.gambar))  # load relasi gambar
        .filter_by(id_kartu=rfid_id)
        .first()
    )

def create_karyawan_repository(data):
    """
    Create user with finger_id from MQTT
    """
    user = DataKaryawan(
       nama=data.get("nama"),
       id_kartu=data.get("id_kartu"),
       waktu_dibuat=datetime.now(),
    )
    db.session.add(user)
    db.session.commit()

    # Setelah user dibuat, simpan gambar (bisa 1 atau lebih)
    images = data.get("gambar")  # Bisa string (satu gambar) atau list

    if isinstance(images, list):
        for img_path in images:
            image = Gambar(
                data_karyawan_id=user.id,
                name=img_path,
            )
            db.session.add(image)
    elif isinstance(images, str):  # Kalau hanya 1 gambar (bukan list)
        image = Gambar(
            data_karyawan_id=user.id,
            name=images,
        )
        db.session.add(image)
        
    db.session.commit()
    return user
