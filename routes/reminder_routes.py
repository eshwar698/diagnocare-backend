from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.reminder_service import generate_reminders

reminder_bp = Blueprint("reminders", __name__)


@reminder_bp.route("/reminders", methods=["GET"])
@jwt_required()
def get_reminders():

    user_id = int(get_jwt_identity())

    reminders = generate_reminders(user_id)

    return jsonify(reminders)