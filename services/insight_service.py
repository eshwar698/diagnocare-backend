def generate_insights(baseline, latest):

    if baseline is None:
        return []

    insights = []

    diff = latest - baseline
    percent = (diff / baseline) * 100

    if percent > 20:
        insights.append(
            f"Your glucose is {percent:.1f}% higher than your personal baseline."
        )

    elif percent < -15:
        insights.append(
            "Your glucose levels are significantly lower than usual."
        )

    else:
        insights.append(
            "Your glucose levels are close to your normal baseline."
        )

    return insights