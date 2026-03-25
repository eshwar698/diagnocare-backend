from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import MedicineReminder
from config import db

medicine_bp = Blueprint("medicine", __name__)


@medicine_bp.route("/add", methods=["POST"])
@jwt_required()
def add_medicine():

    user_id = int(get_jwt_identity())

    data = request.get_json()

    medicine = MedicineReminder(
        user_id=user_id,
        medicine_name=data["medicine_name"],
        time=data["time"],
        before_food=data.get("before_food", False),
        after_food=data.get("after_food", False)
    )

    db.session.add(medicine)
    db.session.commit()

    return jsonify({"message": "Medicine reminder added"}), 201


@medicine_bp.route("/list", methods=["GET"])
@jwt_required()
def list_medicines():

    user_id = int(get_jwt_identity())

    medicines = MedicineReminder.query.filter_by(user_id=user_id).all()

    result = []

    for m in medicines:
        result.append({
            "id": m.id,
            "medicine_name": m.medicine_name,
            "time": m.time,
            "before_food": m.before_food,
            "after_food": m.after_food
        })

    return jsonify(result)


@medicine_bp.route("/delete/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_medicine(id):

    user_id = int(get_jwt_identity())

    medicine = MedicineReminder.query.filter_by(id=id, user_id=user_id).first()

    if not medicine:
        return jsonify({"error": "Medicine not found"}), 404

    db.session.delete(medicine)
    db.session.commit()

    return jsonify({"message": "Medicine deleted"})