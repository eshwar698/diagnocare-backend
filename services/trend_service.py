from models import DailyMetrics


def calculate_trend(user_id):

    metrics = DailyMetrics.query.filter_by(user_id=user_id)\
        .order_by(DailyMetrics.timestamp.desc())\
        .limit(7).all()

    if len(metrics) < 3:
        return "insufficient_data"

    # Reverse so oldest → newest
    values = [m.Glucose for m in reversed(metrics)]

    first = values[0]
    last = values[-1]

    if last > first + 15:
        return "increasing"

    elif last < first - 15:
        return "decreasing"

    else:
        return "stable"