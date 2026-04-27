def suggest_route(shipment):
    """
    Simple route optimization output.
    In production this can be replaced with Google Directions API logic.
    """
    current_route = f"{shipment.source} -> Main Highway Corridor -> {shipment.destination}"

    traffic_level = (shipment.traffic_level or "").lower()
    weather = (shipment.weather_condition or "").lower()

    if traffic_level == "heavy" or weather in {"storm", "heavy-rain", "snow"}:
        optimized_route = f"{shipment.source} -> Ring Road Bypass -> {shipment.destination}"
        route_note = "Optimized route avoids heavy traffic/weather impact zones."
    else:
        optimized_route = current_route
        route_note = "Current route is already optimal."

    return {
        "current_route": current_route,
        "optimized_route": optimized_route,
        "route_note": route_note,
    }
