from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import DailyMetrics

calendar_bp = Blueprint("calendar", __name__)


@calendar_bp.route("/history", methods=["GET"])
@jwt_required()
def history():

    user_id = int(get_jwt_identity())

    metrics = DailyMetrics.query.filter_by(user_id=user_id).all()

    result = []

    for m in metrics:

        result.append({
            "date": m.date,
            "Glucose": m.Glucose,
            "BP": m.BP,
            "Insulin": m.Insulin
        })

    return jsonify(result)
from flask import request
from models import DoctorAppointment
from config import db


@calendar_bp.route("/add-appointment", methods=["POST"])
@jwt_required()
def add_appointment():

    user_id = int(get_jwt_identity())

    data = request.get_json()

    appointment = DoctorAppointment(
        user_id=user_id,
        doctor_name=data["doctor_name"],
        appointment_date=data["date"],
        appointment_time=data["time"],
        notes=data.get("notes", "")
    )

    db.session.add(appointment)
    db.session.commit()

    return jsonify({"message": "Appointment added"}), 201


@calendar_bp.route("/appointments", methods=["GET"])
@jwt_required()
def get_appointments():

    user_id = int(get_jwt_identity())

    appointments = DoctorAppointment.query.filter_by(user_id=user_id).all()

    result = []

    for a in appointments:

        result.append({
            "id": a.id,
            "doctor_name": a.doctor_name,
            "date": a.appointment_date,
            "time": a.appointment_time,
            "notes": a.notes
        })

    return jsonify(result)


@calendar_bp.route("/delete-appointment/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_appointment(id):

    user_id = int(get_jwt_identity())

    appointment = DoctorAppointment.query.filter_by(id=id, user_id=user_id).first()

    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404

    db.session.delete(appointment)
    db.session.commit()

    return jsonify({"message": "Appointment deleted"})