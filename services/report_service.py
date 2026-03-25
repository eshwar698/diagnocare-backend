from models import DailyMetrics
from sqlalchemy import extract


def generate_monthly_report(user_id, year, month):

    metrics = DailyMetrics.query.filter(
        DailyMetrics.user_id == user_id,
        extract("year", DailyMetrics.date) == year,
        extract("month", DailyMetrics.date) == month
    ).order_by(DailyMetrics.date).all()

    if not metrics:
        return None

    glucose_values = [m.Glucose for m in metrics if m.Glucose is not None]

    if not glucose_values:
        return None

    entries = len(glucose_values)

    avg_glucose = sum(glucose_values) / entries
    highest = max(glucose_values)
    lowest = min(glucose_values)

    # --- Risk Trend Calculation (NEW FEATURE) ---

    first_glucose = glucose_values[0]
    last_glucose = glucose_values[-1]

    difference = last_glucose - first_glucose

    if difference < -10:
        trend = "Improving"
    elif difference > 10:
        trend = "Worsening"
    else:
        trend = "Stable"

    # -------------------------------------------

    return {
        "entries": entries,
        "average_glucose": round(avg_glucose, 2),
        "highest_glucose": highest,
        "lowest_glucose": lowest,
        "risk_trend": trend
    }