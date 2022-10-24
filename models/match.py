"""
first level class
"""
import enum
from email.policy import default
import json
from random import choices

from numpy import require

from database.db import db, CustomQuerySet


class Type(enum.Enum):
    Friendly = "Friendly"
    Competitive = "Competitive"
    Tournament = "Tournament"


class Match(db.Document):
    # something like "StDb-91.-2022-01-07" what ever
    match_id = db.StringField(required=True, unique=True)
    # unique identifiers (very long number) of the clan -> oid of the clan object in DB
    clans1_ids = db.ListField(db.StringField(), required=True)
    clans2_ids = db.ListField(db.StringField(), required=True)
    # player distribution is not required, and should be None if not provided
    player_dist1 = db.ListField(db.IntField())
    player_dist2 = db.ListField(db.IntField())
    # allies or axis
    side1        = db.StringField(choices=('Axis', 'Allies'))
    side2        = db.StringField(choices=('Axis', 'Allies'))
    # strong points hold at the end of the game
    caps1        = db.IntField(required=True, choices=(0, 1, 2, 3, 4, 5))
    caps2        = db.IntField(required=True, choices=(0, 1, 2, 3, 4, 5))
    # number of players on each side (assuming both teams had the same number of players)
    players      = db.IntField()
    map          = db.StringField(required=True)
    strongpoints = db.ListField(db.StringField(), max_length=5)
    date         = db.DateTimeField(required=True)
    # how long the game lasted, max is 90 min
    duration     = db.IntField()
    # competitive factor, see HeLO calculations
    factor       = db.FloatField(default=1.0)
    # name of the tournament, of just a training match
    event        = db.StringField()
    # confirmation, very important
    # match must be confirmed from both sides (representatives) in order to
    # take the match into account
    # user id of the user who confirmed the match for clan1
    conf1        = db.StringField()
    # user id of the user who confirmed the match for clan2
    conf2        = db.StringField()
    # flag to check whether corresponding score objects to the match exist or not
    score_posted = db.BooleanField()
    # reserved for admins, necessary to start a recalculate process for this match
    # will be set only temporarily
    recalculate = db.BooleanField()
    # url to the stream of the match
    stream_url = db.StringField()
    meta = {
        "indexes": [
            {
                "fields": ["$match_id", "$map", "$event"]
            }
        ],
        "queryset_class": CustomQuerySet
    }

    def needs_confirmations(self):
        if (self.conf1 != "" and self.conf1 is not None) and (self.conf2 != "" and self.conf2 is not None):
            # do the calcs then
            return False
        return True

    def to_dict(self):
        return json.loads(self.to_json())

    @property
    def type(self) -> Type or None:
        if self.factor == 0.6:
            return Type.Friendly
        elif self.factor == 2.0:
            return Type.Competetive
        elif self.factor == 2.4:
            return Type.Tournament
        else:
            return None
