from datetime import datetime
from math import isfinite

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import DailyMetrics
from config import db

from services.feature_engineering import build_features
from services.ml_service import predict
from services.trend_service import calculate_trend
from services.baseline_service import get_user_baseline
from services.reminder_ai_service import learn_checking_pattern
from services.emergency_service import check_emergency
from services.insight_service import generate_insights

metric_bp = Blueprint("metrics", __name__)


@metric_bp.route("/add-metrics", methods=["POST"])
@jwt_required()
def add_metrics():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    mode = data.get("mode")
    if mode not in {"pre", "post"}:
        return jsonify({"error": "mode must be 'pre' or 'post'"}), 400

    # Apply the 2-hour check only to post-meal measurements.
    if mode == "post":
        last_metric = (
            DailyMetrics.query.filter_by(user_id=user_id)
            .order_by(DailyMetrics.timestamp.desc())
            .first()
        )
        if last_metric and last_metric.timestamp:
            now = datetime.utcnow()
            time_diff = (now - last_metric.timestamp).total_seconds() / 3600
            if time_diff < 2:
                return jsonify({
                    "warning": "Post-meal glucose should be checked 2 hours after eating",
                    "minutes_remaining": max(0, int((2 - time_diff) * 60))
                }), 400

    # Validate required fields and numeric glucose.
    if "Glucose" not in data:
        return jsonify({"error": "Glucose is required"}), 400
    try:
        glucose = float(data["Glucose"])
        if not isfinite(glucose):
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "Glucose must be a valid number"}), 400

    if glucose < 30 or glucose > 600:
        return jsonify({"error": "Glucose value must be between 30 and 600 mg/dL"}), 400

    # BP and Insulin are retained as the existing API fields.
    if "BP" not in data or "Insulin" not in data:
        return jsonify({"error": "BP and Insulin are required"}), 400

    metric = DailyMetrics(
        user_id=user_id,
        Glucose=glucose,
        BP=data["BP"],
        Insulin=data["Insulin"],
        Physical_activity_minutes=data.get("Physical_activity_minutes"),
        Sleep_duration=data.get("Sleep_duration"),
        Stress_score=data.get("Stress_score"),
        LDL=data.get("LDL"),
        HDL=data.get("HDL"),
        Triglycerides=data.get("Triglycerides"),
        Creatinine=data.get("Creatinine"),
        CRP=data.get("CRP"),
    )

    try:
        db.session.add(metric)
        db.session.flush()

        feature_df, feature_mode = build_features(user_id)
        if feature_df is None:
            return jsonify({"error": "Not enough data"}), 400

        prediction_result = predict(feature_df)
        trend = calculate_trend(user_id)
        baseline = get_user_baseline(user_id)

        baseline_difference = None
        if baseline is not None:
            baseline_difference = round(glucose - baseline, 2)

        insights = generate_insights(baseline, glucose)
        recommended_times = learn_checking_pattern(user_id)
        emergency_alert = check_emergency(glucose, data["BP"])
        db.session.commit()
        return jsonify({
            "risk_level": prediction_result["risk_level"],
            "mode": mode,
            "trend": trend,
            "baseline_glucose": baseline,
            "difference_from_baseline": baseline_difference,
            "insights": insights,
            "recommended_check_times": recommended_times,
            "top_contributors": prediction_result["top_contributors"],
            "explanations": prediction_result["explanations"],
            "suggestions": prediction_result["suggestions"],
            "emergency": emergency_alert
        }), 200

    except Exception:
        db.session.rollback()
        # Log detailed exception server-side; avoid exposing internals to clients.
        import logging
        logging.getLogger(__name__).exception("Metric submission/processing failed")
        return jsonify({"error": "Metric submission failed. Please try again."}), 500


@metric_bp.route("/monthly-stats", methods=["GET"])
@jwt_required()
def monthly_stats():
    user_id = int(get_jwt_identity())

    now = datetime.utcnow()
    metrics = DailyMetrics.query.filter_by(user_id=user_id).all()
    monthly_values = [
        m.Glucose for m in metrics
        if m.timestamp and m.timestamp.month == now.month
        and m.timestamp.year == now.year and m.Glucose is not None
    ]

    if not monthly_values:
        return jsonify({"message": "No data for this month"}), 404

    return jsonify({
        "entries_this_month": len(monthly_values),
        "average_glucose": round(sum(monthly_values) / len(monthly_values), 2),
        "highest_glucose": max(monthly_values),
        "lowest_glucose": min(monthly_values),
        "trend": calculate_trend(user_id)
    }), 200
