
from pathlib import Path
import joblib

ARTIFACT_DIR = Path(__file__).resolve().parent.parent

model = None
label_encoder = None
feature_columns = None


def load_model():
    global model, label_encoder, feature_columns

    if model is None:
        model = joblib.load(ARTIFACT_DIR / "temporal_xgb_model.pkl")

    if label_encoder is None:
        label_encoder = joblib.load(ARTIFACT_DIR / "label_encoder.pkl")

    if feature_columns is None:
        feature_columns = joblib.load(ARTIFACT_DIR / "feature_columns.pkl")

    return model, label_encoder, feature_columns


def get_model():
    return model


def get_label_encoder():
    return label_encoder


def get_feature_columns():
    return feature_columns
