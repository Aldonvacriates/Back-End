from flask import current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from marshmallow import ValidationError
from sqlalchemy import select
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import limiter
from app.models import Member, db

from . import auth_bp
from .schemas import login_schema


def _verify_member_password(member, password):
    stored_password = member.password or ""

    if stored_password.startswith(("pbkdf2:", "scrypt:")):
        return check_password_hash(stored_password, password)

    if stored_password == password:
        member.password = generate_password_hash(password)
        db.session.commit()
        return True

    return False


@auth_bp.route("/login", methods=["POST"])
@limiter.limit(lambda: current_app.config["AUTH_LOGIN_RATE_LIMIT"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    try:
        credentials = login_schema.load(data)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Member).where(Member.email == credentials["email"])
    member = db.session.execute(query).scalars().first()

    if not member or not _verify_member_password(member, credentials["password"]):
        return jsonify({"error": "Invalid email or password."}), 401

    access_token = create_access_token(
        identity=str(member.id),
        additional_claims={"email": member.email},
    )
    refresh_token = create_refresh_token(identity=str(member.id))

    return (
        jsonify(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
            }
        ),
        200,
    )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@limiter.limit(lambda: current_app.config["AUTH_REFRESH_RATE_LIMIT"])
def refresh():
    member_id = int(get_jwt_identity())
    member = db.session.get(Member, member_id)

    if not member:
        return jsonify({"error": "Member not found."}), 404

    access_token = create_access_token(
        identity=str(member.id),
        additional_claims={"email": member.email},
    )

    return jsonify({"access_token": access_token, "token_type": "Bearer"}), 200
