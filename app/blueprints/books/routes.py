from flask import current_app, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from sqlalchemy import or_, select

from app.extensions import cache, limiter
from app.models import Book, db

from . import books_bp
from .schemas import book_schema, books_schema


def _books_list_cache_key():
    return "books:list"


def _book_detail_cache_key():
    return f"books:detail:{request.view_args['book_id']}"


def _invalidate_book_cache(book_id=None):
    cache.delete(_books_list_cache_key())
    if book_id is not None:
        cache.delete(f"books:detail:{book_id}")


@books_bp.route("/", methods=["POST"])
@jwt_required()
def create_book():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    try:
        book_data = book_schema.load(data)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_book = Book(**book_data)
    db.session.add(new_book)
    db.session.commit()
    _invalidate_book_cache(new_book.id)

    return jsonify(book_schema.dump(new_book)), 201


@books_bp.route("/", methods=["GET"])
@limiter.limit(lambda: current_app.config["HEAVY_READ_RATE_LIMIT"])
@cache.cached(timeout=60, key_prefix=_books_list_cache_key)
def get_books():
    query = select(Book)
    books = db.session.execute(query).scalars().all()
    return jsonify(books_schema.dump(books)), 200


@books_bp.route("/search", methods=["GET"])
@limiter.limit(lambda: current_app.config["SEARCH_RATE_LIMIT"])
def search_books():
    search_term = request.args.get("q", "").strip()
    if not search_term:
        return jsonify({"error": "Query parameter 'q' is required."}), 400

    wildcard = f"%{search_term}%"
    query = (
        select(Book)
        .where(
            or_(
                Book.title.ilike(wildcard),
                Book.author.ilike(wildcard),
                Book.genre.ilike(wildcard),
                Book.desc.ilike(wildcard),
            )
        )
        .limit(50)
    )
    books = db.session.execute(query).scalars().all()

    return jsonify(books_schema.dump(books)), 200


@books_bp.route("/<int:book_id>", methods=["GET"])
@cache.cached(timeout=60, key_prefix=_book_detail_cache_key)
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

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    try:
        book_data = book_schema.load(data, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in book_data.items():
        setattr(book, key, value)

    db.session.commit()
    _invalidate_book_cache(book.id)
    return jsonify(book_schema.dump(book)), 200


@books_bp.route("/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = db.session.get(Book, book_id)

    if not book:
        return jsonify({"error": "Book not found."}), 404

    db.session.delete(book)
    db.session.commit()
    _invalidate_book_cache(book_id)

    return jsonify({"message": f"Book id: {book_id}, deleted successfully."}), 200
