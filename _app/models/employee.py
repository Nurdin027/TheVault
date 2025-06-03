import uuid
from datetime import datetime

from _app import db


class EmployeeModel(db.Model):
    __tablename__ = "employee"

    id = db.Column(db.String(255), primary_key=True, default=lambda: uuid.uuid4().hex)
    full_name = db.Column(db.String(255))
    employee_id = db.Column(db.String(255))
    phone_number = db.Column(db.String(255))
    email = db.Column(db.String(255))
    address = db.Column(db.String(255))
    job_title_id = db.Column(db.String(255))
    join_date = db.Column(db.DATE)
    deleted_time = db.Column(db.TIMESTAMP)
    add_time = db.Column(db.TIMESTAMP, default=lambda: datetime.now())

    def __init__(self, full_name, employee_id, phone_number, email, address, job_title_id, join_date):
        self.full_name = full_name
        self.employee_id = employee_id
        self.phone_number = phone_number
        self.email = email
        self.address = address
        self.job_title_id = job_title_id
        self.join_date = join_date

    def json(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "employee_id": self.employee_id,
            "phone_number": self.phone_number,
            "email": self.email,
            "address": self.address,
            "job_title_id": self.job_title_id,
            "join_date": self.join_date.strftime("%d-%m-%Y") if self.join_date else None,
            "add_time": self.add_time.strftime("%d-%m-%Y %H:%M") if self.add_time else None,
        }

    @classmethod
    def get_all(cls):
        return cls.query.filter(cls.deleted_time.is_(None)).order_by(cls.join_date).all()
