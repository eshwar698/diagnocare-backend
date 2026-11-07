import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    # Set this in deployment to your frontend origin(s), comma-separated.
    allowed_origins = os.environ.get("CORS_ORIGINS", "*")
    origins = [origin.strip() for origin in allowed_origins.split(",") if origin.strip()]
    CORS(app, origins=origins)

    # Supports SQLite by default and PostgreSQL/MySQL URLs via DATABASE_URL.
    default_db = "sqlite:///health.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", default_db)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    jwt_secret = os.environ.get("JWT_SECRET_KEY")
    if not jwt_secret:
        raise RuntimeError("JWT_SECRET_KEY environment variable must be configured")
    app.config["JWT_SECRET_KEY"] = jwt_secret

    db.init_app(app)
    jwt.init_app(app)
    return app
