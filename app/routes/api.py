from datetime import datetime
from flask import Blueprint, jsonify, request

from app.models import db, Shipment, Alert
from app.services.risk_engine import calculate_risk
from app.services.route_optimizer import suggest_route
from app.utils import api_login_required, admin_api_required


api_bp = Blueprint("api", __name__, url_prefix="/api")


def _status_from_risk(risk_level):
    # Normalizes status label shown in UI.
    if risk_level == "High":
        return "Risk"
    if risk_level == "Medium":
        return "Delayed"
    return "On-time"


@api_bp.route("/dashboard")
@api_login_required
def dashboard_stats():
    # Aggregated statistics for dashboard cards.
    shipments = Shipment.query.all()
    total = len(shipments)
    active = len([s for s in shipments if s.status in {"On-time", "Delayed", "Risk"}])
    delayed = len([s for s in shipments if s.status == "Delayed"])
    high_risk = len([s for s in shipments if s.risk_level == "High"])

    return jsonify(
        {
            "total_shipments": total,
            "active_shipments": active,
            "delayed_shipments": delayed,
            "high_risk_alerts": high_risk,
        }
    )


@api_bp.route("/shipments", methods=["GET"])
@api_login_required
def get_shipments():
    # Returns shipments enriched with risk and route optimization output.
    payload = []
    for shipment in Shipment.query.order_by(Shipment.id.asc()).all():
        risk = calculate_risk(
            shipment.weather_condition,
            shipment.traffic_level,
            shipment.eta_delay_minutes,
        )
        route = suggest_route(shipment)

        shipment.risk_level = risk["risk_level"]
        shipment.status = _status_from_risk(risk["risk_level"])

        payload.append(
            {
                "id": shipment.id,
                "source": shipment.source,
                "destination": shipment.destination,
                "status": shipment.status,
                "location": shipment.location,
                "risk_level": shipment.risk_level,
                "risk_percentage": risk["risk_percentage"],
                "risk_reason": risk["risk_reason"],
                "weather_condition": shipment.weather_condition,
                "traffic_level": shipment.traffic_level,
                "eta_delay_minutes": shipment.eta_delay_minutes,
                "current_lat": shipment.current_lat,
                "current_lng": shipment.current_lng,
                "destination_lat": shipment.destination_lat,
                "destination_lng": shipment.destination_lng,
                "current_route": route["current_route"],
                "optimized_route": route["optimized_route"],
                "route_note": route["route_note"],
            }
        )

    db.session.commit()
    return jsonify(payload)


@api_bp.route("/shipments", methods=["POST"])
@admin_api_required
def add_shipment():
    # Admin endpoint for creating new shipment records.
    payload = request.get_json(silent=True) or {}
    required_fields = {"source", "destination", "location", "current_lat", "current_lng"}
    if not required_fields.issubset(payload.keys()):
        return jsonify({"error": "Missing required shipment fields"}), 400

    shipment = Shipment(
        source=payload["source"],
        destination=payload["destination"],
        location=payload["location"],
        status=payload.get("status", "On-time"),
        risk_level=payload.get("risk_level", "Low"),
        current_lat=float(payload["current_lat"]),
        current_lng=float(payload["current_lng"]),
        destination_lat=float(payload.get("destination_lat", payload["current_lat"])),
        destination_lng=float(payload.get("destination_lng", payload["current_lng"])),
        weather_condition=payload.get("weather_condition", "clear"),
        traffic_level=payload.get("traffic_level", "light"),
        eta_delay_minutes=int(payload.get("eta_delay_minutes", 0)),
    )
    db.session.add(shipment)
    db.session.commit()
    return jsonify({"message": "Shipment added", "id": shipment.id}), 201


@api_bp.route("/shipments/<int:shipment_id>", methods=["PUT"])
@admin_api_required
def update_shipment(shipment_id):
    # Admin endpoint for updating existing shipments.
    shipment = Shipment.query.get_or_404(shipment_id)
    payload = request.get_json(silent=True) or {}
    allowed_fields = {
        "source", "destination", "location", "status", "risk_level",
        "current_lat", "current_lng", "destination_lat", "destination_lng",
        "weather_condition", "traffic_level", "eta_delay_minutes",
    }
    for field, value in payload.items():
        if field in allowed_fields:
            setattr(shipment, field, value)

    db.session.commit()
    return jsonify({"message": "Shipment updated"})


@api_bp.route("/shipments/<int:shipment_id>", methods=["DELETE"])
@admin_api_required
def delete_shipment(shipment_id):
    # Admin endpoint for deleting shipments.
    shipment = Shipment.query.get_or_404(shipment_id)
    db.session.delete(shipment)
    db.session.commit()
    return jsonify({"message": "Shipment deleted"})


@api_bp.route("/alerts", methods=["GET"])
@api_login_required
def get_alerts():
    # Generates alerts and returns them with shipment coordinates for map plotting.
    shipments = Shipment.query.all()

    for shipment in shipments:
        risk = calculate_risk(
            shipment.weather_condition,
            shipment.traffic_level,
            shipment.eta_delay_minutes,
        )
        should_alert = risk["risk_level"] in {"Medium", "High"}

        if should_alert:
            message = f"Shipment {shipment.id}: {risk['risk_reason']} ({risk['risk_percentage']}% risk)"
            exists = Alert.query.filter_by(shipment_id=shipment.id, message=message).first()
            if not exists:
                alert_type = "Weather alert" if "weather" in risk["risk_reason"].lower() else "Delay alert"
                if "traffic" in risk["risk_reason"].lower():
                    alert_type = "Route change alert"
                db.session.add(
                    Alert(
                        shipment_id=shipment.id,
                        message=message,
                        alert_type=alert_type,
                        timestamp=datetime.utcnow(),
                    )
                )

    db.session.commit()

    alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(50).all()
    payload = []
    for alert in alerts:
        shipment = Shipment.query.get(alert.shipment_id)
        if not shipment:
            continue

        payload.append(
            {
                "id": alert.id,
                "shipment_id": alert.shipment_id,
                "message": alert.message,
                "alert_type": alert.alert_type,
                "timestamp": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "lat": shipment.current_lat,
                "lng": shipment.current_lng,
                "risk": shipment.risk_level.upper(),
                "risk_level": shipment.risk_level,
            }
        )

    return jsonify(payload)


# REST aliases requested in assignment.
@api_bp.route("/login", methods=["POST"])
def login_alias():
    return jsonify({"message": "Use /login endpoint for browser or JSON auth."}), 200


@api_bp.route("/register", methods=["POST"])
def register_alias():
    return jsonify({"message": "Use /register endpoint for browser or JSON registration."}), 200
