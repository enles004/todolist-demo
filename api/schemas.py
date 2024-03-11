import typing

from marshmallow import Schema, fields, validate, ValidationError, validates_schema


class ValueField(fields.Field):
    def _deserialize(
        self,
        value: typing.Any,
        attr: str | None,
        data: typing.Mapping[str, typing.Any] | None,
        **kwargs,
    ):
        if isinstance(value, str) or isinstance(value, dict):
            return value
        raise ValidationError({"message": "fields should be str or list"})


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


class ProjectPayload(Schema):
    name = fields.String(required=True)
    id = fields.Integer(required=False)
    completed = fields.Boolean(required=False)


class TaskPayload(Schema):
    title = fields.String(required=True)
    name = fields.String(required=True)

    @validates_schema
    def validate_title(self, data, **kwargs):
        if len(data["title"].split()) > 50:
            raise ValidationError("Title task too long!!, max 50 letters")

    @validates_schema
    def validate_name(self, data, **kwargs):
        if len(data["name"].split()) > 1000:
            raise ValidationError("Name task too long!! max 1000 letters")


class FiltrationProject(Schema):
    name = ValueField(required=False)
    id = fields.Integer(required=False)
    completed = fields.Boolean(required=False)


class FiltrationTask(Schema):
    title = ValueField(required=False)
    name = ValueField(required=False)
    action = fields.Boolean(required=False)
    id = fields.Integer(required=False)
    expiry = fields.DateTime(required=False)
    date_completed = fields.DateTime(required=False, default=None)
    created = fields.DateTime(required=False)


class Pagination(Schema):
    page = fields.Integer(required=False, missing=1)
    per_page = fields.Integer(required=False, missing=10)

    @validates_schema
    def validate_page(self, data, **kwargs):
        if data["page"] <= 0 or data["per_page"] <= 0:
            raise ValidationError({"message": "invalid input, 'page' or 'per_page' must be greater than 0"})


class Sort(Schema):
    sort_by = fields.String(required=False, missing="id")
    order = fields.String(required=False, missing="asc")


class ParamProject(Schema):
    filter = fields.Nested(FiltrationProject(), only=("name", "id", "completed"))
    pagination = fields.Nested(Pagination(), only=("page", "per_page"),
                               missing=Pagination().load({"page": 1, "per_page": 10}))
    sort = fields.Nested(Sort(), only=("sort_by", "order"), missing=Sort().load({"sort_by": "id", "order": "asc"}))

    @validates_schema
    def validate_sort(self, data, **kwargs):
        if data["sort"]["order"] != "asc" and data["sort"]["order"] != "desc":
            raise ValidationError("Can only be 'asc' or 'desc'")


class ParamTask(Schema):
    filter = fields.Nested(FiltrationTask(),
                           only=("title", "name", "id", "date_completed", "action", "created", "expiry"))
    pagination = fields.Nested(Pagination(), only=("page", "per_page"),
                               missing=Pagination().load({"page": 1, "per_page": 10}))
    sort = fields.Nested(Sort(), only=("sort_by", "order"), missing=Sort().load({"sort_by": "id", "order": "asc"}))

    @validates_schema
    def validate_sort(self, data, **kwargs):
        if data["sort"]["order"] != "asc" and data["sort"]["order"] != "desc":
            raise ValidationError("Can only be 'asc' or 'desc'")
