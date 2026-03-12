from flask import Flask
from .extensions import ma, limiter
from .models import db
from .blueprints.members import members_bp
from .blueprints.books import books_bp
from .blueprints.loans import loans_bp

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f"config.{config_name}")

    # initialize extensions
    ma.init_app(app)  # adding our ma extension to our app
    db.init_app(app)  # adding our db extension to our app
    limiter.init_app(app) # adding our limiter extension to our app

    # Register blueprints
    app.register_blueprint(
        members_bp, url_prefix="/members"
    )  # Register the members blueprint with the app
    app.register_blueprint(books_bp, url_prefix="/books")
    app.register_blueprint(loans_bp, url_prefix="/loans")

    return app
