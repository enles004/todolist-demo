from datetime import timedelta, datetime

from flask import jsonify
from flask_bcrypt import Bcrypt
from jwt import encode

from api.resource import GroupResource
from config import secret_key
from db.models import User
from db.session import db_session
from .schemas import LoginPayload, RegisterPayload
from tasks import send_telegram, send_mail_register


class Register(GroupResource):

    def _schema(self):
        return RegisterPayload()

    def _schema_params(self):
        pass

    def post(self, payload, path_params, query_params):
        if db_session.query(User).filter_by(email=payload["email"]).first():
            return jsonify({"Message": "Email is taken"}), 400

        hashed_password = Bcrypt().generate_password_hash(payload["password"]).decode("utf-8")
        hashed_password2 = Bcrypt().generate_password_hash(payload["confirm_password"]).decode("utf-8")
        new_user = User(username=payload["username"],
                        password=hashed_password,
                        confirm_password=hashed_password2,
                        email=payload["email"],
                        role_id=1)
        db_session.add(new_user)
        db_session.commit()
        data = {'email': new_user.email, 'username': new_user.username}
        send_telegram.delay(f"Hello {new_user.email}, welcome to my app. (::")
        send_mail_register.delay(data)
        return jsonify({"email": new_user.email,
                        "username": new_user.username}), 201


class Login(GroupResource):

    def _schema(self):
        return LoginPayload()

    def _schema_params(self):
        pass

    def post(self, payload, path_params, query_params):

        user = db_session.query(User).filter_by(email=payload["email"]).first()
        if not user:
            return jsonify({"Message": "Invalid credentials"}), 401

        is_correct_password = Bcrypt().check_password_hash(user.password, payload["password"])
        if not is_correct_password:
            return jsonify({"Message": "Invalid credentials"}), 401

        expiration = datetime.now() + timedelta(minutes=30)
        token = encode({"user_id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "exp": expiration},
                       secret_key)

        refresh_token = encode({"user_id": user.id,
                                "exp": expiration + timedelta(days=1)},
                               secret_key)

        return jsonify({"Message": "Login successfully",
                        "user": {"token": token,
                                 "refresh_token": refresh_token}}), 200
