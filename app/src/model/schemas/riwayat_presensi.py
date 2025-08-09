from app import db
from app.src.utils.get_timezone import get_timezone
class RiwayatPresensi(db.Model):
    __tablename__='data_presensi'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.Boolean, default=False)
    gambar = db.Column(db.String(255), nullable=True)
    waktu_dibuat = db.Column(db.DateTime(timezone=True), default=get_timezone)
     # FOREIGN KEY ke DataKaryawan
    
    karyawan_id = db.Column(db.Integer, db.ForeignKey('data_karyawan.id'))
    data_karyawan = db.relationship("DataKaryawan", backref="data_presensi")