from abc import abstractmethod

from prison.decoder import ParserException
import prison
from flask import request, jsonify
from flask.views import View
from marshmallow import ValidationError


# AUTH
class GroupResource(View):

    @abstractmethod
    async def _schema(self):
        pass

    @abstractmethod
    async def _schema_params(self):
        pass

    async def _validate(self):
        schema = await self._schema()
        data = schema.load(request.get_json(silent=True))
        return data

    async def _validate_query_params(self):
        data_request = request.args.to_dict()
        data = {}
        for key, value in data_request.items():
            try:
                data[key] = prison.loads(value)
            except ParserException as err:
                raise ValidationError(f"{err}")
        schema = await self._schema_params()
        result = schema.load(data)
        return result

    async def dispatch_request(self, **kwargs):
        # validate payload
        payload = None
        # validate path params path_params = kwargs
        path_params = kwargs
        # validate query params
        query_params = None
        if request.method == "POST":
            try:
                payload = await self._validate()
            except ValidationError as err:
                return jsonify({"message": f"Invalid input {err}"}), 400

            return await self.post(payload=payload, path_params=path_params, query_params=query_params)

        elif request.method == "GET":
            try:
                query_params = await self._validate_query_params()
            except (ValidationError, TypeError) as err:
                return jsonify({"message": f"invalid input {err}"}), 400
            return await self.get(payload=payload, path_params=path_params, query_params=query_params)

    async def post(self, payload, path_params, query_params):
        pass

    async def get(self, payload, path_params, query_params):
        pass


class ItemResource(View):

    @abstractmethod
    def _schema(self):
        pass

    @abstractmethod
    def _schema_params(self):
        pass

    async def _validate(self):
        schema = await self._schema()
        data = schema.load(request.get_json(silent=True))
        return data

    async def _validate_query_params(self):
        schema = await self._schema_params()
        data = schema.load(request.args)
        return data

    async def dispatch_request(self, **kwargs):
        # validate payload
        payload = None
        # validate path params path_params = kwargs
        path_params = kwargs
        # validate query params
        query_params = None
        if request.method == "GET":
            try:
                query_params = await self._validate_query_params()
            except ValidationError as err:
                return jsonify({"Message": f"Invalid input {err}"}), 400
            return await self.get(payload=payload, path_params=path_params, query_params=query_params)

        elif request.method == "PUT":
            return await self.put(payload=payload, path_params=path_params, query_params=query_params)

        elif request.method == "DELETE":
            return await self.delete(payload=payload, path_params=path_params, query_params=query_params)

    async def get(self, payload, path_params, query_params):
        pass

    async def put(self, payload, path_params, query_params):
        pass

    async def delete(self, payload, path_params, query_params):
        pass
