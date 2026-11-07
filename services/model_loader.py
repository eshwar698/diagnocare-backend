from pathlib import Path
import joblib

ARTIFACT_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = ARTIFACT_DIR / "temporal_xgb_model.pkl"
ENCODER_PATH = ARTIFACT_DIR / "label_encoder.pkl"
FEATURES_PATH = ARTIFACT_DIR / "feature_columns.pkl"

model = None
label_encoder = None
feature_columns = None


def load_model():
    """Load all required artifacts once; fail startup if any artifact is invalid."""
    global model, label_encoder, feature_columns

    if model is None or label_encoder is None or feature_columns is None:
        missing = [str(p) for p in (MODEL_PATH, ENCODER_PATH, FEATURES_PATH) if not p.is_file()]
        if missing:
            raise FileNotFoundError("Missing model artifact(s): " + ", ".join(missing))

        loaded_model = joblib.load(MODEL_PATH)
        loaded_encoder = joblib.load(ENCODER_PATH)
        loaded_columns = joblib.load(FEATURES_PATH)

        if not hasattr(loaded_model, "predict"):
            raise TypeError("Model artifact does not expose predict()")
        if not hasattr(loaded_encoder, "inverse_transform"):
            raise TypeError("Label encoder artifact is invalid")
        if not isinstance(loaded_columns, (list, tuple)) or not loaded_columns:
            # Some training scripts persist a pandas Index; accept it as iterable below.
            try:
                loaded_columns = list(loaded_columns)
            except Exception as exc:
                raise TypeError("Feature columns artifact is invalid") from exc
        else:
            loaded_columns = list(loaded_columns)

        if len(set(loaded_columns)) != len(loaded_columns):
            raise ValueError("Feature columns contain duplicates")

        model, label_encoder, feature_columns = loaded_model, loaded_encoder, loaded_columns

    return model, label_encoder, feature_columns


def get_model():
    if model is None:
        load_model()
    return model


def get_label_encoder():
    if label_encoder is None:
        load_model()
    return label_encoder


def get_feature_columns():
    if feature_columns is None:
        load_model()
    return feature_columns
