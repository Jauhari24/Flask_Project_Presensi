from datetime import datetime
from app import db
class CCTV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), default="http://xxx.xxx")
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow)