from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import DailyMetrics
from datetime import datetime
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
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    doctor_name = data.get("doctor_name")
    appointment_date = data.get("date")
    appointment_time = data.get("time")

    if not isinstance(doctor_name, str) or not doctor_name.strip():
        return jsonify({"error": "doctor_name is required"}), 400

    if not isinstance(appointment_date, str) or not appointment_date.strip():
        return jsonify({"error": "date is required"}), 400

    if not isinstance(appointment_time, str) or not appointment_time.strip():
        return jsonify({"error": "time is required"}), 400

    try:
        parsed_date = datetime.strptime(
            appointment_date.strip(), "%Y-%m-%d"
        ).date()

        if parsed_date < datetime.now().date():
            return jsonify({
            "error": "Appointment date cannot be in the past"
            }), 400

    except ValueError:
        return jsonify({"error": "Date must be YYYY-MM-DD"}), 400

    try:
        datetime.strptime(appointment_time.strip(), "%H:%M")
    except ValueError:
        return jsonify({"error": "Time must be HH:MM"}), 400

    try:
        appointment = DoctorAppointment(
            user_id=user_id,
            doctor_name=doctor_name.strip(),
            appointment_date=appointment_date.strip(),
            appointment_time=appointment_time.strip(),
            notes=data.get("notes", "")
        )

        db.session.add(appointment)
        db.session.commit()

        return jsonify({"message": "Appointment added"}), 201

    except Exception:
        db.session.rollback()

        import logging
        logging.getLogger(__name__).exception(
            "Appointment creation failed"
        )

        return jsonify({"error": "Unable to create appointment"}), 500




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