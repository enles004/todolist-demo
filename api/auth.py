from datetime import datetime
from datetime import timedelta

from bson.objectid import ObjectId
from flask import jsonify
from flask_bcrypt import Bcrypt
from jwt import encode

from api.resource import GroupResource
from config import secret_key
from db.session import users
from tasks import send_telegram, send_mail_register
from api.schema.schema_auth import LoginPayload, RegisterPayload


class Register(GroupResource):

    async def _schema(self):
        return RegisterPayload()

    async def _schema_params(self):
        pass

    async def post(self, payload, path_params, query_params):
        check_mail = users.find_one({"email": payload["email"]})
        if check_mail is not None:
            return jsonify({"Message": "Email is taken"}), 400

        hashed_password = Bcrypt().generate_password_hash(payload["password"]).decode("utf-8")
        user = {"_id": str(ObjectId()), "username": payload["username"], "email": payload["email"],
                "password": hashed_password,
                "created": datetime.now(), "role": "user"}
        try:
            users.insert_one(user)
        except Exception:
            return jsonify({"Message": "not successfully"})

        data = {'email': user["email"], 'username': user["username"]}
        send_telegram.delay("Hello {}, welcome to my app. (::".format(user["email"]))
        send_mail_register.delay(data)
        return jsonify({"email": user["email"],
                        "username": user["username"]}), 201


class Login(GroupResource):

    async def _schema(self):
        return LoginPayload()

    def _schema_params(self):
        pass

    async def post(self, payload, path_params, query_params):

        user = users.find_one({"email": payload["email"]})
        if not user:
            return jsonify({"Message": "Invalid credentials"}), 401

        is_correct_password = Bcrypt().check_password_hash(user["password"], payload["password"])
        if not is_correct_password:
            return jsonify({"Message": "Invalid credentials"}), 401

        expiration = datetime.now() + timedelta(minutes=30)
        token = encode({"user_id": user["_id"],
                        "email": user["email"],
                        "username": user["username"],
                        "exp": expiration},
                       secret_key)

        refresh_token = encode({"user_id": user["_id"],
                                "exp": expiration + timedelta(days=1)},
                               secret_key)

        return jsonify({"Message": "Login successfully",
                        "user": {"token": token,
                                 "refresh_token": refresh_token}}), 200
