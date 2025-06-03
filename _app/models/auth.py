from _app import db


class AuthModel(db.Model):
    __tablename__ = "auth"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
        }
