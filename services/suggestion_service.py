
FEATURE_EXPLANATIONS = {
    "Glucose": "Recent glucose readings are high",
    "Glucose_last": "Your latest glucose reading is contributing to your risk level",
    "Glucose_3d_avg_last": "Your recent 3-day average glucose is contributing to your risk level",
    "glucose_3d_avg": "Your glucose levels have been elevated over the past few days",
    "HDL_mean": "Your average HDL cholesterol level is contributing to your risk assessment",
    "Sleep_duration": "You may not be getting enough sleep",
    "Stress_score": "Stress levels are higher than usual",
    "Physical_activity_minutes": "Physical activity levels are low",
    "BP": "Blood pressure readings are elevated",
    "Insulin": "Insulin levels are outside the usual range",
}

FEATURE_SUGGESTIONS = {
    "Glucose": "Consider reducing sugar intake and monitoring your glucose more frequently",
    "Glucose_last": "Follow your prescribed glucose monitoring plan and discuss persistent abnormal readings with your clinician",
    "Glucose_3d_avg_last": "Review your recent glucose trends with your healthcare provider",
    "glucose_3d_avg": "Try adding light exercise like a short walk after meals",
    "HDL_mean": "Discuss cholesterol management, physical activity, and dietary choices with your healthcare provider",
    "Sleep_duration": "Aim for at least 7 hours of sleep",
    "Stress_score": "Consider relaxation techniques or light activity",
    "Physical_activity_minutes": "Try a 10-minute walk today",
    "BP": "Monitor blood pressure and reduce sodium intake",
    "Insulin": "Check insulin timing and consult your doctor if needed",
}


def generate_explanations(top_features):
    explanations = []
    suggestions = []

    for feature in top_features:
        explanation = FEATURE_EXPLANATIONS.get(feature)
        suggestion = FEATURE_SUGGESTIONS.get(feature)

        if explanation:
            explanations.append({
                "feature": feature,
                "explanation": explanation,
            })

        if suggestion:
            suggestions.append({
                "feature": feature,
                "suggestion": suggestion,
            })

    return explanations, suggestions
