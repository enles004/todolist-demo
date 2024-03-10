import hashlib
import json
from functools import wraps

from flask import request, jsonify, g
from jwt import ExpiredSignatureError, InvalidTokenError, decode

from db.models import User, Role_Per, Permission
from db.session import db_session
from db.session import r
from config import secret_key


def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        try:
            credential = decode(token, secret_key, algorithms="HS2565")
        except ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        g.user_id = credential["user_id"]
        g.email = credential["email"]
        g.username = credential["username"]
        return func(*args, **kwargs)

    return wrapper


# Check author permissions
def check_permissions(required_permission):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not g.user_id:
                return jsonify({"Message": "The user not logged in"})
            role_user = db_session.query(User).filter_by(id=g.user_id).first()
            user_permission = db_session.query(Role_Per).filter_by(role_id=role_user.role_id).all()
            permission = []
            for user_per in user_permission:
                permission.append((db_session.query(Permission).filter_by(id=user_per.per_id).first()).name)

            if not any(per in permission for per in required_permission):
                return jsonify({"Message": "User does not have permissions"})
            return func(*args, **kwargs)

        return wrapper

    return decorator


def cache(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        status = "on"
        if status == "on":
            cache_key = hashlib.sha256(str(sorted(kwargs["query_params"])).encode("utf-8")).hexdigest()
            cache_result = r.get(cache_key)

            if cache_result is not None:
                print("from key")
                return json.loads(cache_result)
            else:
                result = func(*args, **kwargs)
                response, status_code = result
                if status_code < 400:
                    r.setex(cache_key, 60, json.dumps(response))
            return result

        elif status == "off":
            result = func(*args, **kwargs)
            return result
    return wrapper
