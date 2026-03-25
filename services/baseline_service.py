from models import DailyMetrics
import numpy as np


def get_user_baseline(user_id):

    metrics = DailyMetrics.query.filter_by(user_id=user_id)\
        .order_by(DailyMetrics.timestamp.desc())\
        .limit(30).all()

    # Need enough readings to calculate baseline
    if len(metrics) < 5:
        return None

    values = [m.Glucose for m in metrics]

    baseline = float(np.mean(values))

    return baseline