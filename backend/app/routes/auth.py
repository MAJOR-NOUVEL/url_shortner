from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from pydantic import ValidationError

from app.extensions import db, limiter
from app.models.user import User
from app.schemas.auth import (
    LoginSchema,
    RegisterSchema,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
@limiter.limit("10 per minute")
def register():
    """Registers a new user account with bcrypt password hashing."""
    data = request.get_json(silent=True) or {}
    try:
        validated = RegisterSchema(**data)
    except ValidationError as e:
        formatted_errors = [{"field": ".".join(str(loc) for loc in err["loc"]), "message": err["msg"]} for err in e.errors()]
        return jsonify({"error": "Validation error", "details": formatted_errors}), 400

    # Check if user already exists
    if User.query.filter_by(email=validated.email).first():
        return jsonify({"error": "Email is already registered. Please log in."}), 409

    new_user = User(email=validated.email)
    new_user.set_password(validated.password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully.",
        "user": new_user.to_dict()
    }), 201

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    """Authenticates credentials and returns a signed JWT access token."""
    data = request.get_json(silent=True) or {}
    try:
        validated = LoginSchema(**data)
    except ValidationError as e:
        formatted_errors = [{"field": ".".join(str(loc) for loc in err["loc"]), "message": err["msg"]} for err in e.errors()]
        return jsonify({"error": "Validation error", "details": formatted_errors}), 400

    user = User.query.filter_by(email=validated.email).first()
    if not user or not user.check_password(validated.password):
        return jsonify({"error": "Invalid email or password."}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "access_token": access_token,
        "token_type": "Bearer",
        "user": user.to_dict()
    }), 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Returns profile for currently authenticated JWT identity."""
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    if not user:
        return jsonify({"error": "User not found."}), 404

    return jsonify({"user": user.to_dict()}), 200
