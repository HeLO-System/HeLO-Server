"""
first level class
"""

import json
from datetime import datetime

from database.db import db, CustomQuerySet


class ConsoleClan(db.Document):
    # e.g. StDb for Stoßtrupp Donnerbalken
    tag = db.StringField(required=True, unique=True, max_length=10)
    # full name
    name = db.StringField()
    # discord icon flag, e.g. :flag_eu:, :flag_de:, ...
    flag = db.StringField()
    # discord invite link to a clan's discord server
    invite = db.StringField()
    # current HeLO Score
    score = db.IntField(default=600)
    # number of games
    num_matches = db.IntField(default=0)
    # confirmation, reserved ??
    conf = db.StringField()
    # alternative tags, if a clan was renamed, reserved
    alt_tags = db.ListField(db.StringField())
    # link to the icon of a clan
    icon = db.StringField()
    # when the clan was last updated (e.g. the score)
    last_updated = db.DateTimeField(default=datetime.now())
    # indicates if a clan has played less than 3 matches in 2 months
    inactive = db.BooleanField()
    # indicates if a clan has been inactive for 4 months
    archived = db.BooleanField()
    meta = {
        "indexes": [
            {
                "fields": ["$tag", "$name", "$alt_tags"]
            }
        ],
        "queryset_class": CustomQuerySet,
        "db_alias": "console"
    }


    def to_dict(self):
        return json.loads(self.to_json())
