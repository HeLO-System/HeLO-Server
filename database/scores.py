# database/models.py
from ._db import db


class Scores(db.Document):
    name = db.StringField(required=True)
    auth = db.StringField(required=True)
    score = db.IntField()
    checksum = db.IntField()
    games = db.IntField()
    history = db.ListField(db.StringField())
    score_history = db.ListField(db.IntField())
    
