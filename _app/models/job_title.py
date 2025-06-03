import uuid
from _app import db


class JobTitleModel(db.Model):
    __tablename__ = "job_title"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    level = db.Column(db.String(255))
    deleted_time = db.Column(db.TIMESTAMP)

    def __init__(self, name, level):
        self.name = name
        self.level = level

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level,
        }

    @classmethod
    def by_id(cls, iden):
        return cls.query.filter(cls.deleted_time.is_(None), cls.id == iden).first()

    @classmethod
    def get_all(cls):
        return cls.query.filter(cls.deleted_time.is_(None)).all()
