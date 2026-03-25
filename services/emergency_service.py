def check_emergency(glucose, bp):

    alerts = []

    if glucose >= 300:
        alerts.append("Critical glucose level detected. Seek medical help immediately.")

    elif glucose >= 200:
        alerts.append("Glucose level is very high. Monitor closely.")

    if bp >= 140:
        alerts.append("Blood pressure is dangerously high.")

    if len(alerts) == 0:
        return None

    return alerts