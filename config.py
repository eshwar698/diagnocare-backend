import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()


def _database_url():
    url = os.environ.get("DATABASE_URL", "sqlite:///health.db")
    # Railway and some providers still expose postgres:// URLs.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    return url


def create_app():
    app = Flask(__name__)

    origins_raw = os.environ.get("CORS_ORIGINS", "*")
    origins = [origin.strip() for origin in origins_raw.split(",") if origin.strip()]
    CORS(app, origins=origins, supports_credentials=False)

    app.config["SQLALCHEMY_DATABASE_URI"] = _database_url()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    jwt_secret = os.environ.get("JWT_SECRET_KEY")
    if not jwt_secret:
        raise RuntimeError("JWT_SECRET_KEY environment variable must be configured")
    app.config["JWT_SECRET_KEY"] = jwt_secret

    db.init_app(app)
    jwt.init_app(app)
    return app
