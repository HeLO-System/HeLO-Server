# database/models.py
from datetime import date
from enum import unique
from math import factorial
from typing import Counter
from .db import db
from flask_bcrypt import generate_password_hash, check_password_hash


"""
firs level class
"""
class Clan(db.Document):
    # e.g. StDb for Stoßtrupp Donnerbalken
    tag = db.StringField(required=True, unique=True)
    # full name
    name = db.StringField()
    # how many games the clan has been played so far
    played_games = db.IntField()
    # discord icon flag, e.g. :flag_eu:, :flag_de:, ...
    flag = db.StringField()
    # discord invite link to a clan's discord server
    invite = db.StringField()
    # current HeLO Score
    score = db.IntField()
    # number of games = count (siehe unten)
    # TODO: rename
    matches = db.IntField()
    # confirmation, reserved ??
    conf = db.StringField()
    
    def init(self):
        if self.matches == None: self.matches = 0
        if self.score   == None: self.score = 500

"""
firs level class
"""
class Event(db.Document):
    # acronym of the event, like HPL = Hell Let Loose Premier League
    tag = db.StringField(required=True, unique=True)
    # corresponding name to the tag
    name = db.StringField()
    # event flag, e.g. :flag_hpl: what ever
    flag = db.StringField()
    # discord invite link to the event's discord server
    invite = db.StringField()
    # confirmation, reserved ??
    conf = db.StringField()


"""
first level class
"""
class Match(db.Document):
    # something like "StDb-91.-2022-01-07" what ever
    match_id     = db.StringField(required=True, unique=True)
    # unique identifier (very long number) of the clan -> oid of the clan object in DB
    clan1_id     = db.StringField()
    # name of the clan (clan tag)
    clan1        = db.StringField()
    # if clan1 played with another clan
    coop1_id     = db.StringField()
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
    # confirmation, very important
    # match must be confirmed from both sides (representatives) in order to
    # take the match into account
    # user id of the user who confirmed the match for clan1
    conf1        = db.StringField()
    # user id of the user who confirmed the match for clan2
    conf2        = db.StringField()
    # deprecated
    score_posted = db.BooleanField()


"""
second level class
"""
class User(db.Document):
    # discord id, very long number
    userid = db.StringField(required=True, unique=True)
    # required for login
    pin = db.StringField()
    name = db.StringField()
    # admin or not
    role = db.StringField()
    clan = db.StringField()
    # confirmation of a user (id), reserved ??
    conf = db.StringField()
 
    def hash_password(self):
        self.pin = generate_password_hash(self.pin).decode('utf8')
 
    def check_password(self, pin):
        return check_password_hash(self.pin, pin)


"""
class to store all scores from all clans, this class should be understood as QoL class,
that make things easier in the long run, but should not be considered as "first level class"
Every new score will be stored in a Score object. The maximum amount of score objects
is the sum of all matches of every clan, e.g. 3 clans with (31, 26, 45) games
--> 31 + 26 + 45 = 102 Score objects
"""
class Scores(db.Document):
    clan = db.StringField(required=True)
    # number of games, count = 31 means it's the score gained from the 31st match
    count = db.IntField(required=True)
    # match id of the match where the score calculation
    # is based on, something like "StDb-91.-2022-01-07"
    match_id = db.StringField(required=True)
    score = db.IntField(required=True)
    # redundant, because with "count" and "clan" we can extract the old score
    # besides when creating the Score object, we don't need to care about
    # double checking whether the score in the corresponding clan object is the same
    # IMPORTANT: clan.score must be updated first!
    # score_before = db.IntField(required=True)

    def __init__(self, clan: str, count: int, match_id: str, score: int):
        super().__init__()
        self.clan = clan
        self.count = count
        self.match_id = match_id
        self.score = score

    @classmethod
    def from_match(cls, match: Match, clan: Clan):
        """Alternative constructor.

        Args:
            match (Match): Match object the calculation is based on
            clan (Clan): Clan that the score belongs to

        Returns:
            Score: the new Score object
        """
        # clan.id is the oid of the Clan object in the DB
        return cls(str(clan.id), clan.played_games, match.match_id, clan.score)
    
    # def new_from_match(match:Match, clan:Clan):
    #     score = Scores()
    #     score.match = match.match_id
    #     score.clan = str(clan.id)
    #     score.score_before = clan.score
    #     return score
