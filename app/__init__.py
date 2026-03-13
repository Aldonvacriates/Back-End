from flask import Flask, jsonify
from flask_limiter.errors import RateLimitExceeded

from .extensions import cache, jwt, limiter, ma
from .models import db
from .blueprints.auth import auth_bp
from .blueprints.members import members_bp
from .blueprints.books import books_bp
from .blueprints.loans import loans_bp


def create_app(config_name="DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(f"config.{config_name}")

    # initialize extensions
    ma.init_app(app)  # adding our ma extension to our app
    db.init_app(app)  # adding our db extension to our app
    jwt.init_app(app)  # adding our jwt extension to our app
    limiter.init_app(app)  # adding our limiter extension to our app
    cache.init_app(app)  # adding our cache extension to our app

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit(error):
        if error.response is not None:
            return error.response

        return (
            jsonify(
                {
                    "error": "rate_limit_exceeded",
                    "message": "Rate limit exceeded. Please retry later.",
                    "details": {"limit": error.description},
                }
            ),
            429,
        )

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(
        members_bp, url_prefix="/members"
    )  # Register the members blueprint with the app
    app.register_blueprint(books_bp, url_prefix="/books")
    app.register_blueprint(loans_bp, url_prefix="/loans")

    return app
