from flask import Blueprint

frontend_bp = Blueprint("frontend_bp", __name__)

from . import routes
