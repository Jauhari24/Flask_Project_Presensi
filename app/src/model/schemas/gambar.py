from datetime import datetime
from app import db

class Gambar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    data_karyawan_id = db.Column(db.Integer, db.ForeignKey('data_karyawan.id'), nullable=False)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)