from datetime import datetime
from app.models import db, User, Shipment, Alert
from app.services.risk_engine import calculate_risk


def seed_default_data():
    # Seed users only if user table is empty.
    if User.query.count() == 0:
        admin = User(name="Admin User", email="admin@supplychain.com", role="admin")
        admin.set_password("admin123")

        user = User(name="Ops User", email="user@supplychain.com", role="user")
        user.set_password("user123")

        db.session.add_all([admin, user])
        db.session.commit()

    # Seed shipment + alert demo data on first run.
    if Shipment.query.count() == 0:
        sample_shipments = [
            Shipment(
                source="Mumbai",
                destination="Pune",
                status="On-time",
                location="Navi Mumbai",
                risk_level="Low",
                current_lat=19.0760,
                current_lng=72.8777,
                destination_lat=18.5204,
                destination_lng=73.8567,
                weather_condition="clear",
                traffic_level="light",
                eta_delay_minutes=5,
            ),
            Shipment(
                source="Delhi",
                destination="Jaipur",
                status="Delayed",
                location="Gurugram",
                risk_level="Medium",
                current_lat=28.4595,
                current_lng=77.0266,
                destination_lat=26.9124,
                destination_lng=75.7873,
                weather_condition="rain",
                traffic_level="moderate",
                eta_delay_minutes=30,
            ),
            Shipment(
                source="Bengaluru",
                destination="Chennai",
                status="Risk",
                location="Hosur",
                risk_level="High",
                current_lat=12.7409,
                current_lng=77.8253,
                destination_lat=13.0827,
                destination_lng=80.2707,
                weather_condition="storm",
                traffic_level="heavy",
                eta_delay_minutes=60,
            ),
        ]
        db.session.add_all(sample_shipments)
        db.session.commit()

        alerts = []
        for shipment in Shipment.query.all():
            risk = calculate_risk(
                shipment.weather_condition,
                shipment.traffic_level,
                shipment.eta_delay_minutes,
            )
            shipment.risk_level = risk["risk_level"]
            if risk["risk_level"] in {"Medium", "High"}:
                alerts.append(
                    Alert(
                        shipment_id=shipment.id,
                        message=f"{shipment.source} to {shipment.destination}: {risk['risk_reason']}",
                        timestamp=datetime.utcnow(),
                        alert_type="Weather alert" if "weather" in risk["risk_reason"].lower() else "Delay alert",
                    )
                )

        db.session.add_all(alerts)
        db.session.commit()
