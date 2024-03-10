from flask import jsonify


def filtering(query, data_filter_params, model):
    for field in data_filter_params.keys():
        value = data_filter_params[field]
        if isinstance(value, dict):
            if "$contains" in value:
                query = query.filter(getattr(model, field).ilike("%{}%".format(value["$contains"])))
            elif "$equal" in value:
                query = query.filter(getattr(model, field) == value["$equal"])
            else:
                return jsonify({"message": "invalid input"}), 400
        else:
            query = query.filter(getattr(model, field) == value)

    return query


def sorting(query, data_sort_params, model):
    sort_by = data_sort_params["sort_by"]
    order = data_sort_params["order"]
    if order == "asc":
        query = query.order_by(getattr(model, sort_by))
    elif order == "desc":
        query = query.order_by(getattr(model, sort_by).desc())

    return query
