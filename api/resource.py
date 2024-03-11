from abc import abstractmethod

from prison.decoder import ParserException
import prison
from flask import request, jsonify
from flask.views import View
from marshmallow import ValidationError


# AUTH
class GroupResource(View):

    @abstractmethod
    def _schema(self):
        pass

    @abstractmethod
    def _schema_params(self):
        pass

    def _validate(self):
        data = self._schema().load(request.get_json(silent=True))
        return data

    def _validate_query_params(self):
        data_request = request.args.to_dict()
        data = {}
        for key, value in data_request.items():
            try:
                data[key] = prison.loads(value)
            except ParserException as err:
                raise ValidationError(f"{err}")
        result = self._schema_params().load(data)
        print(result)
        return result

    def dispatch_request(self, **kwargs):
        # validate payload
        payload = None
        # validate path params path_params = kwargs
        path_params = kwargs
        # validate query params
        query_params = None
        if request.method == "POST":
            try:
                payload = self._validate()
            except ValidationError as err:
                return jsonify({"message": f"Invalid input {err}"}), 400

            return self.post(payload=payload, path_params=path_params, query_params=query_params)

        elif request.method == "GET":
            try:
                query_params = self._validate_query_params()
            except ValidationError as err:
                return jsonify({"message": f"invalid input {err}"}), 400
            return self.get(payload=payload, path_params=path_params, query_params=query_params)

    def post(self, payload, path_params, query_params):
        pass

    def get(self, payload, path_params, query_params):
        pass


class ItemResource(View):

    @abstractmethod
    def _schema(self):
        pass

    @abstractmethod
    def _schema_params(self):
        pass

    def _validate(self):
        data = self._schema().load(request.get_json(silent=True))
        return data

    def _validate_query_params(self):
        data = self._schema_params().load(request.args)
        return data

    def dispatch_request(self, **kwargs):
        # validate payload
        payload = None
        # validate path params path_params = kwargs
        path_params = kwargs
        # validate query params
        query_params = None
        if request.method == "GET":
            try:
                query_params = self._validate_query_params()
            except ValidationError as err:
                return jsonify({"Message": f"Invalid input {err}"}), 400
            return self.get(payload=payload, path_params=path_params, query_params=query_params)

        elif request.method == "PUT":
            return self.put(payload=payload, path_params=path_params, query_params=query_params)

        elif request.method == "DELETE":
            return self.delete(payload=payload, path_params=path_params, query_params=query_params)

    def get(self, payload, path_params, query_params):
        pass

    def put(self, payload, path_params, query_params):
        pass

    def delete(self, payload, path_params, query_params):
        pass
