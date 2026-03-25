from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import User, UserProfile, DailyMetrics
from config import db
from utils.bmi import calculate_bmi

auth_bp = Blueprint("auth", __name__)


# ================= SIGNUP =================
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "User exists"}), 400

    user = User(
        email=data["email"],
        password=generate_password_hash(data["password"])
    )

    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "User created",
        "access_token": token
    })


# ================= LOGIN =================
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    token = create_access_token(identity=str(user.id))

    return jsonify({"access_token": token})


# ================= ONBOARDING =================
@auth_bp.route("/onboarding", methods=["POST"])
@jwt_required()
def onboarding():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    required = ["age", "height", "weight", "name"]

    for field in required:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    height = float(data["height"])
    weight = float(data["weight"])

    if height <= 0 or weight <= 0:
        return {"error": "Height and weight must be greater than 0"}, 400

    bmi = calculate_bmi(height, weight)

    # ✅ GET USER
    user = User.query.get(user_id)

    # ✅ SAVE BASIC + OPTIONAL FIELDS
    user.name = data.get("name")
    user.gender = data.get("gender")
    user.sleep = data.get("sleep")
    user.diet = data.get("diet")
    user.stress = data.get("stress")

    # ✅ PROFILE (UPDATE OR CREATE)
    profile = UserProfile.query.filter_by(user_id=user_id).first()

    if profile:
        profile.age = data["age"]
        profile.height = height
        profile.weight = weight
        profile.bmi = bmi
    else:
        profile = UserProfile(
            user_id=user_id,
            age=data["age"],
            height=height,
            weight=weight,
            bmi=bmi
        )
        db.session.add(profile)

    db.session.commit()

    return jsonify({
        "message": "Onboarding completed",
        "bmi": bmi
    })


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)
    profile = UserProfile.query.filter_by(user_id=user_id).first()

    return jsonify({
        "name": user.name if user and user.name else "User",

        "age": profile.age if profile else None,
        "height": profile.height if profile else None,
        "weight": profile.weight if profile else None,
        "bmi": profile.bmi if profile else None,

        # ✅ FIXED FIELDS
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

    UserProfile.query.filter_by(user_id=user_id).delete()
    DailyMetrics.query.filter_by(user_id=user_id).delete()
    User.query.filter_by(id=user_id).delete()

    db.session.commit()

    return jsonify({"message": "Account deleted"}), 200