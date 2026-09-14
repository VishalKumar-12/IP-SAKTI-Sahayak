import re

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from backend.extensions import db
from backend.models import User


auth_bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_signup(data):
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name:
        return "Name is required."

    if not email or not EMAIL_RE.match(email):
        return "A valid email is required."

    if not password or len(password) < 6:
        return "Password must be at least 6 characters long."

    return None


@auth_bp.route("/auth/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}

    error = _validate_signup(data)
    if error:
        return jsonify({"success": False, "error": error}), 400

    email = data.get("email").strip().lower()
    name = data.get("name").strip()
    password = data.get("password")

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({
            "success": False,
            "error": "An account with this email already exists."
        }), 409

    user = User(name=name, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=user.id)

    return jsonify({
        "success": True,
        "token": token,
        "user": user.to_dict()
    }), 201


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({
            "success": False,
            "error": "Email and password are required."
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({
            "success": False,
            "error": "Invalid email or password."
        }), 401

    token = create_access_token(identity=user.id)

    return jsonify({
        "success": True,
        "token": token,
        "user": user.to_dict()
    })


@auth_bp.route("/auth/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"success": False, "error": "User not found."}), 404

    return jsonify({"success": True, "user": user.to_dict()})
