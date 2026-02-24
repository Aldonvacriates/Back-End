from .schemas import member_schema, members_schema
from flask import request,jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Member, db
from . import members_bp

# -------Routes--------


# Create a new member
@members_bp.route("/", methods=["POST"])
def create_member():
    try:
        member_data = member_schema.load(
            request.json
        )  # validate and deserialize the input data
    except ValidationError as e:
        return jsonify(e.messages), 400  # return validation errors if any

    query = select(Member).where(
        Member.email == member_data["email"]
    )  # check if a member with the same email already exists
    existing_member = db.session.execute(query).scalars().all()
    if existing_member:
        return jsonify({"error": "Email already associated with an account."}), 400

    new_member = Member(
        **member_data
    )  # create a new Member instance with the validated data
    db.session.add(new_member)  # add the new member to the session
    db.session.commit()  # commit the session to save the new member to the database
    return member_schema.jsonify(new_member), 201


# GET ALL MEMBERS
@members_bp.route("/", methods=["GET"])
def get_members():
    query = select(Member)  # query to select all members
    members = (
        db.session.execute(query).scalars().all()
    )  # execute the query and fetch all members

    return members_schema.jsonify(members)


# GET SPECIFIC MEMBERS
@members_bp.route("/<int:member_id>", methods=["GET"])
def get_member(member_id):
    member = db.session.get(Member, member_id)

    if member:
        return member_schema.jsonify(member), 200
    return jsonify({"error": "Member not found."}), 404


# UPDATE SPECIFIC USER
@members_bp.route("/<int:member_id>", methods=["PUT"])
def update_member(member_id):
    member = db.session.get(Member, member_id)

    if not member:
        return jsonify({"error": "Member not found."}), 404

    try:
        member_data = member_schema.load(
            request.json, partial=True
        )  # validate and deserialize the input data, allowing for partial updates
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in member_data.items():
        setattr(member, key, value)

    db.session.commit()
    return member_schema.jsonify(member), 200


# DELETE SPECIFIC USER
@members_bp.route("/<int:member_id>", methods=["DELETE"])
def delete_member(member_id):
    member = db.session.get(Member, member_id)

    if not member:
        return jsonify({"error": "Member not found."}), 404

    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": f"Member id: {member_id}, deleted successfully."}), 200
