from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select

from app.models import Member, db
from . import members_bp
from .schemas import member_schema, members_schema


@members_bp.route("/", methods=["POST"])
def create_member():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    try:
        member_data = member_schema.load(data)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Member).where(Member.email == member_data["email"])
    existing_member = db.session.execute(query).scalars().first()

    if existing_member:
        return jsonify({"error": "Email already associated with an account."}), 400

    new_member = Member(**member_data)
    db.session.add(new_member)
    db.session.commit()

    return jsonify(member_schema.dump(new_member)), 201


@members_bp.route("/", methods=["GET"])
def get_members():
    query = select(Member)
    members = db.session.execute(query).scalars().all()
    return jsonify(members_schema.dump(members)), 200


@members_bp.route("/<int:member_id>", methods=["GET"])
def get_member(member_id):
    member = db.session.get(Member, member_id)

    if not member:
        return jsonify({"error": "Member not found."}), 404

    return jsonify(member_schema.dump(member)), 200


@members_bp.route("/<int:member_id>", methods=["PUT"])
def update_member(member_id):
    member = db.session.get(Member, member_id)

    if not member:
        return jsonify({"error": "Member not found."}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    try:
        member_data = member_schema.load(data, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    if "email" in member_data:
        query = select(Member).where(
            Member.email == member_data["email"], Member.id != member_id
        )
        existing_member = db.session.execute(query).scalars().first()
        if existing_member:
            return (
                jsonify({"error": "Email already associated with another account."}),
                400,
            )

    for key, value in member_data.items():
        setattr(member, key, value)

    db.session.commit()
    return jsonify(member_schema.dump(member)), 200


@members_bp.route("/<int:member_id>", methods=["DELETE"])
def delete_member(member_id):
    member = db.session.get(Member, member_id)

    if not member:
        return jsonify({"error": "Member not found."}), 404

    db.session.delete(member)
    db.session.commit()

    return jsonify({"message": f"Member id: {member_id}, deleted successfully."}), 200
