from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import UserProfile, User
from config import db
from utils.bmi import calculate_bmi

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    profile = UserProfile.query.filter_by(user_id=user_id).first()
    user = User.query.get(user_id)
    if not profile or not user:
        return jsonify({"error": "Profile not found"}), 404

    try:
        if "name" in data:
            if not isinstance(data["name"], str) or not data["name"].strip():
                return jsonify({"error": "Name must be a non-empty string"}), 400
            user.name = data["name"].strip()

        if data.get("age") is not None:
            age = int(data["age"])
            if age < 10 or age > 120:
                return jsonify({"error": "Age must be between 10 and 120"}), 400
            profile.age = age

        if data.get("height") is not None:
            height = float(data["height"])
            if not 100 <= height <= 250:
                return jsonify({"error": "Height must be between 100cm and 250cm"}), 400
            profile.height = height

        if data.get("weight") is not None:
            weight = float(data["weight"])
            if not 30 <= weight <= 300:
                return jsonify({"error": "Weight must be between 30kg and 300kg"}), 400
            profile.weight = weight

    except (TypeError, ValueError):
        return jsonify({"error": "Age, height, and weight must be valid numbers"}), 400

    if "gender" in data:
        if data["gender"] not in ["Male", "Female", "Other"]:
            return jsonify({"error": "Invalid gender"}), 400
        user.gender = data["gender"]
        profile.gender = data["gender"]

    if "sleep" in data:
        user.sleep = str(data["sleep"])
    if "diet" in data:
        user.diet = data["diet"]
    if "stress" in data:
        user.stress = str(data["stress"])

    if profile.height and profile.weight:
        profile.bmi = calculate_bmi(profile.height, profile.weight)

    db.session.commit()
    return jsonify({"message": "Profile updated"}), 200
