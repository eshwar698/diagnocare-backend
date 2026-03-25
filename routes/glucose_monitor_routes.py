from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.glucose_monitor_service import check_missed_glucose
from datetime import datetime
from services.glucose_graph_service import get_monthly_glucose_graph
from config import db
from models import DailyMetrics
glucose_monitor_bp = Blueprint("glucose_monitor", __name__)


@glucose_monitor_bp.route("/missed-check", methods=["GET"])
@jwt_required()
def missed_glucose_check():

    user_id = int(get_jwt_identity())

    result = check_missed_glucose(user_id)

    return jsonify(result)

@glucose_monitor_bp.route("/monthly-glucose-graph", methods=["GET"])
@jwt_required()
def monthly_glucose_graph():

    user_id = int(get_jwt_identity())

    now = datetime.utcnow()

    graph_data = get_monthly_glucose_graph(
        user_id,
        now.year,
        now.month
    )

    return jsonify(graph_data)

@glucose_monitor_bp.route("/latest", methods=["GET"])
@jwt_required()
def latest_glucose():
    user_id = int(get_jwt_identity())

    from models import DailyMetrics

    latest = (
        DailyMetrics.query
        .filter_by(user_id=user_id)
        .order_by(DailyMetrics.timestamp.desc())
        .first()
    )

    if not latest:
        return jsonify({"message": "No data found"}), 404

    return jsonify({
        "glucose": latest.Glucose,
        "timestamp": latest.timestamp
    })

@glucose_monitor_bp.route("/add", methods=["POST"])
@jwt_required()
def add_glucose():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        value = data.get("value")

        if value is None:
            return jsonify({"error": "Glucose value required"}), 400

        new_entry = DailyMetrics(
            user_id=user_id,
            Glucose=value,
            date=datetime.utcnow(),
            timestamp=datetime.utcnow()
        )

        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"message": "Glucose added"}), 200

    except Exception as e:
        print("ADD GLUCOSE ERROR:", e)
        return jsonify({"error": "Something went wrong"}), 500