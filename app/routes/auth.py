from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.models import db, User
from app.utils import get_current_user


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # Handles both browser form registration and JSON API registration.
    if request.method == "POST":
        payload = request.get_json(silent=True) or request.form

        name = payload.get("name", "").strip()
        email = payload.get("email", "").strip().lower()
        password = payload.get("password", "")
        role = payload.get("role", "user")

        if not all([name, email, password]):
            if request.is_json:
                return jsonify({"error": "name, email and password are required"}), 400
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({"error": "Email already exists"}), 409
            flash("Email already exists.", "warning")
            return redirect(url_for("auth.register"))

        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        if request.is_json:
            return jsonify({"message": "Registration successful"}), 201

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", current_user=get_current_user())


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Login with secure password validation and session creation.
    if request.method == "POST":
        payload = request.get_json(silent=True) or request.form

        email = payload.get("email", "").strip().lower()
        password = payload.get("password", "")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            if request.is_json:
                return jsonify({"error": "Invalid credentials"}), 401
            flash("Invalid credentials.", "danger")
            return redirect(url_for("auth.login"))

        session["user_id"] = user.id
        session["user_role"] = user.role
        session["user_name"] = user.name

        if request.is_json:
            return jsonify({"message": "Login successful", "role": user.role}), 200

        return redirect(url_for("main.dashboard"))

    return render_template("login.html", current_user=get_current_user())


@auth_bp.route("/logout")
def logout():
    # Clear all session data on logout.
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))
