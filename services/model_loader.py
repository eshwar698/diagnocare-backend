import joblib

# Global cached objects
model = None
label_encoder = None
feature_columns = None


def load_model():

    global model, label_encoder, feature_columns

    if model is None:
        model = joblib.load("temporal_xgb_model.pkl")

    if label_encoder is None:
        label_encoder = joblib.load("label_encoder.pkl")

    if feature_columns is None:
        feature_columns = joblib.load("feature_columns.pkl")


def get_model():
    return model


def get_label_encoder():
    return label_encoder


def get_feature_columns():
    return feature_columns