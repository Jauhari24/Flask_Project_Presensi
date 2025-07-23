from app import db
from app.src.utils.get_timezone import get_timezone
class DataKaryawan(db.Model):
    __tablename__='data_karyawan'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.Float)
    jabatan = db.Column(db.Float)
    id_kartu = db.Column(db.Integer, primary_key=True)
    foto = db.Column(db.Float)
    status = db.Column(db.Boolean, default=False)
    waktu_dibuat = db.Column(db.DateTime(timezone=True), default=get_timezone)
    waktu_diubah = db.Column(db.DateTime(timezone=True), default=get_timezone)