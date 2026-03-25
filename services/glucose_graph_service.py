from models import DailyMetrics
from sqlalchemy import extract


def get_monthly_glucose_graph(user_id, year, month):

    metrics = DailyMetrics.query.filter(
        DailyMetrics.user_id == user_id,
        extract("year", DailyMetrics.date) == year,
        extract("month", DailyMetrics.date) == month
    ).order_by(DailyMetrics.date).all()

    graph_data = []

    for m in metrics:

        if m.Glucose is not None:

            graph_data.append({
                "day": m.date.day,
                "glucose": m.Glucose
            })

    return graph_data