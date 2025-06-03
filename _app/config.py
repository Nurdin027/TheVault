from datetime import timedelta
from os import getenv as cfg

from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URI = cfg('DB_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = cfg('DEBUG') == 'True'
SECRET_KEY = cfg('SECRET_KEY')
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_size": 100,
    "pool_recycle": 300,
}
JWT_SECRET_KEY = cfg('JWT_SECRET_KEY')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(cfg('JWT_ACCESS_TOKEN_EXPIRES') or 3600))
SWAGGER_UI_JSONEDITOR = True
