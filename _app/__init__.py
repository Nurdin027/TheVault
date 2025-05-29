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

# region Config
app.config['SQLALCHEMY_DATABASE_URI'] = cfg('DB_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = cfg('DEBUG') == 'True'
app.config['SECRET_KEY'] = cfg('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = cfg('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = cfg('JWT_ACCESS_TOKEN_EXPIRES')
app.config['SWAGGER_UI_JSONEDITOR'] = True
# endregion

db = SQLAlchemy(app)
migrate = Migrate(app, db)

api = Api(app)
jwt = JWTManager(app)

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

from _app.resources.users import Login, Register, Profile, UpdateProfile
from _app.resources.address import Provinsi, KabKota, Kecamatan, Kelurahan, MyAddress

api.add_resource(Login, "/api/auth/login")
api.add_resource(Register, "/api/auth/register")
api.add_resource(Profile, "/api/profile")
api.add_resource(UpdateProfile, "/api/profile/update")

api.add_resource(Provinsi, "/api/daerah/provinsi")
api.add_resource(KabKota, "/api/daerah/kab-kota/<iden>")
api.add_resource(Kecamatan, "/api/daerah/kecamatan/<iden>")
api.add_resource(Kelurahan, "/api/daerah/kel-desa/<iden>")

api.add_resource(MyAddress, "/api/address", "/api/address/<iden>")


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'
