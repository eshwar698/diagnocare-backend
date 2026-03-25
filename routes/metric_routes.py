from datetime import datetime
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
    data = request.get_json()
    # Post-meal 2 hour validation
    mode = data.get("mode")

    if mode == "post":

        last_metric = DailyMetrics.query.filter_by(user_id=user_id)\
        .order_by(DailyMetrics.timestamp.desc())\
        .first()

    if last_metric:
        now = datetime.utcnow()
        time_diff = (now - last_metric.timestamp).total_seconds() / 3600

        if time_diff < 2:
            return jsonify({
                "warning": "Post-meal glucose should be checked 2 hours after eating",
                "minutes_remaining": int((2 - time_diff) * 60)
            }), 400
    # Medical safety validation
    glucose = float(data["Glucose"])

    if glucose < 30 or glucose > 600:
        return jsonify({"error": "Glucose value must be between 30 and 600 mg/dL"}), 400
    # Store metric
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

    db.session.add(metric)
    db.session.commit()

    # Build ML features
    feature_df, mode = build_features(user_id)

    if feature_df is None:
        return jsonify({"error": "Not enough data"}), 400

    # Run ML prediction
    prediction_result = predict(feature_df)

    # Calculate glucose trend
    trend = calculate_trend(user_id)

    # Get personal baseline
    baseline = get_user_baseline(user_id)

    baseline_difference = None
    if baseline is not None:
        current_glucose = data["Glucose"]
        baseline_difference = round(current_glucose - baseline, 2)

    # Generate health insights
    insights = generate_insights(
        baseline,
        data["Glucose"]
    )

    # Smart reminder learning
    recommended_times = learn_checking_pattern(user_id)

    # Emergency detection
    emergency_alert = check_emergency(
        data["Glucose"],
        data["BP"]
    )

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
    })
@metric_bp.route("/monthly-stats", methods=["GET"])
@jwt_required()
def monthly_stats():

    user_id = int(get_jwt_identity())

    now = datetime.utcnow()
    month = now.month
    year = now.year

    metrics = DailyMetrics.query.filter_by(user_id=user_id).all()

    monthly_values = []

    for m in metrics:
        if m.timestamp.month == month and m.timestamp.year == year:
            monthly_values.append(m.Glucose)

    if not monthly_values:
        return jsonify({"message": "No data for this month"}), 404

    avg_glucose = round(sum(monthly_values) / len(monthly_values), 2)
    max_glucose = max(monthly_values)
    min_glucose = min(monthly_values)

    trend = calculate_trend(user_id)

    return jsonify({
        "entries_this_month": len(monthly_values),
        "average_glucose": avg_glucose,
        "highest_glucose": max_glucose,
        "lowest_glucose": min_glucose,
        "trend": trend
    })