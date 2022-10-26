"""
first level class
"""

import json

from database.db import CustomQuerySet, db
from numpy import require


class ConsoleMatch(db.Document):
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
    players1      = db.IntField() # n1, also sum(player_dist1)
    players2      = db.IntField() # n2, also sum(player_dist2)
    team_size1    = db.IntField() # this is t1 as in the calculations
    team_size2    = db.IntField() # this is t2 as in the calculations
    randoms1      = db.IntField() # this is not t1 as in the calculations, t1 = players1 + randoms1
    randoms2      = db.IntField() # see t1    
    map          = db.StringField(required=True)
    strongpoints = db.ListField(db.StringField(), max_length=5)
    date         = db.DateTimeField(required=True)
    # how long the game lasted, max is 90 min (150min for offensive)
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
    # whether it's offensive or not
    offensive = db.BooleanField()
    # flag to check whether corresponding score objects to the match exist or not
    score_posted = db.BooleanField()
    # reserved for admins, necessary to start a recalculate process for this match
    # will be set only temporarily
    recalculate = db.BooleanField()
    meta = {
        "indexes": [
            {
                "fields": ["$match_id", "$map", "$event"]
            }
        ],
        "queryset_class": CustomQuerySet,
        "db_alias": "console"
    }


    def needs_confirmations(self):
        if (self.conf1 != "" and self.conf1 is not None) and (self.conf2 != "" and self.conf2 is not None):
            # do the calcs then
            return False
        return True


    def to_dict(self):
        return json.loads(self.to_json())


    def get_console_settings(self):
        return {
            "n1": self.players1,
            "n2": self.players2,
            "t1": self.team_size1 if self.team_size1 else self.randoms1 + self.players1,
            "t2": self.team_size2 if self.team_size2 else self.randoms2 + self.players2,
            "offensive": self.offensive
        }
