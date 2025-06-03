from _app import app, db

app.app_context().push()


class Seeder:
    @classmethod
    def seed(cls):
        from _app.models.auth import AuthModel
        if AuthModel.query.count() == 0:
            try:
                for i in ["Admin", "User"]:
                    auth = AuthModel()
                    auth.name = i
                    db.session.add(auth)
                db.session.commit()
            except Exception as e:
                print(e)
                db.session.rollback()
