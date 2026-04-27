from flask import Blueprint
from app.routes.api import get_shipments, get_alerts


# Assignment-compatible REST endpoints without /api prefix.
rest_bp = Blueprint("rest", __name__)


@rest_bp.route("/shipments", methods=["GET"])
def shipments_alias():
    return get_shipments()


@rest_bp.route("/alerts", methods=["GET"])
def alerts_alias():
    return get_alerts()
