from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from models import User, UserProfile, DailyMetrics, MedicineReminder, DoctorAppointment
from config import db
from utils.bmi import calculate_bmi

auth_bp = Blueprint("auth", __name__)


def _json_body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = _json_body()
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    email = data.get("email")
    password = data.get("password")
    if not isinstance(email, str) or not email.strip():
        return jsonify({"error": "A valid email is required"}), 400
    if not isinstance(password, str) or len(password) < 8:
        return jsonify({"error": "Password must contain at least 8 characters"}), 400

    email = email.strip().lower()
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User exists"}), 409

    user = User(email=email, password=generate_password_hash(password))
    try:
        db.session.add(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Unable to create account"}), 500

    token = create_access_token(identity=str(user.id))
    return jsonify({"message": "User created", "access_token": token}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = _json_body()
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    email = data.get("email")
    password = data.get("password")
    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email.strip().lower()).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    return jsonify({"access_token": create_access_token(identity=str(user.id))}), 200


@auth_bp.route("/onboarding", methods=["POST"])
@jwt_required()
def onboarding():
    user_id = int(get_jwt_identity())
    data = _json_body()
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    for field in ["age", "height", "weight", "name"]:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Name must be a non-empty string"}), 400

    try:
        age = int(data["age"])
        height = float(data["height"])
        weight = float(data["weight"])
    except (TypeError, ValueError):
        return jsonify({"error": "Age, height, and weight must be numeric"}), 400

    if not 10 <= age <= 120:
        return jsonify({"error": "Age must be between 10 and 120"}), 400
    if not 100 <= height <= 250:
        return jsonify({"error": "Height must be between 100cm and 250cm"}), 400
    if not 30 <= weight <= 300:
        return jsonify({"error": "Weight must be between 30kg and 300kg"}), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    bmi = calculate_bmi(height, weight)
    user.name = name.strip()
    user.gender = data.get("gender")
    user.sleep = data.get("sleep")
    user.diet = data.get("diet")
    user.stress = data.get("stress")

    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if profile is None:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)

    profile.age = age
    profile.height = height
    profile.weight = weight
    profile.bmi = bmi
    if user.gender is not None:
        profile.gender = user.gender

    db.session.commit()
    return jsonify({"message": "Onboarding completed", "bmi": bmi}), 200


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    profile = UserProfile.query.filter_by(user_id=user_id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "name": user.name or "User",
        "age": profile.age if profile else None,
        "height": profile.height if profile else None,
        "weight": profile.weight if profile else None,
        "bmi": profile.bmi if profile else None,
        "gender": user.gender,
        "sleep": user.sleep,
        "diet": user.diet,
        "stress": user.stress,
        "check_frequency": getattr(profile, "check_frequency", None),
    }), 200


@auth_bp.route("/delete", methods=["DELETE"])
@jwt_required()
def delete_account():
    user_id = int(get_jwt_identity())

    try:
        # Delete every user-owned row explicitly; current schema has no FK cascades
        # for these tables. Always scope deletes to the authenticated user.
        DoctorAppointment.query.filter_by(user_id=user_id).delete(synchronize_session=False)
        MedicineReminder.query.filter_by(user_id=user_id).delete(synchronize_session=False)
        DailyMetrics.query.filter_by(user_id=user_id).delete(synchronize_session=False)
        UserProfile.query.filter_by(user_id=user_id).delete(synchronize_session=False)
        User.query.filter_by(id=user_id).delete(synchronize_session=False)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Account deletion failed"}), 500

    return jsonify({"message": "Account deleted"}), 200
