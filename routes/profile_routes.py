from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import UserProfile, User
from config import db
from utils.bmi import calculate_bmi

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():

    user_id = int(get_jwt_identity())

    profile = UserProfile.query.filter_by(user_id=user_id).first()

    if not profile:
        return jsonify({"error": "Profile not found"}), 404

    return jsonify({
        "age": profile.age,
        "height": profile.height,
        "weight": profile.weight,
        "bmi": profile.bmi,
        "gender": profile.gender
    })


@profile_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():

    user_id = int(get_jwt_identity())
    data = request.get_json()

    profile = UserProfile.query.filter_by(user_id=user_id).first()
    user = User.query.get(user_id)
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    if "name" in data and data["name"]:
        user.name = data["name"]
    # Age validation
    if "age" in data and data["age"] is not None:
        age = int(data["age"])
        if age < 10 or age > 120:
            return jsonify({"error": "Age must be between 10 and 120"}), 400
        profile.age = age

    # Height validation
    if "height" in data and data["height"] is not None:
        height = float(data["height"])
        if height < 100 or height > 250:
            return jsonify({"error": "Height must be between 100cm and 250cm"}), 400
        profile.height = height

    # Weight validation
    if "weight" in data and data["weight"] is not None:
        weight = float(data["weight"])
        if weight < 30 or weight > 300:
            return jsonify({"error": "Weight must be between 30kg and 300kg"}), 400
        profile.weight = weight

    # Gender validation
    allowed = ["Male", "Female", "Other"]
    if "gender" in data:
        if data["gender"] not in allowed:
            return jsonify({"error": "Invalid gender"}), 400
        user.gender = data["gender"]
    # Optional fields
    if "sleep" in data:
        user.sleep = str(data["sleep"])

    if "diet" in data:
        user.diet = data["diet"]

    if "stress" in data:
        user.stress = str(data["stress"])
    # Recalculate BMI if height or weight changed
    if profile.height and profile.weight:
        profile.bmi = calculate_bmi(profile.height, profile.weight)

    db.session.commit()

    return jsonify({
        "message": "Profile updated"
    })