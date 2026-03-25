def calculate_bmi(height_cm, weight_kg):
    if height_cm <= 0 or weight_kg <= 0:
        return 0  # or None

    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)