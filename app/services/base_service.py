from app.extensions import db


class BaseService:

    @staticmethod
    def commit():

        db.session.commit()

    @staticmethod
    def rollback():

        db.session.rollback()

    @staticmethod
    def save(model):

        db.session.add(model)

        db.session.commit()

        return model