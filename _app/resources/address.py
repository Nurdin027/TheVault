from datetime import datetime

import requests
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource

from _app import db
from _app.global_func import responseapi, global_parser
from _app.models.address import AddressModel


class Provinsi(Resource):
    @classmethod
    def get(cls):
        try:
            url = "https://www.emsifa.com/api-wilayah-indonesia/api/provinces.json"
            res = requests.get(url)
            if res.status_code == 200:
                return responseapi(data=res.json())
            else:
                return responseapi(500, "error", "Fail to get data")
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")


class KabKota(Resource):
    @classmethod
    def get(cls, iden):
        try:
            url = f"https://www.emsifa.com/api-wilayah-indonesia/api/regencies/{iden}.json"
            res = requests.get(url)
            if res.status_code == 200:
                return responseapi(data=res.json())
            elif res.status_code == 404:
                return responseapi(400, "error", "Data not found")
            else:
                return responseapi(500, "error", "Fail to get data")
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")


class Kecamatan(Resource):
    @classmethod
    def get(cls, iden):
        try:
            url = f"https://www.emsifa.com/api-wilayah-indonesia/api/districts/{iden}.json"
            res = requests.get(url)
            if res.status_code == 200:
                return responseapi(data=res.json())
            elif res.status_code == 404:
                return responseapi(400, "error", "Data not found")
            else:
                return responseapi(500, "error", "Fail to get data")
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")


class Kelurahan(Resource):
    @classmethod
    def get(cls, iden):
        try:
            url = f"https://www.emsifa.com/api-wilayah-indonesia/api/villages/{iden}.json"
            res = requests.get(url)
            if res.status_code == 200:
                return responseapi(data=res.json())
            elif res.status_code == 404:
                return responseapi(400, "error", "Data not found")
            else:
                return responseapi(500, "error", "Fail to get data")
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")


class MyAddress(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        try:
            par = global_parser([
                {"name": "provinsi_id", "type": "str", "req": True},
                {"name": "provinsi", "type": "str", "req": True},
                {"name": "kota_id", "type": "str", "req": True},
                {"name": "kota", "type": "str", "req": True},
                {"name": "kecamatan_id", "type": "str", "req": True},
                {"name": "kecamatan", "type": "str", "req": True},
                {"name": "kelurahan_id", "type": "str", "req": True},
                {"name": "kelurahan", "type": "str", "req": True},
                {"name": "full_address", "type": "str", "req": True}
            ])
            address = AddressModel(get_jwt_identity(), par['provinsi_id'], par['provinsi'], par['kota_id'], par['kota'], par['kecamatan_id'],
                                   par['kecamatan'], par['kelurahan_id'], par['kelurahan'], par['full_address'])
            db.session.add(address)
            db.session.commit()
            return responseapi(data=address.json())
        except Exception as e:
            print(e)
            db.session.rollback()
            return responseapi(500, "error", f"Error: {e}")

    @classmethod
    @jwt_required()
    def get(cls):
        try:
            address = AddressModel.my_address(get_jwt_identity())
            return responseapi(data=[x.json() for x in address])
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")

    @classmethod
    @jwt_required()
    def patch(cls, iden):
        try:
            par = global_parser([
                {"name": "provinsi_id", "type": "str"},
                {"name": "provinsi", "type": "str"},
                {"name": "kota_id", "type": "str"},
                {"name": "kota", "type": "str"},
                {"name": "kecamatan_id", "type": "str"},
                {"name": "kecamatan", "type": "str"},
                {"name": "kelurahan_id", "type": "str"},
                {"name": "kelurahan", "type": "str"},
                {"name": "full_address", "type": "str"},
                {"name": "is_main", "type": "int"}
            ])
            address = AddressModel.query.filter_by(id=iden).first()
            if not address or address.user_id != get_jwt_identity():
                return responseapi(404, "error", "Address not found")
            address.provinsi_id = par.get("provinsi_id") or address.provinsi_id
            address.provinsi = par.get("provinsi") or address.provinsi
            address.kota_id = par.get("kota_id") or address.kota_id
            address.kota = par.get("kota") or address.kota
            address.kecamatan_id = par.get("kecamatan_id") or address.kecamatan_id
            address.kecamatan = par.get("kecamatan") or address.kecamatan
            address.kelurahan_id = par.get("kelurahan_id") or address.kelurahan_id
            address.kelurahan = par.get("kelurahan") or address.kelurahan
            address.full_address = par.get("full_address") or address.full_address
            if par.get("is_main"):
                if par.get("is_main") == 1:
                    for x in AddressModel.my_address(get_jwt_identity()):
                        x.is_main = 0
                address.is_main = par.get("is_main")
            db.session.commit()
            return responseapi(data=address.json())
        except Exception as e:
            print(e)
            db.session.rollback()
            return responseapi(500, "error", f"Error: {e}")

    @classmethod
    @jwt_required()
    def delete(cls, iden):
        try:
            address = AddressModel.query.filter_by(id=iden).first()
            if not address or address.user_id != get_jwt_identity():
                return responseapi(404, "error", "Address not found")
            address.deleted_time = datetime.now()
            db.session.commit()
            return responseapi(message="Delete data successfully")
        except Exception as e:
            print(e)
            db.session.rollback()
            return responseapi(500, "error", f"Error: {e}")
