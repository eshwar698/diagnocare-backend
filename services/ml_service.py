import logging
import numpy as np
import pandas as pd
import shap

from services.suggestion_service import generate_explanations
from services.model_loader import get_model, get_label_encoder, get_feature_columns

logger = logging.getLogger(__name__)


def _class_shap_values(shap_values, class_index, n_features):
    """Normalize SHAP's common multi-class output layouts to (features,)."""
    values = getattr(shap_values, "values", shap_values)
    values = np.asarray(values)

    # SHAP versions may return list[class] arrays or ndarray/Explanation.
    if isinstance(shap_values, list):
        values = np.asarray(shap_values[class_index])
    elif values.ndim == 3:
        # Common layouts: (samples, features, classes) or (classes, samples, features)
        if values.shape[0] == 1 and values.shape[1] == n_features:
            values = values[0, :, class_index]
        elif values.shape[0] > class_index and values.shape[2] == n_features:
            values = values[class_index, 0, :]
        else:
            raise ValueError(f"Unsupported SHAP shape: {values.shape}")
    elif values.ndim == 2:
        if values.shape[0] == 1 and values.shape[1] == n_features:
            values = values[0]
        else:
            raise ValueError(f"Unsupported SHAP shape: {values.shape}")
    else:
        raise ValueError(f"Unsupported SHAP shape: {values.shape}")

    values = np.asarray(values).reshape(-1)
    if values.size != n_features:
        raise ValueError(f"SHAP returned {values.size} values for {n_features} features")
    return values


def predict(feature_df):
    model = get_model()
    label_encoder = get_label_encoder()
    feature_columns = get_feature_columns()

    if not isinstance(feature_df, pd.DataFrame) or feature_df.empty:
        raise ValueError("Prediction input must be a non-empty DataFrame")
    missing = [c for c in feature_columns if c not in feature_df.columns]
    if missing:
        raise ValueError("Missing model features: " + ", ".join(missing))

    # Force the training-time order and numeric finite input.
    X = feature_df.loc[:, feature_columns].copy()
    X = X.apply(pd.to_numeric, errors="raise")
    if not np.isfinite(X.to_numpy(dtype=float)).all():
        raise ValueError("Prediction input contains NaN or infinite values")

    prediction = int(model.predict(X)[0])
    risk_label = str(label_encoder.inverse_transform([prediction])[0])

    explainer = shap.TreeExplainer(model)
    raw_shap = explainer.shap_values(X)
    class_shap = _class_shap_values(raw_shap, prediction, len(feature_columns))
    impacts = dict(zip(feature_columns, class_shap))
    top_features = [
        {"feature": str(name), "impact": float(value)}
        for name, value in sorted(impacts.items(), key=lambda item: abs(item[1]), reverse=True)[:3]
    ]

    explanations, suggestions = generate_explanations([item["feature"] for item in top_features])

    emergency = None
    glucose_column = next((c for c in ("Glucose", "glucose") if c in X.columns), None)
    if glucose_column:
        glucose = float(X[glucose_column].iloc[0])
        if glucose < 70:
            emergency = {
                "type": "low_glucose",
                "message": "Low glucose reading detected. Follow your clinician-provided hypoglycemia plan and recheck as directed."
            }
        elif glucose > 250:
            emergency = {
                "type": "high_glucose",
                "message": "High glucose reading detected. Follow your clinician-provided care plan; seek urgent care if severe symptoms occur."
            }

    return {
        "risk_level": risk_label,
        "top_contributors": top_features,
        "explanations": explanations,
        "suggestions": suggestions,
        "emergency": emergency,
    }
