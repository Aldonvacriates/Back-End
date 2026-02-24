from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from typing import List

Flask

from marshmallow import ValidationError
from sqlalchemy import select








# Create the table
with app.app_context():
    db.create_all()

app.run(debug=True)
