from datetime import datetime, timedelta
from models import MedicineReminder, DoctorAppointment, DailyMetrics


def generate_reminders(user_id):

    reminders = []

    now = datetime.utcnow()

    # Medicine reminders
    medicines = MedicineReminder.query.filter_by(user_id=user_id).all()

    for med in medicines:
        reminders.append({
            "type": "medicine",
            "message": f"Time to take {med.medicine_name}",
            "time": med.time,
            "before_food": med.before_food,
            "after_food": med.after_food
        })

    # Appointment reminders
    appointments = DoctorAppointment.query.filter_by(user_id=user_id).all()

    for app in appointments:
        reminders.append({
            "type": "appointment",
            "message": f"Doctor appointment with {app.doctor_name}",
            "date": app.appointment_date,
            "time": app.appointment_time
        })

    # Missed entry reminder (no glucose today)
    today = now.date()

    today_entry = DailyMetrics.query.filter(
        DailyMetrics.user_id == user_id,
        DailyMetrics.date >= datetime(today.year, today.month, today.day)
    ).first()

    if not today_entry:
        reminders.append({
            "type": "health",
            "message": "You haven't logged your glucose reading today"
        })

    return reminders