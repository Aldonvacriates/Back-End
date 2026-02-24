from flask import Flask
from .extensions import ma
from .models import db
from.blueprints.members import members_bp

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    # initialize extensions
    ma.init_app(app) # adding our ma extension to our app
    db.init_app(app)  # adding our db extension to our app

    # Register blueprints
    app.register_blueprint(members_bp, url_prefix='/members')  # Register the members blueprint with the app


    return app
