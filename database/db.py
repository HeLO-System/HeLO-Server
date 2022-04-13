# database/db.py
from flask_mongoengine import MongoEngine
from mongoengine.queryset import QuerySet

db = MongoEngine()

def initialize_db(app):
    db.init_app(app)


class CustomQuerySet(QuerySet):

    def to_json_serializable(self):
        return [doc.to_dict() for doc in self]
