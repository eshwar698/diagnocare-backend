import numpy as np
import joblib
import shap

# =====================================
# LOAD SAVED ARTIFACTS
# =====================================
model = joblib.load("temporal_xgb_model.pkl")
label_encoder = joblib.load("label_encoder.pkl")
feature_columns = joblib.load("feature_columns.pkl")

# Initialize SHAP explainer once
explainer = shap.Explainer(model)


# =====================================
# PREDICTION FUNCTION
# =====================================
def predict_risk(input_dict):
    """
    input_dict must contain ALL features used in training.
    Example:
    {
        "Glucose": 180,
        "BMI": 29,
        ...
    }
    """

    # Ensure correct feature order
    input_data = np.array([[input_dict[col] for col in feature_columns]])

    # ===============================
    # MODEL PREDICTION
    # ===============================
    pred_class = model.predict(input_data)[0]
    risk_label = label_encoder.inverse_transform([pred_class])[0]

    probabilities = model.predict_proba(input_data)[0]
    confidence = float(np.max(probabilities))

    # ===============================
    # SHAP EXPLANATION
    # ===============================
    shap_values = explainer(input_data)

    # Shape: (n_samples, n_features, n_classes)
    shap_class_values = shap_values.values[0, :, pred_class]

    # Pair features with shap values
    feature_impacts = list(zip(feature_columns, shap_class_values))

    # Sort by absolute impact
    feature_impacts_sorted = sorted(
        feature_impacts,
        key=lambda x: abs(x[1]),
        reverse=True
    )

    # Convert numpy floats to Python floats (important for JSON)
    top_features = [
        (feature, float(value))
        for feature, value in feature_impacts_sorted[:5]
    ]

    # ===============================
    # IMPROVED CLINICAL EXPLANATION
    # ===============================
    explanation_lines = []
    for feature, value in top_features:
        impact_strength = round(abs(value), 3)
        direction = "increased" if value > 0 else "decreased"

        explanation_lines.append(
            f"{feature} {direction} probability of '{risk_label}' classification "
            f"(impact magnitude: {impact_strength})"
        )

    explanation_text = "Top contributing factors:\n" + "\n".join(explanation_lines)

    return {
        "risk_level": risk_label,
        "confidence": round(confidence, 3),
        "top_features": top_features,
        "explanation": explanation_text
    }


# =====================================
# LOCAL TEST BLOCK
# =====================================
if __name__ == "__main__":

    # Dummy input (replace with real values)
    sample_input = {col: 0 for col in feature_columns}

    result = predict_risk(sample_input)

    print("\nPrediction Result:")
    print(result)