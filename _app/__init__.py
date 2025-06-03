from datetime import timedelta

from flask import Flask
from dotenv import load_dotenv
from os import getenv as cfg

from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint

load_dotenv()
app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app, prefix='/api')
jwt = JWTManager(app)
jwt._set_error_handler_callbacks(app)

# region JWT auth utils
from _app.global_func import responseapi


@jwt.expired_token_loader
def expired_token_callback(eh=None, ed=None):
    print(eh, ed)
    return responseapi(401, "token_expired", "The token has expired.")


@jwt.invalid_token_loader
def invalid_token_callback(e):
    return responseapi(401, "invalid_token", e)


@jwt.unauthorized_loader
def missing_token_callback(e):
    return responseapi(401, "authorization_required", e)


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return responseapi(401, "fresh_token_required", "The token is not fresh.")


@jwt.revoked_token_loader
def revoke_token_callback():
    return responseapi(401, "token_revoked", "The token has been revoked.")


# endregion JWT auth utils

from _app.seeder import Seeder

Seeder.seed()

# region Swagger
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "TheVault",
        "persistAuthorization": True,
        "servers": [
            {
                "url": "http://localhost:5000",
                "description": "Development server"
            },
            {
                "url": cfg("PROD_DOMAIN"),
                "description": "Production server"
            }
        ]
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
# endregion Swagger

from _app.resources.users import Login, Register, Profile, UpdateProfile, RefreshToken, JobTitle, Employee
from _app.resources.address import Provinsi, KabKota, Kecamatan, Kelurahan, MyAddress

api.add_resource(Login, "/auth/login")
api.add_resource(Register, "/auth/register")
api.add_resource(RefreshToken, "/auth/token-refresh")
api.add_resource(Profile, "/profile")
api.add_resource(UpdateProfile, "/profile/update")

api.add_resource(JobTitle, "/job-title", "/job-title/<iden>")
api.add_resource(Employee, "/employee", "/employee/<iden>")

api.add_resource(Provinsi, "/daerah/provinsi")
api.add_resource(KabKota, "/daerah/kab-kota/<iden>")
api.add_resource(Kecamatan, "/daerah/kecamatan/<iden>")
api.add_resource(Kelurahan, "/daerah/kel-desa/<iden>")

api.add_resource(MyAddress, "/address", "/address/<iden>")


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'
