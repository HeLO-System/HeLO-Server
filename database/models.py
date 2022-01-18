# database/models.py
from datetime import date
from enum import unique
from math import factorial
from .db import db
from flask_bcrypt import generate_password_hash, check_password_hash


class User(db.Document):
    # discord id, very long number
    userid = db.StringField(required=True, unique=True)
    # required for login
    pin = db.StringField()
    name = db.StringField()
    # admin or not
    role = db.StringField()
    clan = db.StringField()
    # TODO: ?
    conf = db.StringField()
 
    def hash_password(self):
        # TODO: ist es nicht theoretisch schlauer das direkt oben zu callen ? sonst gibt es einen (kurzen)
        # Moment wo der/die Pin ungehasht irgendwo liegt, Achtung: gefährliches Halbwissen
        self.pin = generate_password_hash(self.pin).decode('utf8')
 
    def check_password(self, pin):
        return check_password_hash(self.pin, pin)


class Clan(db.Document):
    # e.g. StDb for Stoßtrupp Donnerbalken
    tag = db.StringField(required=True, unique=True)
    # full name
    name = db.StringField()
    # TODO: ?
    flag = db.StringField()
    # TODO: ?
    invite = db.StringField()
    # current HeLO Score
    score = db.IntField()
    # TODO: ?, number of games? = count (siehe unten)
    matches = db.IntField()
    # TODO: ?
    conf = db.StringField()
    
    def init(self):
        if self.matches == None: self.matches = 0
        if self.score   == None: self.score = 500


class Event(db.Document):
    # TODO: ?, maybe the acronym of the event, like HPL = Hell Let Loose Premier League
    tag = db.StringField(required=True, unique=True)
    name = db.StringField()
    # TODO: ?
    flag = db.StringField()
    # TODO: ?
    invite = db.StringField()
    # TODO: ?
    conf = db.StringField()


class Match(db.Document):
    # something like "StDb-91.-2022-01-07"
    # # TODO: id = oid ?
    match_id     = db.StringField(required=True, unique=True)
    # unique identifier (very long number) of the clan
    clan1_id     = db.StringField()
    # name of the clan (clan tag)
    clan1        = db.StringField()
    coop1_id     = db.StringField()
    # if clan1 played with another clan
    coop1        = db.StringField()
    clan2_id     = db.StringField()
    clan2        = db.StringField()
    coop2_id     = db.StringField()
    coop2        = db.StringField()
    # allies or axis
    side1        = db.StringField()
    side2        = db.StringField()
    # strong points hold at the end of the game
    caps1        = db.IntField()
    caps2        = db.IntField()
    # number of players on each side (assuming both teams had the same number of players)
    players      = db.IntField()
    map          = db.StringField()
    date         = db.DateTimeField()
    # how long the game lasted, max is 90 min
    duration     = db.IntField()
    # competitive factor, see HeLO calculations
    factor       = db.DecimalField()
    # name of the tournament, of just a training match
    event        = db.StringField()
    # TODO: ?
    conf1        = db.StringField()
    conf2        = db.StringField()
    # TODO: ?
    score_posted = db.BooleanField()


class Scores(db.Document):
    clan = db.StringField(required=True)
    # number of games
    count = db.IntField(required=True)
    # match id, something like "StDb-91.-2022-01-07"
    match = db.StringField(required=True)
    score = db.IntField(required=True)
    score_before = db.IntField(required=True)
    
    # TODO: ?
    def new_from_match(match:Match, clan:Clan):
        score = Scores()
        score.match = match.match_id
        score.clan = str(clan.id)
        score.score_before = clan.score
        return score
