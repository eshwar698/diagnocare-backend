from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    CORS(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///health.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")

    db.init_app(app)
    jwt.init_app(app)

    return app
