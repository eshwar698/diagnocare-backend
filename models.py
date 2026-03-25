from config import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name= db.Column(db.String(100), nullable=True)
    gender= db.Column(db.String(10), nullable=True)
    sleep = db.Column(db.String(50), nullable=True) 
    diet = db.Column(db.String(50), nullable=True) 
    stress = db.Column(db.String(50), nullable=True)
class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    age = db.Column(db.Integer)
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    bmi = db.Column(db.Float)
    gender = db.Column(db.String(10))
    sleep=db.Column(db.String(50))
    diet=db.Column(db.String(50))
    stress=db.Column(db.String(50))

class DailyMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    Glucose = db.Column(db.Float)
    BP = db.Column(db.Float)
    Insulin = db.Column(db.Float)

    Physical_activity_minutes = db.Column(db.Float)
    Sleep_duration = db.Column(db.Float)
    Stress_score = db.Column(db.Float)
    LDL = db.Column(db.Float)
    HDL = db.Column(db.Float)
    Triglycerides = db.Column(db.Float)
    Creatinine = db.Column(db.Float)
    CRP = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class MedicineReminder(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    medicine_name = db.Column(db.String(120), nullable=False)

    time = db.Column(db.String(10), nullable=False)

    before_food = db.Column(db.Boolean, default=False)

    after_food = db.Column(db.Boolean, default=False)

class DoctorAppointment(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    doctor_name = db.Column(db.String(120), nullable=False)

    appointment_date = db.Column(db.String(20), nullable=False)

    appointment_time = db.Column(db.String(10), nullable=False)

    notes = db.Column(db.String(255))