import os
from flask import Flask
from dotenv import load_dotenv

from app.models import db, User, Shipment
from app.routes.auth import auth_bp
from app.routes.main import main_bp
from app.routes.api import api_bp
from app.routes.rest import rest_bp
from app.seed import seed_default_data


def create_app():
    # Load environment variables from .env if present.
    load_dotenv()

    app = Flask(__name__)

    # Core Flask configuration and secure session secret.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me-in-production")

    # Database configuration: default SQLite for demo, easy MySQL switch.
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "sqlite:///supplychain.db",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # API keys used by frontend integrations.
    app.config["GOOGLE_MAPS_API_KEY"] = os.getenv(
        "GOOGLE_MAPS_API_KEY",
        "YOUR_GOOGLE_MAPS_API_KEY",
    )
    app.config["WEATHER_API_KEY"] = os.getenv(
        "WEATHER_API_KEY",
        "YOUR_WEATHER_API_KEY",
    )

    # Initialize the database extension.
    db.init_app(app)

    # Register modular route blueprints.
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(rest_bp)

    # Create schema and seed sample data on first run.
    with app.app_context():
        db.create_all()
        seed_default_data()

    # Expose API keys to templates globally.
    @app.context_processor
    def inject_global_values():
        return {
            "google_maps_api_key": app.config["GOOGLE_MAPS_API_KEY"],
            "weather_api_key": app.config["WEATHER_API_KEY"],
        }

    return app
