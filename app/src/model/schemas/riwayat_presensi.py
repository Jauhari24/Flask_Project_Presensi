from app import db
from app.src.utils.get_timezone import get_timezone
class RiwayatPresensi(db.Model):
    __tablename__='data_presensi'
    id = db.Column(db.Integer, primary_key=True)
    waktu_masuk = db.Column(db.DateTime(timezone=True), default=get_timezone)
    waktu_keluar = db.Column(db.DateTime(timezone=True), default=get_timezone)
    status = db.Column(db.Boolean, default=False)
    waktu_dibuat = db.Column(db.DateTime(timezone=True), default=get_timezone)
    waktu_diubah = db.Column(db.DateTime(timezone=True), default=get_timezone)