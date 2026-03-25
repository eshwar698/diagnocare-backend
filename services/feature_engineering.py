import pandas as pd
from models import UserProfile, DailyMetrics
from services.model_loader import get_feature_columns




def build_features(user_id):
    feature_columns = get_feature_columns()
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    metrics = DailyMetrics.query.filter_by(user_id=user_id)\
        .order_by(DailyMetrics.date.asc()).all()

    if not profile or not metrics:
        return None, "Not enough data"

    df = pd.DataFrame([m.__dict__ for m in metrics])
    df = df.drop(columns=["_sa_instance_state"])

    df["Age"] = profile.age
    df["BMI"] = profile.bmi

    optional_cols = [
        "Physical_activity_minutes","Sleep_duration","Stress_score",
        "LDL","HDL","Triglycerides","Creatinine","CRP"
    ]

    for col in optional_cols:
        if col not in df:
            df[col] = 0

    df = df.fillna(0)

    if len(df) >= 7:

        df["Glucose_mean_7d"] = df["Glucose"].rolling(7).mean()
        df["Glucose_std_7d"] = df["Glucose"].rolling(7).std()
        df["Glucose_trend_7d"] = df["Glucose"].diff().rolling(7).mean()

        mode = "temporal"

    else:

        df["Glucose_mean_7d"] = df["Glucose"]
        df["Glucose_std_7d"] = 0
        df["Glucose_trend_7d"] = 0

        mode = "snapshot"

    latest = df.iloc[-1:].copy()

    for col in feature_columns:
        if col not in latest:
            latest[col] = 0

    feature_df = latest[feature_columns].copy()
    feature_df = feature_df.fillna(0)
    feature_df = feature_df.astype("float32")

    return feature_df, mode