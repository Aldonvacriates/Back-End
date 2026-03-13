from flask import Flask, jsonify
from flask_limiter.errors import RateLimitExceeded

from .extensions import cache, jwt, limiter, ma
from .models import db
from .blueprints.auth import auth_bp
from .blueprints.frontend import frontend_bp
from .blueprints.members import members_bp
from .blueprints.books import books_bp
from .blueprints.loans import loans_bp


def validate_runtime_config(app, config_name):
    if config_name != "ProductionConfig":
        return

    if app.config["JWT_SECRET_KEY"] == "replace-this-with-a-32-byte-minimum-jwt-secret":
        raise RuntimeError("JWT_SECRET_KEY must be set to a real secret in production.")

    if app.config["SQLALCHEMY_DATABASE_URI"].endswith("@localhost/library_db"):
        raise RuntimeError(
            "Production requires DATABASE_URL or Railway MySQL variables."
        )

    if app.config["RATELIMIT_STORAGE_URI"].startswith("redis://localhost"):
        raise RuntimeError(
            "Production requires REDIS_URL or RATELIMIT_STORAGE_URI for Flask-Limiter."
        )

    if (
        app.config["CACHE_TYPE"] == "RedisCache"
        and app.config["CACHE_REDIS_URL"].startswith("redis://localhost")
    ):
        raise RuntimeError(
            "Production requires REDIS_URL or CACHE_REDIS_URL for Flask-Caching."
        )


def create_app(config_name="DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(f"config.{config_name}")
    app.config["APP_CONFIG_NAME"] = config_name

    validate_runtime_config(app, config_name)

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
    app.register_blueprint(frontend_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(
        members_bp, url_prefix="/members"
    )  # Register the members blueprint with the app
    app.register_blueprint(books_bp, url_prefix="/books")
    app.register_blueprint(loans_bp, url_prefix="/loans")

    return app
