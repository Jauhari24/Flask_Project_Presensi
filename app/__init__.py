from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import app.config as config
import os
import secrets
from flask_socketio import SocketIO

load_dotenv()
db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO(cors_allowed_origins="*") # Inisialisasi SocketIO

def create_app():
    load_dotenv()
    app = Flask(__name__)
     # 🔐 Gunakan SECRET_KEY dari env jika ada, jika tidak, generate random
    app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)
    app.config.from_object(config)
    app.config['SQLALCHEMY_DATABASE_URI'] = '{driver}://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4'.format(
    driver=app.config['DB_DRIVER'],
    user=app.config['DB_USER'],
    password=app.config['DB_PASSWORD'],
    host=app.config['DB_HOST'],
    port=app.config['DB_PORT'],
    database=app.config['DB_NAME'],
    )

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app) # Pasang SocketIO ke Flask app
    from app.src.model.schemas import DataKaryawan,RiwayatPresensi
    
        
    
    from app.src.routes.main import main
    from app.src.routes.auth import auth
    from app.src.routes.users import users
    from app.src.routes.card import card
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(card)

    return app