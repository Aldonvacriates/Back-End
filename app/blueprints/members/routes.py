# Import request object to read incoming HTTP data
# jsonify is used to return JSON responses
from flask import request, jsonify

# ValidationError is raised when Marshmallow validation fails
from marshmallow import ValidationError

# SQLAlchemy select query helper
from sqlalchemy import select

# Import Member model and database instance
from app.models import Member, db

# Import the Blueprint for members routes
from . import members_bp
from .schemas import member_schema, members_schema

from app.extensions import limiter

# ---------------------------------------------------
# CREATE MEMBER
# ---------------------------------------------------
# Endpoint: POST /members
# Creates a new member in the database
@members_bp.route("/", methods=["POST"])
def create_member():

    # Get JSON data sent in the request body
    data = request.get_json()

    # Validate that the request contains JSON
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    try:
        # Validate and deserialize input data using Marshmallow schema
        member_data = member_schema.load(data)

    # If validation fails return the error messages
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Check if the email already exists in the database
    query = select(Member).where(Member.email == member_data["email"])
    existing_member = db.session.execute(query).scalars().first()

    # Prevent duplicate emails
    if existing_member:
        return jsonify({"error": "Email already associated with an account."}), 400

    # Create a new Member object using the validated data
    new_member = Member(**member_data)

    # Add the new member to the database session
    db.session.add(new_member)

    # Commit transaction to permanently save the record
    db.session.commit()

    # Return the created member as JSON
    return jsonify(member_schema.dump(new_member)), 201


# ---------------------------------------------------
# GET ALL MEMBERS
# ---------------------------------------------------
# Endpoint: GET /members
# Returns a list of all members
@members_bp.route("/", methods=["GET"])
@limiter.limit("3 per hour") # Apply rate limit to this endpoint
def get_members():

    # Create query to select all members
    query = select(Member)

    # Execute query and return all results
    members = db.session.execute(query).scalars().all()

    # Serialize members list using Marshmallow schema
    return jsonify(members_schema.dump(members)), 200


# ---------------------------------------------------
# GET ONE MEMBER
# ---------------------------------------------------
# Endpoint: GET /members/<member_id>
# Returns a single member by ID
@members_bp.route("/<int:member_id>", methods=["GET"])
def get_member(member_id):

    # Retrieve member by primary key
    member = db.session.get(Member, member_id)

    # Return error if member does not exist
    if not member:
        return jsonify({"error": "Member not found."}), 404

    # Return the member data
    return jsonify(member_schema.dump(member)), 200


# ---------------------------------------------------
# UPDATE MEMBER
# ---------------------------------------------------
# Endpoint: PUT /members/<member_id>
# Updates an existing member
@members_bp.route("/<int:member_id>", methods=["PUT"])
@limiter.limit("3 per hour") # Apply rate limit to this endpoint
def update_member(member_id):

    # Retrieve member from database
    member = db.session.get(Member, member_id)

    # Return error if member does not exist
    if not member:
        return jsonify({"error": "Member not found."}), 404

    # Get JSON request body
    data = request.get_json()

    # Validate request body
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    try:
        # Validate and partially update fields (partial=True allows missing fields)
        member_data = member_schema.load(data, partial=True)

    except ValidationError as e:
        return jsonify(e.messages), 400

    # If email is being updated we must check uniqueness
    if "email" in member_data:

        query = select(Member).where(
            Member.email == member_data["email"],  # same email
            Member.id != member_id,  # but different user
        )

        existing_member = db.session.execute(query).scalars().first()

        # Prevent duplicate email
        if existing_member:
            return (
                jsonify({"error": "Email already associated with another account."}),
                400,
            )

    # Update each field dynamically
    for key, value in member_data.items():
        setattr(member, key, value)

    # Save changes to database
    db.session.commit()

    # Return updated member
    return jsonify(member_schema.dump(member)), 200


# ---------------------------------------------------
# DELETE MEMBER
# ---------------------------------------------------
# Endpoint: DELETE /members/<member_id>
# Removes a member from the database
@members_bp.route("/<int:member_id>", methods=["DELETE"])
def delete_member(member_id):

    # Retrieve member
    member = db.session.get(Member, member_id)

    # Return error if member does not exist
    if not member:
        return jsonify({"error": "Member not found."}), 404

    # Delete member from database
    db.session.delete(member)

    # Commit deletion
    db.session.commit()

    # Return confirmation message
    return jsonify({"message": f"Member id: {member_id}, deleted successfully."}), 200
