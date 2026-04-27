from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


# Shared SQLAlchemy instance for all models.
db = SQLAlchemy()


class User(db.Model):
    # User authentication and authorization table.
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")

    def set_password(self, plain_password):
        self.password = generate_password_hash(plain_password)

    def check_password(self, plain_password):
        return check_password_hash(self.password, plain_password)


class Shipment(db.Model):
    # Shipment status, location, and disruption-related fields.
    __tablename__ = "shipments"

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(120), nullable=False)
    destination = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="On-time")
    location = db.Column(db.String(120), nullable=False)
    risk_level = db.Column(db.String(20), nullable=False, default="Low")

    current_lat = db.Column(db.Float, nullable=False)
    current_lng = db.Column(db.Float, nullable=False)
    destination_lat = db.Column(db.Float, nullable=False)
    destination_lng = db.Column(db.Float, nullable=False)

    weather_condition = db.Column(db.String(30), nullable=False, default="clear")
    traffic_level = db.Column(db.String(30), nullable=False, default="light")
    eta_delay_minutes = db.Column(db.Integer, nullable=False, default=0)

    alerts = db.relationship("Alert", backref="shipment", lazy=True, cascade="all, delete-orphan")


class Alert(db.Model):
    # Alert records for dashboard and operational notifications.
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey("shipments.id"), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    alert_type = db.Column(db.String(30), nullable=False, default="Delay alert")
