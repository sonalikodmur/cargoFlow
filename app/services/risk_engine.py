def calculate_risk(weather_condition, traffic_level, eta_delay_minutes):
    """
    Rule-based disruption prediction logic.
    Keeps logic intentionally simple and explainable for demo use.
    """
    score = 10
    reasons = []

    normalized_weather = (weather_condition or "").lower()
    normalized_traffic = (traffic_level or "").lower()

    # Weather impact rules.
    if normalized_weather in {"storm", "heavy-rain", "snow"}:
        score += 55
        reasons.append("Bad weather detected")
    elif normalized_weather in {"rain", "windy"}:
        score += 25
        reasons.append("Moderate weather risk")

    # Traffic impact rules.
    if normalized_traffic == "heavy":
        score += 30
        reasons.append("Heavy traffic in current route")
    elif normalized_traffic == "moderate":
        score += 15
        reasons.append("Moderate traffic slowdown")

    # Delay impact rules.
    if eta_delay_minutes >= 45:
        score += 20
        reasons.append("Long ETA delay trend")
    elif eta_delay_minutes >= 20:
        score += 10
        reasons.append("Rising delay indicator")

    score = min(score, 99)

    if score >= 75:
        risk_level = "High"
    elif score >= 45:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    if not reasons:
        reasons.append("Conditions normal")

    return {
        "risk_percentage": score,
        "risk_level": risk_level,
        "risk_reason": ", ".join(reasons),
    }
