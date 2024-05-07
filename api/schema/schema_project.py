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


class ProjectPayload(Schema):
    name = fields.String(required=False)
    id = fields.Integer(required=False)
    completed = fields.Boolean(required=False)


class FiltrationProject(Schema):
    name = ValueField(required=False)
    id = fields.Integer(required=False)
    completed = fields.Boolean(required=False)


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
