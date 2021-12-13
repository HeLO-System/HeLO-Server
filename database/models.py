# database/models.py
from datetime import date
from enum import unique
from math import factorial
from .db import db
from flask_bcrypt import generate_password_hash, check_password_hash

   
class User(db.Document):
    userid = db.StringField(required=True, unique=True)
    pin = db.StringField(required=True, min_length=1)
    name = db.StringField()
    role = db.StringField()
    clan = db.StringField()
    conf = db.StringField()
 
    def hash_password(self):
        self.pin = generate_password_hash(self.pin).decode('utf8')
 
    def check_password(self, pin):
        return check_password_hash(self.pin, pin)


class Clan(db.Document):
    tag = db.StringField(required=True, unique=True)
    name = db.StringField()
    flag = db.StringField()
    invite = db.StringField()
    conf = db.StringField()


class Event(db.Document):
    tag = db.StringField(required=True, unique=True)
    name = db.StringField()
    flag = db.StringField()
    invite = db.StringField()
    conf = db.StringField()


class Match(db.Document):
    match_id   = db.StringField(required=True, unique=True)
    clan1_id   = db.StringField()
    clan1      = db.StringField()
    coop1_id   = db.StringField()
    coop1      = db.StringField()
    clan2_id   = db.StringField()
    clan2      = db.StringField()
    coop2_id   = db.StringField()
    coop2      = db.StringField()
    side1      = db.StringField()
    side2      = db.StringField()
    caps1      = db.IntField()
    caps2      = db.IntField()
    map        = db.StringField()
    date       = db.DateTimeField()
    duration   = db.IntField()
    factor     = db.DecimalField()
    event      = db.StringField()
    conf1      = db.StringField()
    conf2      = db.StringField()


class Score(db.Document):
    name = db.StringField(required=True)
    auth = db.StringField(required=True)
    score = db.IntField()
    checksum = db.IntField()
    games = db.IntField()
    history = db.ListField(db.StringField())
    score_history = db.ListField(db.IntField())
    
