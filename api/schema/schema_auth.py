from marshmallow import Schema, fields, validate, ValidationError, validates_schema


class RegisterPayload(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=20))
    password = fields.String(required=True, validate=validate.Length(min=6, max=20))
    confirm_password = fields.String(required=True)
    email = fields.Email(required=True, validate=validate.Email())

    @validates_schema
    def validate_confirm_password(self, data, **kwargs):
        if data["password"] != data["confirm_password"]:
            raise ValidationError("Incorrect confirm password")


class LoginPayload(Schema):
    email = fields.Email(required=True, validate=validate.Email())
    password = fields.String(required=True)

