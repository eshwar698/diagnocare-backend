from models import DailyMetrics
from datetime import datetime
from sqlalchemy import func


def check_missed_glucose(user_id):

    today = datetime.utcnow().date()

    today_entry = DailyMetrics.query.filter(
        DailyMetrics.user_id == user_id,
        func.date(DailyMetrics.date) == today
    ).first()

    if today_entry:
        return {
            "status": "logged",
            "message": "Today's glucose already recorded"
        }

    return {
        "status": "missed",
        "message": "You have not logged glucose today"
    }