from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_restful import Resource

from _app import db
from _app.global_func import global_parser, responseapi
from _app.models.address import AddressModel
from _app.models.users import UsersModel


class Register(Resource):
    @classmethod
    def post(cls):
        par = global_parser([
            {"name": "full_name", "type": "str", "req": True},
            {"name": "email", "type": "str"},
            {"name": "username", "type": "str", "req": True},
            {"name": "password", "type": "str", "req": True},
        ])
        try:
            exists = UsersModel.get_user(par['email'])
            if exists:
                return responseapi(400, "error", "This email address is already in use.")
            exists = UsersModel.get_user(par['username'])
            if exists:
                return responseapi(400, "error", "This username address is already in use.")
            user = UsersModel(par['full_name'], par['username'], par['email'], par['password'])
            db.session.add(user)
            db.session.commit()
            return responseapi(data=user.json())
        except Exception as e:
            print(e)
            db.session.rollback()
            return responseapi(status_code=500, status="error", message=str(e))


class Login(Resource):
    @classmethod
    def post(cls):
        par = global_parser([
            {"name": "username", "type": "str", "req": True},
            {"name": "password", "type": "str", "req": True},
        ])
        try:
            user = UsersModel.get_user(par['username'])
            if user and user.decrypt_password(par['password']):
                access_token = create_access_token(identity=user.id, fresh=True, expires_delta=False)
                refresh_token = create_refresh_token(user.id)
                data = {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user_detail": user.json()
                }
                return responseapi(data=data)
            return responseapi(401, "error", "Incorrect username or password")
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")


class Profile(Resource):
    @classmethod
    @jwt_required()
    def get(cls):
        try:
            me = UsersModel.by_id(get_jwt_identity())
            address = AddressModel.my_main_address(me.id)
            data = me.json()
            data.update({
                "address": address.json() if address else None
            })
            return responseapi(data=data)
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")


class UpdateProfile(Resource):
    @classmethod
    @jwt_required()
    def patch(cls):
        try:
            par = global_parser([
                {"name": "full_name", "type": "str"},
                {"name": "email", "type": "str"},
                {"name": "username", "type": "str"},
                {"name": "password", "type": "str"},
                {"name": "old_password", "type": "str"},
            ])
            me = UsersModel.by_id(get_jwt_identity())
            if par.get("full_name"):
                me.full_name = par["full_name"]
            if par.get("email"):
                me.email = par["email"]
            if par.get("username"):
                me.username = par["username"]
            if par.get("password"):
                if not par.get("old_password"):
                    return responseapi(400, "error", "old_password required")
                elif me.decrypt_password(par['old_password']):
                    me.hashed_password = UsersModel.encrypt_password(par['password'])
                else:
                    return responseapi(401, "unauthorized", "Incorrect old password")
            db.session.commit()
            return responseapi(data=me.json())
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")
