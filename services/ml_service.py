from services.suggestion_service import generate_explanations
import shap
from services.model_loader import get_model, get_label_encoder, get_feature_columns


def predict(feature_df):

    model = get_model()
    label_encoder = get_label_encoder()
    feature_columns = get_feature_columns()

    explainer = shap.TreeExplainer(model)

    # Model prediction
    prediction = model.predict(feature_df)[0]

    risk_label = label_encoder.inverse_transform([prediction])[0]

    # SHAP values
    shap_values = explainer.shap_values(feature_df)

    class_shap = shap_values[0, :, prediction]

    feature_impacts = dict(zip(feature_columns, class_shap))

    top_features = sorted(
        feature_impacts.items(),
        key=lambda x: abs(x[1]),
        reverse=True
    )[:3]

    top_features = [
        {"feature": f, "impact": float(v)}
        for f, v in top_features
    ]

    feature_names = [f["feature"] for f in top_features]

    explanations, suggestions = generate_explanations(feature_names)

    # 🚨 Emergency glucose detection
    emergency = None

    try:
        glucose_value = float(feature_df["glucose"].iloc[0])

        if glucose_value < 70:
            emergency = {
                "type": "low_glucose",
                "message": "Possible hypoglycemia detected. Consume fast-acting sugar (juice, glucose tablets) and recheck in 15 minutes."
            }

        elif glucose_value > 250:
            emergency = {
                "type": "high_glucose",
                "message": "Dangerously high glucose detected. Drink water, consider light activity if safe, and recheck soon."
            }

    except Exception:
        emergency = None

    return {
        "risk_level": risk_label,
        "top_contributors": top_features,
        "explanations": explanations,
        "suggestions": suggestions,
        "emergency": emergency
    }