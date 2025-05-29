import uuid
from datetime import datetime

from _app import db


class AddressModel(db.Model):
    __tablename__ = "address"

    id = db.Column(db.String(255), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = db.Column(db.String(255))
    provinsi_id = db.Column(db.String(255))
    provinsi = db.Column(db.String(255))
    kota_id = db.Column(db.String(255))
    kota = db.Column(db.String(255))
    kecamatan_id = db.Column(db.String(255))
    kecamatan = db.Column(db.String(255))
    kelurahan_id = db.Column(db.String(255))
    kelurahan = db.Column(db.String(255))
    full_address = db.Column(db.String(255))
    is_main = db.Column(db.Integer, default=0)
    deleted_time = db.Column(db.TIMESTAMP)
    add_time = db.Column(db.TIMESTAMP, default=lambda: datetime.now())

    def __init__(self, user_id, provinsi_id, provinsi, kota_id, kota, kecamatan_id, kecamatan, kelurahan_id, kelurahan, full_address, is_main=0):
        self.user_id = user_id
        self.provinsi_id = provinsi_id
        self.provinsi = provinsi
        self.kota_id = kota_id
        self.kota = kota
        self.kecamatan_id = kecamatan_id
        self.kecamatan = kecamatan
        self.kelurahan_id = kelurahan_id
        self.kelurahan = kelurahan
        self.full_address = full_address
        self.is_main = is_main

    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "provinsi_id": self.provinsi_id,
            "provinsi": self.provinsi,
            "kota_id": self.kota_id,
            "kota": self.kota,
            "kecamatan_id": self.kecamatan_id,
            "kecamatan": self.kecamatan,
            "kelurahan_id": self.kelurahan_id,
            "kelurahan": self.kelurahan,
            "full_address": self.full_address,
            "is_main": self.is_main,
            "add_time": self.add_time.strftime("%d-%m-%Y %H:%M") if self.add_time else None,
        }

    @classmethod
    def my_address(cls, user_id):
        return cls.query.filter(cls.deleted_time.is_(None), cls.user_id == user_id).order_by(cls.is_main.desc(), cls.add_time).all()

    @classmethod
    def my_main_address(cls, user_id):
        return cls.query.filter(cls.deleted_time.is_(None), cls.user_id == user_id).order_by(cls.is_main.desc()).first()
