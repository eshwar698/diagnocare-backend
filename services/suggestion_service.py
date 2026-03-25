FEATURE_EXPLANATIONS = {
    "Glucose": "Recent glucose readings are high",
    "glucose_3d_avg": "Your glucose levels have been elevated over the past few days",
    "Sleep_duration": "You may not be getting enough sleep",
    "Stress_score": "Stress levels are higher than usual",
    "Physical_activity_minutes": "Physical activity levels are low",
    "BP": "Blood pressure readings are elevated",
    "Insulin": "Insulin levels are outside the usual range"
}


FEATURE_SUGGESTIONS = {
    "Glucose": "Consider reducing sugar intake and monitoring your glucose more frequently",
    "glucose_3d_avg": "Try adding light exercise like a short walk after meals",
    "Sleep_duration": "Aim for at least 7 hours of sleep",
    "Stress_score": "Consider relaxation techniques or light activity",
    "Physical_activity_minutes": "Try a 10-minute walk today",
    "BP": "Monitor blood pressure and reduce sodium intake",
    "Insulin": "Check insulin timing and consult your doctor if needed"
}


def generate_explanations(top_features):

    explanations = []
    suggestions = []

    for feature in top_features:

        if feature in FEATURE_EXPLANATIONS:
            explanations.append(FEATURE_EXPLANATIONS[feature])

        if feature in FEATURE_SUGGESTIONS:
            suggestions.append(FEATURE_SUGGESTIONS[feature])

    return explanations, suggestions