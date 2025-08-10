from app.src.model.schemas.cctv import CCTV
from app import db
from datetime import datetime
def get_cctv_link_repository():
    # Lakukan query ke database untuk mendapatkan link CCTV
    data = CCTV.query.first()  
    return data

def update_cctv_link_repository(url):
    # Lakukan query ke database untuk memperbarui link CCTV
    data = CCTV.query.first()
    data.url = url
    data.updated_at = datetime.now()
    db.session.commit()
    return data