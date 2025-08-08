from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import Config
from app.extensions import db
from app.routes.readings import readings_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this in production
    jwt = JWTManager(app)
    CORS(app)
    db.init_app(app)

    app.register_blueprint(readings_bp)

    return app
