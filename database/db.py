# database/db.py
from flask_mongoengine import MongoEngine
from mongoengine.queryset import QuerySet

db = MongoEngine()

def initialize_db(app):
    db.init_app(app)


class CustomQuerySet(QuerySet):

    def to_json_serializable(self):
        # check if a document in the QuerySet has the method "to_dict"
        # if not return the default document
        return [doc.to_dict() if hasattr(doc, "to_dict") else doc for doc in self]
