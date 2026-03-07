import os

from app import create_app
from app.models import db


app = create_app("DevelopmentConfig")


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(port=port, use_reloader=False)
