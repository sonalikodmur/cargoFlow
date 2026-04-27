from flask import Blueprint, render_template
from app.utils import login_required, get_current_user


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    # Redirect-like landing by rendering login when unauthenticated.
    return render_template("index.html", current_user=get_current_user())


@main_bp.route("/dashboard")
@login_required
def dashboard():
    # Main operational dashboard page.
    return render_template("dashboard.html", current_user=get_current_user())


@main_bp.route("/tracking")
@login_required
def tracking():
    # Shipment tracking page with map and route comparison.
    return render_template("tracking.html", current_user=get_current_user())
