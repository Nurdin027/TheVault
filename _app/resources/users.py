from datetime import timedelta, datetime

from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_restful import Resource

from _app import db
from _app.global_func import global_parser, responseapi
from _app.models.address import AddressModel
from _app.models.employee import EmployeeModel
from _app.models.job_title import JobTitleModel
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
                access_token = create_access_token(identity=user.id, fresh=True)
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


class RefreshToken(Resource):
    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        try:
            access_token = create_access_token(identity=get_jwt_identity(), fresh=True)
            data = {
                "access_token": access_token,
            }
            return responseapi(data=data)
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


# region Jabatan
class JobTitle(Resource):
    @classmethod
    @jwt_required()
    def get(cls):
        try:
            data = JobTitleModel.get_all()
            return responseapi(data=[x.json() for x in data])
        except Exception as e:
            print(e)
            return responseapi(status_code=500, status="error", message=str(e))

    @classmethod
    @jwt_required()
    def post(cls):
        par = global_parser([
            {"name": "name", "type": "str", "req": True},
            {"name": "level", "type": "str"},
        ])
        try:
            jabatan = JobTitleModel(par['name'], par['level'])
            db.session.add(jabatan)
            db.session.commit()
            return responseapi(data=jabatan.json(), message="Insert data successfully")
        except Exception as e:
            print(e)
            db.session.rollback()
            return responseapi(status_code=500, status="error", message=str(e))

    @classmethod
    @jwt_required()
    def patch(cls, iden):
        par = global_parser([
            {"name": "name", "type": "str"},
            {"name": "level", "type": "str"},
        ])
        try:
            jabatan = JobTitleModel.by_id(iden)
            if not jabatan:
                return responseapi(404, "error", "Data not found")
            jabatan.name = par.get("name") or jabatan.name
            jabatan.level = par.get("level") or jabatan.level
            db.session.commit()
            return responseapi(data=jabatan.json(), message="Update data successfully")
        except Exception as e:
            print(e)
            db.session.rollback()
            return responseapi(status_code=500, status="error", message=str(e))

    @classmethod
    @jwt_required()
    def delete(cls, iden):
        try:
            jabatan = JobTitleModel.by_id(iden)
            if not jabatan:
                return responseapi(404, "error", "Data not found")
            jabatan.deleted_time = datetime.now()
            db.session.commit()
            return responseapi(data=jabatan.json(), message="Delete data successfully")
        except Exception as e:
            print(e)
            db.session.rollback()
            return responseapi(status_code=500, status="error", message=str(e))


# endregion Jabatan

# region Employee
class Employee(Resource):
    @classmethod
    @jwt_required()
    def get(cls):
        try:
            data = EmployeeModel.get_all()
            return responseapi(data=[x.json() for x in data])
        except Exception as e:
            print(e)
            return responseapi(status_code=500, status="error", message=str(e))

    @classmethod
    @jwt_required()
    def post(cls):
        par = global_parser([
            {"name": "full_name", "type": "str", "req": True},
            {"name": "employee_id", "type": "str", "req": True},
            {"name": "phone_number", "type": "str", "req": True},
            {"name": "email", "type": "str", "req": True},
            {"name": "address", "type": "str", "req": True},
            {"name": "job_title_id", "type": "str", "req": True},
            {"name": "join_date", "type": "str"},
        ])
        try:
            join_date = datetime.now().date()
            if par.get("join_date"):
                join_date = datetime.strptime(par['join_date'], "%d-%m-%Y")
            employee = EmployeeModel(par['full_name'], par['employee_id'], par['phone_number'],
                                     par['email'], par['address'], par['job_title_id'], join_date)
            db.session.add(employee)
            db.session.commit()
            return responseapi(data=employee.json(), message="Insert data successfully")
        except Exception as e:
            print(e)
            db.session.rollback()
            return responseapi(status_code=500, status="error", message=str(e))

    @classmethod
    @jwt_required()
    def patch(cls, iden):
        par = global_parser([
            {"name": "full_name", "type": "str", "req": True},
            {"name": "employee_id", "type": "str", "req": True},
            {"name": "phone_number", "type": "str", "req": True},
            {"name": "email", "type": "str", "req": True},
            {"name": "address", "type": "str", "req": True},
            {"name": "job_title_id", "type": "str", "req": True},
            {"name": "join_date", "type": "str"},
        ])
        try:
            employee = EmployeeModel.by_id(iden)
            if not employee:
                return responseapi(404, "error", "Data not found")
            employee.name = par.get("name") or employee.name
            employee.level = par.get("level") or employee.level
            employee.full_name = par.get("full_name") or employee.full_name
            employee.employee_id = par.get("employee_id") or employee.employee_id
            employee.phone_number = par.get("phone_number") or employee.phone_number
            employee.email = par.get("email") or employee.email
            employee.address = par.get("address") or employee.address
            employee.job_title_id = par.get("job_title_id") or employee.job_title_id
            if par.get("join_date"):
                employee.join_date = datetime.strptime(par['join_date'], "%d-%m-%Y")
            db.session.commit()
            return responseapi(data=employee.json(), message="Update data successfully")
        except Exception as e:
            print(e)
            db.session.rollback()
            return responseapi(status_code=500, status="error", message=str(e))

    @classmethod
    @jwt_required()
    def delete(cls, iden):
        try:
            employee = EmployeeModel.by_id(iden)
            if not employee:
                return responseapi(404, "error", "Data not found")
            employee.deleted_time = datetime.now()
            db.session.commit()
            return responseapi(data=employee.json(), message="Delete data successfully")
        except Exception as e:
            print(e)
            db.session.rollback()
            return responseapi(status_code=500, status="error", message=str(e))
# endregion Employee
