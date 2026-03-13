from marshmallow import fields

from app.extensions import ma


class LoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


login_schema = LoginSchema()
