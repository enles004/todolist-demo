import typing

from marshmallow import Schema, fields, ValidationError, validates_schema


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


class TaskPayload(Schema):
    title = fields.String(required=False)
    name = fields.String(required=False)

    @validates_schema
    def validate_title(self, data, **kwargs):
        if "title" in data and len(data["title"].split()) > 50:
            raise ValidationError("Title task too long!!, max 50 letters")

    @validates_schema
    def validate_name(self, data, **kwargs):
        if "name" in data and len(data["name"].split()) > 1000:
            raise ValidationError("Name task too long!! max 1000 letters")


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
