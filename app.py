import os

from app import create_app
from app.models import db


def get_config_name():
    config_name = os.getenv("APP_CONFIG")
    if config_name:
        return config_name

    if os.getenv("RAILWAY_ENVIRONMENT_NAME") or os.getenv("RAILWAY_PROJECT_ID"):
        return "ProductionConfig"

    return "DevelopmentConfig"


def should_auto_create_tables():
    return os.getenv("AUTO_CREATE_TABLES", "").lower() in {"1", "true", "yes", "on"}


app = create_app(get_config_name())


if should_auto_create_tables():
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=app.config.get("DEBUG", False),
    )
