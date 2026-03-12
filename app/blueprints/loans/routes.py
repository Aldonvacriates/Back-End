from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select

from app.models import Book, Loan, Member, db

from . import loans_bp
from .schemas import loan_schema, loans_schema


def _get_books_from_ids(book_ids):
    if not book_ids:
        return [], []

    unique_ids = list(dict.fromkeys(book_ids))
    query = select(Book).where(Book.id.in_(unique_ids))
    books = db.session.execute(query).scalars().all()

    books_by_id = {book.id: book for book in books}
    missing_ids = [book_id for book_id in unique_ids if book_id not in books_by_id]
    ordered_books = [books_by_id[book_id] for book_id in unique_ids if book_id in books_by_id]

    return ordered_books, missing_ids


@loans_bp.route("/", methods=["POST"])
def create_loan():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    try:
        loan_data = loan_schema.load(data)
    except ValidationError as e:
        return jsonify(e.messages), 400

    book_ids = loan_data.pop("book_ids", [])

    member = db.session.get(Member, loan_data["member_id"])
    if not member:
        return jsonify({"error": "Member not found."}), 404

    books, missing_ids = _get_books_from_ids(book_ids)
    if missing_ids:
        return jsonify({"error": "Some books were not found.", "missing_book_ids": missing_ids}), 404

    new_loan = Loan(**loan_data)
    new_loan.books = books

    db.session.add(new_loan)
    db.session.commit()

    return jsonify(loan_schema.dump(new_loan)), 201


@loans_bp.route("/", methods=["GET"])
def get_loans():
    query = select(Loan)
    loans = db.session.execute(query).scalars().all()
    return jsonify(loans_schema.dump(loans)), 200


@loans_bp.route("/<int:loan_id>", methods=["GET"])
def get_loan(loan_id):
    loan = db.session.get(Loan, loan_id)

    if not loan:
        return jsonify({"error": "Loan not found."}), 404

    return jsonify(loan_schema.dump(loan)), 200


@loans_bp.route("/<int:loan_id>", methods=["PUT"])
def update_loan(loan_id):
    loan = db.session.get(Loan, loan_id)

    if not loan:
        return jsonify({"error": "Loan not found."}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    try:
        loan_data = loan_schema.load(data, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    if "member_id" in loan_data:
        member = db.session.get(Member, loan_data["member_id"])
        if not member:
            return jsonify({"error": "Member not found."}), 404

    if "book_ids" in loan_data:
        books, missing_ids = _get_books_from_ids(loan_data.pop("book_ids"))
        if missing_ids:
            return (
                jsonify({"error": "Some books were not found.", "missing_book_ids": missing_ids}),
                404,
            )
        loan.books = books

    for key, value in loan_data.items():
        setattr(loan, key, value)

    db.session.commit()
    return jsonify(loan_schema.dump(loan)), 200


@loans_bp.route("/<int:loan_id>", methods=["DELETE"])
def delete_loan(loan_id):
    loan = db.session.get(Loan, loan_id)

    if not loan:
        return jsonify({"error": "Loan not found."}), 404

    db.session.delete(loan)
    db.session.commit()

    return jsonify({"message": f"Loan id: {loan_id}, deleted successfully."}), 200
