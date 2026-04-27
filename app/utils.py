from functools import wraps
from flask import session, jsonify, redirect, url_for, flash
from app.models import User


def get_current_user():
    # Resolve signed-in user from Flask session.
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def login_required(view):
    # Route guard for browser pages.
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view


def api_login_required(view):
    # Route guard for JSON APIs.
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return view(*args, **kwargs)

    return wrapped_view


def admin_api_required(view):
    # Restrict API actions to admin users only.
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        if session.get("user_role") != "admin":
            return jsonify({"error": "Forbidden: admin only"}), 403
        return view(*args, **kwargs)

    return wrapped_view
