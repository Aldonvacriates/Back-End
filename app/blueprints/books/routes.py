from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select

from app.models import Book, db

from . import books_bp
from .schemas import book_schema, books_schema


@books_bp.route("/", methods=["POST"])
def create_book():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    try:
        book_data = book_schema.load(data)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_book = Book(**book_data)
    db.session.add(new_book)
    db.session.commit()

    return jsonify(book_schema.dump(new_book)), 201


@books_bp.route("/", methods=["GET"])
def get_books():
    query = select(Book)
    books = db.session.execute(query).scalars().all()
    return jsonify(books_schema.dump(books)), 200


@books_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = db.session.get(Book, book_id)

    if not book:
        return jsonify({"error": "Book not found."}), 404

    return jsonify(book_schema.dump(book)), 200


@books_bp.route("/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = db.session.get(Book, book_id)

    if not book:
        return jsonify({"error": "Book not found."}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    try:
        book_data = book_schema.load(data, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in book_data.items():
        setattr(book, key, value)

    db.session.commit()
    return jsonify(book_schema.dump(book)), 200


@books_bp.route("/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = db.session.get(Book, book_id)

    if not book:
        return jsonify({"error": "Book not found."}), 404

    db.session.delete(book)
    db.session.commit()

    return jsonify({"message": f"Book id: {book_id}, deleted successfully."}), 200
