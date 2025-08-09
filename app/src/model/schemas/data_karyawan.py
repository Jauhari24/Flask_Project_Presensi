from app import db
from app.src.utils.get_timezone import get_timezone
class DataKaryawan(db.Model):
    __tablename__='data_karyawan'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String(250), nullable=False) 
    id_kartu = db.Column(db.String(50), unique=True, nullable=False)  # ✅ ubah dari Integer ke String
    gambar =  db.relationship('Gambar', backref='data_karyawan', lazy=True)
    waktu_dibuat = db.Column(db.DateTime(timezone=True), default=get_timezone)
    waktu_diubah = db.Column(db.DateTime(timezone=True), default=get_timezone)