import uuid
from datetime import datetime

from os import getenv as cfg
import bcrypt
from sqlalchemy import or_

from _app import db


class UsersModel(db.Model):
    __tablename__ = "users"
    __salt__ = cfg("SALT").encode("UTF-8")

    id = db.Column(db.String(255), primary_key=True, default=lambda: uuid.uuid4().hex)
    full_name = db.Column(db.String(255))
    username = db.Column(db.String(255))
    email = db.Column(db.String(255))
    hashed_password = db.Column(db.String(255))
    auth = db.Column(db.Integer)
    deleted_time = db.Column(db.TIMESTAMP)
    add_time = db.Column(db.TIMESTAMP, default=lambda: datetime.now())

    def __init__(self, full_name, username, email, password, auth=3):
        self.full_name = full_name
        self.username = username
        self.email = email
        self.hashed_password = self.encrypt_password(password)
        self.auth = auth

    def json(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "username": self.username,
            "email": self.email,
            "add_time": self.add_time.strftime("%d-%m-%Y %H:%M") if self.add_time else None,
        }

    @classmethod
    def by_id(cls, iden):
        return cls.query.filter_by(id=iden).first()

    @classmethod
    def encrypt_password(cls, plain):
        return bcrypt.hashpw(plain.encode("UTF-8"), cls.__salt__)

    def decrypt_password(self, plain):
        return bcrypt.checkpw(plain.encode("UTF-8"), self.hashed_password.encode("UTF-8"))

    @classmethod
    def get_user(cls, user):
        return cls.query.filter(cls.deleted_time.is_(None), or_(cls.username == user, cls.email == user)).first()
