from flask import Blueprint

books_bp = Blueprint("books_bp", __name__)

from . import routes  # Import routes so they are registered with the blueprint.
