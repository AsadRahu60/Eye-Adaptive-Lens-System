def classify(distance_cm: float, lux: float, motion: float) -> str:
    if distance_cm and distance_cm < 60:
        return "near"
    if lux and lux > 5000:
        return "outdoor"
    return "desk"
