from models import DailyMetrics
from collections import Counter


def learn_checking_pattern(user_id):

    metrics = DailyMetrics.query.filter_by(user_id=user_id).all()

    # Need enough data to learn pattern
    if len(metrics) < 10:
        return []

    # Extract hours from timestamps
    hours = [m.timestamp.hour for m in metrics if m.timestamp]

    if not hours:
        return []

    # Find most common hours
    common_hours = Counter(hours).most_common(3)

    # Return only the hour values
    recommended_hours = [hour for hour, count in common_hours]

    return recommended_hours