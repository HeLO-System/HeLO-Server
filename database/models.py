# database/models.py
from datetime import date
from enum import unique
from math import factorial
from .db import db
from flask_bcrypt import generate_password_hash, check_password_hash

   
class User(db.Document):
    userid = db.StringField(required=True, unique=True)
    pin = db.StringField()
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
    score = db.IntField()
    matches = db.IntField()
    conf = db.StringField()
    
    def init(self):
        if self.matches == None: self.matches = 0
        if self.score   == None: self.score = 500


class Event(db.Document):
    tag = db.StringField(required=True, unique=True)
    name = db.StringField()
    flag = db.StringField()
    invite = db.StringField()
    conf = db.StringField()


class Match(db.Document):
    match_id     = db.StringField(required=True, unique=True)
    clan1_id     = db.StringField()
    clan1        = db.StringField()
    coop1_id     = db.StringField()
    coop1        = db.StringField()
    clan2_id     = db.StringField()
    clan2        = db.StringField()
    coop2_id     = db.StringField()
    coop2        = db.StringField()
    side1        = db.StringField()
    side2        = db.StringField()
    caps1        = db.IntField()
    caps2        = db.IntField()
    players      = db.IntField()
    map          = db.StringField()
    date         = db.DateTimeField()
    duration     = db.IntField()
    factor       = db.DecimalField()
    event        = db.StringField()
    conf1        = db.StringField()
    conf2        = db.StringField()
    score_posted = db.BooleanField()


class Scores(db.Document):
    clan = db.StringField(required=True)
    count = db.IntField(required=True)
    match = db.StringField(required=True)
    score = db.IntField(required=True)
    score_before = db.IntField(required=True)
    
    def new_from_match(match:Match, clan:Clan):
        score = Scores()
        score.match = match.match_id
        score.clan = str(clan.id)
        score.score_before = clan.score
        return score